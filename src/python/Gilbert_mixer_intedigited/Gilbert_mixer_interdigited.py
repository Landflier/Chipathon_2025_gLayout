#!/usr/bin/env python3

import os
import sys
from typing import Optional
from gdsfactory import Component
from gdsfactory.components import rectangle
from glayout import MappedPDK
from glayout import gf180
from glayout.routing.straight_route import straight_route
from glayout.routing.c_route import c_route
from glayout.routing.L_route import L_route
from glayout import via_stack, via_array
from gdsfactory.grid import grid
from gdsfactory.cell import cell
from gdsfactory.component import Component, copy
from glayout.primitives.via_gen import via_array, via_stack
from glayout.primitives.guardring import tapring
# from pydantic import validate_arguments
from glayout.util.comp_utils import evaluate_bbox, to_float, to_decimal, prec_array, prec_center, prec_ref_center, movey, align_comp_to_port
from glayout.util.port_utils import rename_ports_by_orientation, rename_ports_by_list, add_ports_perimeter, print_ports
from glayout.util.snap_to_grid import component_snap_to_grid
from glayout.spice import Netlist
    
# Add the diff_pair module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../diff_pair'))

def _create_finger_array(
    pdk: MappedPDK,
    width: float,
    fingers: int,
    length: float,
    sdlayer: str,
    sd_route_topmet: str,
    interfinger_rmult: int,
    sd_rmult: int,
    gate_rmult: int
) -> Component:
    """
    Internal function to create a finger array with extra edge gates.
    
    Args:
        pdk: PDK for design rules and layer information
        width: Total width of the transistor
        fingers: Number of fingers
        length: Gate length
        sdlayer: Source/drain doping layer (e.g., "n+s/d")
        sd_route_topmet: Top metal layer for source/drain routing
        interfinger_rmult: Routing multiplier for interfinger connections
        sd_rmult: Source/drain routing multiplier
        gate_rmult: Gate routing multiplier
    
    Returns:
        Component: Finger array with diffusion, doping, and extra edge gates
    """
    # error checking
    if "+s/d" not in sdlayer:
        raise ValueError("specify + doped region for multiplier")

    if sd_rmult<1 or interfinger_rmult<1 or gate_rmult<1:
        raise ValueError("routing multipliers must be positive int")

    # Calculate finger width
    finger_width = width / fingers
    
    # Calculate poly height for transistor finger
    poly_height = finger_width + 2 * pdk.get_grule("poly", "active_diff")["overhang"]
    
    # Snap dimensions to grid
    length = pdk.snap_to_2xgrid(length)
    finger_width = pdk.snap_to_2xgrid(finger_width)
    poly_height = pdk.snap_to_2xgrid(poly_height)
    
    # figure out poly (gate) spacing: s/d metal doesnt overlap transistor, s/d min seperation criteria is met
    sd_viaxdim = interfinger_rmult * evaluate_bbox(via_stack(pdk, "active_diff", "met1"))[0]
    poly_spacing = 2 * pdk.get_grule("poly", "mcon")["min_separation"] + pdk.get_grule("mcon")["width"]
    poly_spacing = max(sd_viaxdim, poly_spacing)
    met1_minsep = pdk.get_grule("met1")["min_separation"]
    poly_spacing += met1_minsep if length < met1_minsep else 0
    
    # create a single finger
    finger = Component("finger")
    gate = finger << rectangle(size=(length, poly_height), layer=pdk.get_glayer("poly"), centered=True)
    sd_viaarr = via_array(pdk, "active_diff", "met1", size=(sd_viaxdim, finger_width), minus1=True, lay_bottom=False).copy()
    interfinger_correction = via_array(pdk, "met1", sd_route_topmet, size=(None, finger_width), lay_every_layer=True, num_vias=(1, None))
    sd_viaarr << interfinger_correction
    sd_viaarr_ref = finger << sd_viaarr
    sd_viaarr_ref.movex((poly_spacing + length) / 2)
    finger.add_ports(gate.get_ports_list(), prefix="gate_")
    finger.add_ports(sd_viaarr_ref.get_ports_list(), prefix="rightsd_")
    
    # create finger array
    fingerarray = prec_array(finger, columns=4*fingers, rows=1, spacing=(poly_spacing + length, 1), absolute_spacing=True)
    sd_via_ref_left = fingerarray << sd_viaarr
    sd_via_ref_left.movex(0 - (poly_spacing + length) / 2)
    fingerarray.add_ports(sd_via_ref_left.get_ports_list(), prefix="leftsd_")
    
    # center finger array and add ports
    centered_farray = Component()
    fingerarray_ref_center = prec_ref_center(fingerarray)
    centered_farray.add(fingerarray_ref_center)
    centered_farray.add_ports(fingerarray_ref_center.get_ports_list())
    
    # add extra gates at far left and far right after centering
    spacing = poly_spacing + length  # same spacing as used in the array
    # Calculate positions relative to outermost finger centers, not bbox edges
    num_fingers = 4 * fingers
    leftmost_finger_center = -(num_fingers - 1) * spacing / 2
    rightmost_finger_center = (num_fingers - 1) * spacing / 2
    left_gate = centered_farray << rectangle(size=(length, poly_height), layer=pdk.get_glayer("poly"), centered=True)
    left_gate.movex(leftmost_finger_center - spacing)
    right_gate = centered_farray << rectangle(size=(length, poly_height), layer=pdk.get_glayer("poly"), centered=True)
    right_gate.movex(rightmost_finger_center + spacing)
    centered_farray.add_ports(left_gate.get_ports_list(), prefix="leftgate_")
    centered_farray.add_ports(right_gate.get_ports_list(), prefix="rightgate_")
    
    # create diffusion and +doped region
    multiplier = rename_ports_by_orientation(centered_farray)
    diff_extra_enc = 2 * pdk.get_grule("mcon", "active_diff")["min_enclosure"]
    diff_dims = (diff_extra_enc + evaluate_bbox(multiplier)[0], finger_width)
    diff = multiplier << rectangle(size=diff_dims, layer=pdk.get_glayer("active_diff"), centered=True)
    sd_diff_ovhg = pdk.get_grule("n+s/d", "active_diff")["min_enclosure"]  # Using n+s/d for NMOS
    sdlayer_dims = [dim + 2 * sd_diff_ovhg for dim in diff_dims]
    sdlayer_ref = multiplier << rectangle(size=sdlayer_dims, layer=pdk.get_glayer("n+s/d"), centered=True)
    multiplier.add_ports(sdlayer_ref.get_ports_list(), prefix="plusdoped_")
    multiplier.add_ports(diff.get_ports_list(), prefix="diff_")

    return multiplier


def add_via_pins_and_labels(
    top_level: Component,
    via_ref: Component,
    pin_name: str,
    pdk: MappedPDK,
    pin_layer: str = "met4",
    debug_mode: str = True,
) -> Component:
    """
    Add pins and labels to a via for external connectivity.
    
    Args:
        top_level: Component to add pins and labels to
        via_ref: Reference to the via component
        pin_name: Name for the pin and label
        pdk: PDK for layer information
        pin_layer: Metal layer for the pin (default: "met4")
        debug_mode: whether to show rectangles where the pin should be
    
    Returns:
        Component: The modified top_level component
    """

    top_level.unlock()
    
    # print(f"DEBUG: {via_ref.ports}")
    # print(f"DEBUG: {via_ref.center}")
    # print(f"DEBUG: {via_ref.size}")
    # Get via center and size
    via_center = via_ref.center
    via_size = via_ref.size
    
    # Use the largest dimension for pin size
    pin_size = max(via_size[0], via_size[1])
    
    # Get the metal layer and convert to pin/label layers using diff_pair function
    metal_layer = pdk.get_glayer(pin_layer)
    
    # Get pin and label layers - dynamic layer from via top metal layer
    pin_layer_gds, label_layer_gds = get_pin_layers(metal_layer, pdk)
    
    # Create visual pin rectangle following diff_pair pattern
    top_level.add_label(text=pin_name, position=via_center, layer=label_layer_gds)
    
    if debug_mode:
        pin_label = rectangle(layer=pin_layer_gds, size=(pin_size, pin_size), centered=True).copy()
        pin_label_ref = top_level << pin_label
        pin_label_ref.move(via_center)
    
    # Add electrical ports for connectivity using the via center
    # Create ports with all four orientations (E=0°, N=90°, W=180°, S=270°)
    top_level.add_port(
        center=via_center,
        width=pin_size,
        orientation=0,  # East orientation
        layer=metal_layer,
        name=f"{pin_name}_E"
    )
    top_level.add_port(
        center=via_center,
        width=pin_size,
        orientation=90,  # North orientation
        layer=metal_layer,
        name=f"{pin_name}_N"
    )
    top_level.add_port(
        center=via_center,
        width=pin_size,
        orientation=180,  # West orientation
        layer=metal_layer,
        name=f"{pin_name}_W"
    )
    top_level.add_port(
        center=via_center,
        width=pin_size,
        orientation=270,  # South orientation
        layer=metal_layer,
        name=f"{pin_name}_S"
    )
    
    return top_level

# Routing the LO drains towards VDD and outside pins
def create_vias_and_route(comp, pin1, pin2, pin3, pin4, pdk_choice, lo_bbox, offset=1.0, route_hlayer="met2", route_vlayer="met3", via_top_layer="met4", via_bottom_layer="met3"):
    """
    Create vias and routing for 4 drain pins in pairs.
    
    Args:
        comp: Component to add vias and routing to
        pin1, pin2: First pair of pins to connect (e.g., left M1, right M1)
        pin3, pin4: Second pair of pins to connect (e.g., left M2, right M2)
        pdk_choice: PDK choice for via creation
        lo_bbox: Width/edge dimension of the LO bbox for positioning calculation
        offset: Offset for the vias (default: 1.0)
        route_hlayer: Layer for horizontal routing (default: "met2")
        route_vlayer: Layer for vertical routing (default: "met3")
        via_top_layer: Top metal layer for vias (default: "met4")
        via_bottom_layer: Bottom metal layer for vias (default: "met3")
    
    Returns:
        Tuple of (via1_ref, via2_ref) - references to the created vias
    """
    # print(f"DEBUG: offset: {offset}")
    # Get pin properties
    pin_width = pin1.width
    pin1_center = pin1.center
    pin2_center = pin2.center
    pin3_center = pin3.center
    pin4_center = pin4.center
    
    # Calculate Y positions (middle of each pair)
    via1_y = (pin1_center[1] + pin2_center[1]) / 2
    via2_y = (pin3_center[1] + pin4_center[1]) / 2
    
    sep_met_vlayer = pdk_choice.get_grule(route_vlayer, route_vlayer)['min_separation']
    # Calculate via X positions: 0.5um right of the right border of each tapring
    via1_x = pin1_center[0] + lo_bbox / 2 + offset  # Right edge of left tapring + 1.0um (default offset)
    via2_x = pin2_center[0] + lo_bbox / 2 + offset + pin_width + sep_met_vlayer  # Right edge of left tapring + 1.0um (default offset)

   # Create vias (square, matching the pin width)
    via1 = via_array(pdk_choice, via_top_layer, via_bottom_layer, 
                     size=(pin_width, pin_width),
                     fullbottom=True)
    via2 = via_array(pdk_choice, via_top_layer, via_bottom_layer, 
                     size=(pin_width, pin_width),
                     fullbottom=True)
    
    # Add vias to component and position them
    via1_ref = comp << via1
    via2_ref = comp << via2
    
    via1_ref.move((via1_x, via1_y))
    via2_ref.move((via2_x, via2_y))
    
    # Create L-routes for each pin to its respective via
    route1 = L_route(
        pdk_choice, 
        pin1,
        via1_ref['top_met_N'],
        hglayer=route_hlayer,
        vglayer=route_vlayer
    )
    route2 = L_route(
        pdk_choice, 
        pin2,
        via1_ref['top_met_N'],
        hglayer=route_hlayer,
        vglayer=route_vlayer
    )
    route3 = L_route(
        pdk_choice, 
        pin3,
        via2_ref['top_met_N'],
        hglayer=route_hlayer,
        vglayer=route_vlayer
    )
    route4 = L_route(
        pdk_choice, 
        pin4,
        via2_ref['top_met_N'],
        hglayer=route_hlayer,
        vglayer=route_vlayer
    )
    
    # Add routes to component
    comp << route1
    comp << route2
    comp << route3
    comp << route4
    
    return via1_ref, via2_ref


def create_labels_and_ports(
    top_level: Component,
    pdk: MappedPDK,
    debug_mode: bool = True
) -> Component:
    """
    Add electrical ports and labels to a top-level design component.
    Similar to add_via_pins_and_labels() but for complete design labeling.
    
    Args:
        top_level: Component to add ports and labels to
        pdk: PDK for layer information and design rules
        debug_mode: If True, add visual pin rectangles for debugging
    
    Returns:
        Component: The modified top_level component with added ports and labels
    """
    # TODO: Implementation needed
    pass


def create_LO_diff_pairs(
    pdk: MappedPDK,
    width: float,
    fingers: int,
    LO_FET_kwargs: dict,
    length: Optional[float] = None,
    tie: Optional[bool] = True,
) -> Component:
    """
    Create interdigitized LO differential pairs for Gilbert cell mixer.
    This is the main function for implementing interdigitized layout.
    
    Args:
        pdk: PDK for design rules and layer information
        length: float of length of the transistors in the LO_diff_pairs
        width: float of width of the transistors in the LO_diff_pairs
        fingers: int of number of fingers in the LO_diff_pairs
        LO_FET_kwargs: Dictionary of additional FET parameters (similar to current __main__ kwargs)
                      Should include parameters like:
                      - with_dnwell
                      - sd_route_topmet, gate_route_topmet
                      - sd_rmult, rmult
                      - gate_rmult
                      - substrate_tap_layers
    
    Returns:
        Component: Single interdigitized component containing both LO differential pairs
    """
    
    if width % fingers != 0:
        raise ValueError(f"Width ({width}) must be a multiple of number of fingers ({fingers})")
    
    # Use PDK minimum length if not specified
    if length is None:
        length = pdk.get_grule('poly')['min_width']

    # Get parameters from LO_FET_kwargs
    sd_rmult = LO_FET_kwargs.get("sd_rmult", 1)
    sd_route_topmet = LO_FET_kwargs.get("sd_route_topmet", "met2")
    sdlayer = LO_FET_kwargs.get("sdlayer", "n+s/d")
    routing = LO_FET_kwargs.get("routing", True)
    inter_finger_topmet = LO_FET_kwargs.get("inter_finger_topmet", "met1")
    gate_route_topmet = LO_FET_kwargs.get("gate_route_topmet", "met2")
    gate_rmult = LO_FET_kwargs.get("gate_rmult", 1)
    interfinger_rmult = LO_FET_kwargs.get("interfinger_rmult", 1)
    sd_route_extension = LO_FET_kwargs.get("sd_route_extension", 0)
    gate_route_extension = LO_FET_kwargs.get("gate_route_extension", 0)
    tie_layers = LO_FET_kwargs.get("tie_layers", ("met2","met1"))

    # error checking
    if "+s/d" not in sdlayer:
        raise ValueError("specify + doped region for multiplier")

    if sd_rmult<1 or interfinger_rmult<1 or gate_rmult<1:
        raise ValueError("routing multipliers must be positive int")


    # Calculate finger width
    finger_width = width / fingers
    
    # Calculate poly height for transistor finger
    poly_height = finger_width + 2 * pdk.get_grule("poly", "active_diff")["overhang"]
    
    # Snap dimensions to grid
    length = pdk.snap_to_2xgrid(length)
    finger_width = pdk.snap_to_2xgrid(finger_width)
    poly_height = pdk.snap_to_2xgrid(poly_height)
    # sizing_ref_viastack = via_stack(pdk, "active_diff", "met1")

    
    # Create finger array using the internal function
    multiplier = _create_finger_array(
        pdk=pdk,
        width=width,
        fingers=fingers,
        length=length,
        sdlayer=sdlayer,
        sd_route_topmet=sd_route_topmet,
        interfinger_rmult=interfinger_rmult,
        sd_rmult=sd_rmult,
        gate_rmult=gate_rmult
    )
    
    
    """Generic poly/sd vias generator
    args:
    pdk = pdk to use
    sdlayer = either p+s/d for pmos or n+s/d for nmos
    width = expands the transistor in the y direction
    length = transitor length (if left None defaults to min length)
    routing = true or false, specfies if sd should be connected
    inter_finger_topmet = top metal of the via array laid on the source/drain regions
    ****NOTE: routing metal is layed over the source drain regions regardless of routing option
    sd_rmult = multiplies thickness of sd metal (int only)
    gate_rmult = multiplies gate by adding rows to the gate via array (int only)
    interfinger_rmult = multiplies thickness of source/drain routes between the gates (int only)
    sd_route_extension = float, how far extra to extend the source/drain connections (default=0)
    gate_route_extension = float, how far extra to extend the gate connection (default=0)
    dummy_routes: bool default=True, if true add add vias and short dummy poly,source,drain

    ports (one port for each edge),
    --- LO2_gate_Lo_b ---
    --- LO2_source    --- * extends to the right 
    --- LO2_drain     --- * extends to the left
    --- finger array  ---
    --- LO_1_drain    --- * extends to the left
    --- LO_1_source   --- * extends to the right
    --- LO_1_gate_Lo  ---

   The connections are, if the transistors from left to right
   in the LO pair are A B C D, and d and s denote source/drain area;
   (dAsBdCsDdDsCdBsA)*4_d

    gate_... all edges (top met route of gate connection)
    source_...all edges (top met route of source connections)
    drain_...all edges (top met route of drain connections)
    plusdoped_...all edges (area of p+s/d or n+s/d layer)
    diff_...all edges (diffusion region)
    rowx_coly_...all ports associated with finger array include gate_... and array_ (array includes all ports of the viastacks in the array)
    leftsd_...all ports associated with the left most via array
    dummy_L,R_N,E,S,W ports if dummy_routes=True
    """

    # argument parsing and rule setup
    min_length = pdk.get_grule("poly")["min_width"]
    length = min_length if (length or min_length) <= min_length else length
    length = pdk.snap_to_2xgrid(length)
    min_width = max(min_length, pdk.get_grule("active_diff")["min_width"])
    width = min_width if (width or min_width) <= min_width else finger_width
    width = pdk.snap_to_2xgrid(width)
    # print(f"DEBUG: width: {width}")

    # get finger array
    multiplier = component_snap_to_grid(rename_ports_by_orientation(multiplier))
    # print(f"DEBUG: multiplier dimensions: {evaluate_bbox(multiplier)}")
    # print(f"DEBUG: multiplier center: {multiplier.center}")

    # route all drains/ gates/ sources
    if routing:
        number_sd_rows = 0
        # print(f"DEBUG: multiplier ports, just before adding sd vias: {multiplier.ports}")
        for port_name in multiplier.ports.keys():
            if port_name.startswith("leftsd_array") and "_col" in port_name:
                # Extract row number from port name like "row0_col1_..."
                row_part = port_name.split("_")[2]
                row_num = int(row_part.replace("row", ""))
                number_sd_rows = max(number_sd_rows, row_num)

        # place vias, then straight route from top port to via-botmet_N
        # print(f"DEBUG: number_sd_rows : {number_sd_rows}")
        sdvia = via_stack(pdk, "met1", sd_route_topmet)
        sdmet_height = sd_rmult*evaluate_bbox(sdvia)[1]
        sdroute_minsep = pdk.get_grule(sd_route_topmet)["min_separation"]
        sdvia_ports = list()
        """
        mosfet circuit:
        s/d denotes source drain
        '-' denotes connected
        d-----d
            d-----d
        A   B C   D
        s---s s---s

        --- LO2_gate_LO_b         ---
        --- LO2_source  (port2)   --- * extends to the right 
        --- LO2_drain   (port4)   --- * extends to the left
        --- finger array          ---
        --- LO_1_drain  (port1)   --- * extends to the left
        --- LO_1_source (port3)   --- * extends to the right
        --- LO_1_gate_LO          ---
        """
        for finger in range(4*fingers+1):
            """ 
            # (dA sB dC sD dD sC dB sA)*4_d
            check_port_1 = (finger % 8 == 1 or finger % 8 == 7) 
            check_port_2 = (finger % 8 == 3 or finger % 8 == 5)
            check_port_3 = (finger % 8 == 0 or finger % 8 == 4)
            check_port_4 = (finger % 8 == 2 or finger % 8 == 6)
            """
            # (dA sB dC sD)*4 _d
            check_port_1 = (finger % 4 == 1 ) 
            check_port_2 = (finger % 4 == 3 )
            check_port_3 = (finger % 4 == 0 )
            check_port_4 = (finger % 4 == 2 )

            # port 3 (drain A/drain C)
            if check_port_3:
                if finger != 0:
                    aligning_port_name = f"row0_col{finger-1}_rightsd_array_row{number_sd_rows}_col0_top_met_N"
                    rel_align_port = multiplier.ports[aligning_port_name]
                # special case for 0-th finger
                else:
                    aligning_port_name = f"leftsd_top_met_N"
                    rel_align_port = multiplier.ports[aligning_port_name]
                    # special case, for when zeroth finger - vertical routing gets multiplied
                    # by interfinger_rmult, since this uses a different port
                    rel_align_port.width = rel_align_port.width / interfinger_rmult 

                y_align_via = -width/2
                alignment_port=('c', 'b')

                #sdvia_extension = sdroute_minsep + (sdmet_height)/2
                sdvia_extension = -(sdroute_minsep + sdroute_minsep + (sdmet_height/2 + sdmet_height))
                sd_route_extension_temp =  -pdk.snap_to_2xgrid(sd_route_extension)

            # port 1 (source B/source A)
            elif check_port_1:
                aligning_port_name = f"row0_col{finger-1}_rightsd_array_row0_col0_top_met_N"
                rel_align_port = multiplier.ports[aligning_port_name]
                y_align_via = -width/2
                alignment_port=('c', 'b')

                sdvia_extension = -(sdroute_minsep + (sdmet_height)/2)
                sd_route_extension_temp = -pdk.snap_to_2xgrid(sd_route_extension)
   
            # port 4 (drain D/drain B)
            elif check_port_4:
                aligning_port_name = f"row0_col{finger-1}_rightsd_array_row{number_sd_rows}_col0_top_met_N"
                rel_align_port = multiplier.ports[aligning_port_name]
                y_align_via = width/2
                alignment_port=('c', 't')

                sdvia_extension = sdroute_minsep + sdroute_minsep + (sdmet_height/2 + sdmet_height)
                sd_route_extension_temp = pdk.snap_to_2xgrid(sd_route_extension)

            # port 2 (source C/source D)
            elif check_port_2:
                aligning_port_name = f"row0_col{finger-1}_rightsd_array_row0_col0_top_met_N"
                rel_align_port = multiplier.ports[aligning_port_name]
                y_align_via = width/2
                alignment_port=('c', 't')

                sdvia_extension = sdroute_minsep + (sdmet_height)/2
                sd_route_extension_temp =  pdk.snap_to_2xgrid(sd_route_extension)

            # diff_top_port = movey(rel_align_port,y_align_viaination=dest)
            # print(f"DEBUG: y_align_via: {y_align_via} ")
            # print(f"DEBUG: sdvia: {sdvia} ")
            # print(f"DEBUG: rel_align_port: {rel_align_port} ")
            # print(f"DEBUG: rel_align_port.layer: {rel_align_port.layer} ")
            # print(f"DEBUG: rel_align_port.width: {rel_align_port.width} ")
            # print(f"DEBUG: (center): {rel_align_port.center[0], y_align_via} ")

            # print(f"DEBUG: ")
            # diff_top_port = movey(rel_align_port,y_align_viaination=dest)

            diff_top_port = multiplier.add_port(
                    center=(rel_align_port.center[0], y_align_via),
                    width=rel_align_port.width,
                    orientation=90,  # North orientation
                    layer=rel_align_port.layer,
                    name=f"diffusion_port_to_align_sd_{finger}"
                    )

            # print(f"DEBUG: diff_top_port: {diff_top_port} ")

            # routing all source-drains of the 4 transistors
            # place sdvia such that metal does not overlap diffusion
            # sdvia_ref = align_comp_to_port(sdvia,diff_top_port,alignment=('c','c'))

            sd_track_y_displacement = sdvia_extension + sd_route_extension_temp
            sdvia_ref = align_comp_to_port(sdvia,diff_top_port,alignment=(alignment_port))
            multiplier.add(sdvia_ref.movey(sd_track_y_displacement))
            multiplier << straight_route(pdk, diff_top_port, sdvia_ref.ports["bottom_met_N"])
            # multiplier << straight_route(pdk, diff_top_port, sdvia_ref.ports["bottom_lay_N"])
            sdvia_ports += [sdvia_ref.ports["top_met_W"], sdvia_ref.ports["top_met_E"]]

            if finger==4*fingers:
                break

            # gates routing 
            """ 
            # (dA sB dC sD dD sC dB sA)*4_d
            check_gate_LO   = (finger % 2 ==0) 
            check_gate_LO_b = (finger % 2 ==1)
            """

            """
            --- LO2_gate_LO_b         ---
            --- LO2_source  (port2)   --- * extends to the right 
            --- LO2_drain   (port4)   --- * extends to the left
            --- finger array          ---
            --- LO_1_drain  (port1)   --- * extends to the left
            --- LO_1_source (port3)   --- * extends to the right
            --- LO_1_gate_LO          ---
            """
            # (dA sB dC sD)*4 _d
            check_gate_LO   = (finger % 2 == 0)
            check_gate_LO_b = (finger % 2 == 1)

            metal_seperation = pdk.util_max_metal_seperation()

            gate_ports = {name: port for name, port in multiplier.ports.items() if "gate" in name}
            # print(f"DEBUG: Gate ports: {gate_ports}")

            # LO_gate, transistors A and D
            if check_gate_LO:
                aligning_gate_port_name = f"row0_col{finger}_gate_S"
                rel_gate_aligning_port = multiplier.ports[aligning_gate_port_name]
                # gate_yshift = 0 - metal_seperation - gate_route_extension 
                gate_extension = -(3 * sdroute_minsep + 5/2 * sdmet_height + sd_route_extension + gate_route_extension)
                y_align_via = - width/2 + gate_extension
            # LO_b_gate, transistors B and C
            elif check_gate_LO_b:
                # aligning_gate_port_name = f"row{number_sd_rows}_col0_gate_N"
                aligning_gate_port_name = f"row0_col{finger}_gate_N"
                rel_gate_aligning_port = multiplier.ports[aligning_gate_port_name]
                gate_extension = 3 * sdroute_minsep + 5/2 * sdmet_height + sd_route_extension + gate_route_extension
                y_align_via = width/2 + gate_extension
            
            # route gates, vertical
            psuedo_Ngateroute = multiplier.add_port(
                    center=(rel_gate_aligning_port.center[0], y_align_via),
                    width=rel_gate_aligning_port.width,
                    orientation=90,  # North orientation
                    layer=rel_gate_aligning_port.layer,
                    name=f"gate_port_vroute_{finger}"
                    )
            psuedo_Ngateroute.y = pdk.snap_to_2xgrid(psuedo_Ngateroute.y)
            multiplier << straight_route(pdk,rel_gate_aligning_port,psuedo_Ngateroute)
        # place route met: gate, horziontal
        # print(f"DEBUG: fingers:: {fingers}")
        # print(f"DEBUG: Gate ports: {gate_ports}")
        gate_width = multiplier.ports[f"gate_port_vroute_{4*fingers-2}"].center[0] - multiplier.ports["gate_port_vroute_0"].center[0] + rel_gate_aligning_port.width
        gate_route = rename_ports_by_list(via_array(pdk,"poly",gate_route_topmet, size=(gate_width,None),num_vias=(None,gate_rmult), no_exception=True, fullbottom=True),[("top_met_","gate_top_")])
        # North gate
        gate_LO_b_ref = align_comp_to_port(gate_route.copy(), multiplier.ports[f"gate_port_vroute_{4*fingers-1}"], alignment=('l','t'),layer=pdk.get_glayer("poly"))
        # South gate
        gate_LO_ref = align_comp_to_port(gate_route.copy(), multiplier.ports[f"gate_port_vroute_{4*fingers-2}"], alignment=('l','b'),layer=pdk.get_glayer("poly"))
        multiplier.add(gate_LO_b_ref)
        multiplier.add(gate_LO_ref)

        # Get unique y-coordinates for each of the ports and get the indeces of the ports on that port/track/s-d line
        y_coords = [port.center[1] for port in sdvia_ports]
        unique_y_coords = list(set(y_coords))
        unique_y_coords.sort()  # Sort for consistent ordering
        
        # Get indices for each unique y-coordinate
        y_coord_indices = [] 
        for unique_y in unique_y_coords:
            first_index = next(i for i, y in enumerate(y_coords) if y == unique_y)
            y_coord_indices.append(first_index)
        
        # print(f"DEBUG: Unique Y coordinates: {unique_y_coords}")
        # print(f"DEBUG: Indices for each Y coordinate: {y_coord_indices}")

        port_1_sd_index = y_coord_indices[1]
        port_2_sd_index = y_coord_indices[2]
        port_3_sd_index = y_coord_indices[0]
        port_4_sd_index = y_coord_indices[3]
        # print(f"DEBUG: sd_via_ports :{sdvia_ports}")
        # place route met: port_1 port_2 port_3 port_4
        sd_width = sdvia_ports[-1].center[0] - sdvia_ports[0].center[0]
        sd_route = rectangle(size=(sd_width,sdmet_height),layer=pdk.get_glayer(sd_route_topmet),centered=True)
        port_1_sd_route = align_comp_to_port(sd_route.copy(), sdvia_ports[port_1_sd_index], alignment=(None,'c'))
        port_2_sd_route = align_comp_to_port(sd_route.copy(), sdvia_ports[port_2_sd_index], alignment=(None,'c'))
        port_3_sd_route = align_comp_to_port(sd_route.copy(), sdvia_ports[port_3_sd_index], alignment=(None,'c'))
        port_4_sd_route = align_comp_to_port(sd_route.copy(), sdvia_ports[port_4_sd_index], alignment=(None,'c'))
        multiplier.add(port_1_sd_route)
        multiplier.add(port_2_sd_route)
        multiplier.add(port_3_sd_route)
        multiplier.add(port_4_sd_route)
        # add ports
        multiplier.add_ports(port_1_sd_route.get_ports_list(), prefix="port_1_")
        multiplier.add_ports(port_2_sd_route.get_ports_list(), prefix="port_2_")
        multiplier.add_ports(port_3_sd_route.get_ports_list(), prefix="port_3_")
        multiplier.add_ports(port_4_sd_route.get_ports_list(), prefix="port_4_")
        # multiplier.add_ports(gate_ref.get_ports_list(prefix="gate_"))
        # multiplier.add_ports(gate_ref.get_ports_list(prefix="gate_"))

    # add tapring

    # add tie if tie
    if tie:
        tap_separation = max(
                pdk.get_grule("met2")["min_separation"],
                pdk.get_grule("met1")["min_separation"],
                pdk.get_grule("active_diff", "active_tap")["min_separation"],
                )

        tap_separation += pdk.get_grule("p+s/d", "active_tap")["min_enclosure"]
        tap_encloses = (
            2 * (tap_separation + multiplier.xmax),
            2 * (tap_separation + multiplier.ymax),
        )
        tiering_ref = multiplier << tapring(
            pdk,
            enclosed_rectangle=tap_encloses,
            sdlayer="p+s/d",
            horizontal_glayer=tie_layers[0],
            vertical_glayer=tie_layers[1],
        )
        multiplier.add_ports(tiering_ref.get_ports_list(), prefix="tie_")
        """
        for row in range(m):
            for dummyside,tieside in [("L","W"),("R","E")]:
                try:
                    multiplier<<straight_route(pdk,multiplier.ports[f"multiplier_{row}_dummy_{dummyside}_gsdcon_top_met_W"],multiplier.ports[f"tie_{tieside}_top_met_{tieside}"],glayer2="met1")
                except KeyError:
                    pass
        """
    # add pwell
    multiplier.add_padding(
        layers=(pdk.get_glayer("pwell"),),
        default=pdk.get_grule("pwell", "active_tap")["min_enclosure"],
    )
    multiplier = add_ports_perimeter(multiplier,layer=pdk.get_glayer("pwell"),prefix="well_")
    
 
    # Create final interdigitized component
    lo_diff_pairs = component_snap_to_grid(rename_ports_by_orientation(multiplier))
    lo_diff_pairs.name = "LO_diff_pairs_interdigitized"
    
    return lo_diff_pairs
    

if __name__ == "__main__":
    
    pdk_choice = gf180

    LO_FET_kwargs = {
        "with_dnwell": False,
        "sd_route_topmet": "met2",
        "gate_route_topmet": "met2",
        "sd_rmult" : 2,
        "gate_rmult": 3,
        "interfinger_rmult": 2,
        "substrate_tap_layers": ("met2","met1"),
        # "routing": True,
        "inter_finger_topmet": "met1",
        # "sdlayer": "n+s/d",
        "sd_route_extension": 0.8,
        "gate_route_extension": 0,
    }

    # Generate differential pair with explicit parameters
    LO_diff_pairs = create_LO_diff_pairs(
        pdk=pdk_choice,
        # length   = 3.0,         # [um], length of channel
        width    = 9.0,           # [um],  width of channel
        fingers  = 3,             # Number of fingers
        LO_FET_kwargs=LO_FET_kwargs
    )


    comp = Component( name = "Gilbert_mixer_interdigitized" )

    LO_diff_pairs_ref = comp << LO_diff_pairs

    # Print available ports for debugging
    # print(f"DEBUG: RF ports: {list(RF_diff_pair_ref.ports.keys())}")
    # print(f"DEBUG: LO_left ports: {list(LO_diff_pair_top_ref.ports.keys())}")
    # print(f"DEBUG: LO_right ports: {list(LO_diff_pair_bot_ref.ports.keys())}")

    # get minimal separtion needed for tapring separations
    sep_met1 = pdk_choice.get_grule('met1', 'met1')['min_separation']
    sep_met2 = pdk_choice.get_grule('met2', 'met2')['min_separation']
    sep_met3 = pdk_choice.get_grule('met3', 'met3')['min_separation']
    # sep_pplus = pdk_choice.get_grule('pplus', 'pplus')['min_separation']

    sep = max(sep_met1, sep_met2)
    
    ## choose ports to route
    lo_1_M2_source_port_name = "LO_diff_pairs_interdigitized_LO1_M2_SOURCE_W"
    lo_2_M1_source_port_name = "LO_diff_pairs_interdigitized_LO1_M1_SOURCE_W"

    ## Get the LO drain port names (using the updated naming scheme)
    lo_top_m1_drain = "LO_diff_pairs_interdigitized_LO1_M1_DRAIN_E"  
    lo_bot_m1_drain = "LO_diff_pairs_interdigitized_LO1_M1_DRAIN_E"
    lo_top_m2_drain = "LO_diff_pairs_interdigitized_LO1_M2_DRAIN_E"  
    lo_bot_m2_drain = "LO_diff_pairs_interdigitized_LO1_M2_DRAIN_E"

    # Write both hierarchical and flattened GDS files
    print("✓ Writing GDS files...")
    comp.write_gds('lvs/gds/Gilbert_cell_interdigitized.gds', cellname="Gilbert_cell_interdigitized")
    print("  - Hierarchical GDS: Gilbert_cell_interdigitized.gds")

    """ 
    print("\n...Running DRC...")
    
    try:
        drc_result = pdk_choice.drc_magic(comp, comp.name)
        print(f"✓ Magic DRC result: {drc_result}")
    except Exception as e:
        print(f"⚠ Magic DRC skipped: {e}")
    """
    print("\n" + "="*60)
    print("TEST COMPLETED - GDS file generated successfully!")
    print("="*60)
    
    
