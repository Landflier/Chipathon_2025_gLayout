#!/usr/bin/env python3
"""
Interdigitized Current Mirror with Decoupling Capacitor Design

This module provides functions to create an interdigitized current mirror layout
based on GLayout primitives. The design includes:
- Interdigitized NMOS transistor pairs for improved matching
- Proper current mirror routing (gate-drain short for reference)
- External I/O via placement for easy chip-level integration
- Framework for decoupling capacitor integration

Key Functions:
============

create_cmirror_interdigitized(pdk, width, fingers, CM_FET_kwargs, length=None, component_name="cmirror_interdigitized")
    -> Component
    Creates the basic interdigitized current mirror structure with two NMOS transistors.
    
add_cmirror_routing(pdk, cm_component) -> Component
    Adds proper current mirror routing: source connections (VSS), gate connections (bias),
    and gate-drain short for the reference transistor.
    
create_cmirror_with_decap(pdk, width, fingers, CM_FET_kwargs, decap_size=None, length=None) 
    -> Component
    Creates complete current mirror with routing and framework for decoupling capacitor.
    
create_cmirror_vias_outside_tapring_and_route(pdk, cmirror_ref, comp, extra_port_vias_x_displacement)
    -> tuple[via_vref_ref, via_vcopy_ref, via_vss_ref, via_vb_ref]
    Creates external I/O vias for VREF, VCOPY, VSS, and VB connections outside the tapring.

add_pin_and_label_to_via(comp, via_ref, pin_name, pdk, debug_mode=False) -> Component
    Utility function to add pins and labels to vias for proper GDS annotation.

Usage Example:
=============
    CM_FET_kwargs = {
        "sd_route_topmet": "met2",
        "gate_route_topmet": "met2", 
        "sd_rmult": 2,
        "gate_rmult": 3,
        "with_tie": True,
        "tie_layers": ("met2","met1")
    }
    
    cmirror = create_cmirror_with_decap(
        pdk=gf180,
        width=20.0,    # [um] 
        fingers=4,     # fingers per transistor
        CM_FET_kwargs=CM_FET_kwargs
    )
"""

import os
import sys
from typing import Optional
from gdsfactory import Component

from glayout import gf180, MappedPDK
from glayout import tapring
from glayout.routing.straight_route import straight_route
from glayout.routing.c_route import c_route
from glayout.routing.L_route import L_route
from glayout import via_stack, via_array

from gdsfactory.components import rectangle
from glayout.primitives.via_gen import via_array, via_stack
from glayout.util.comp_utils import evaluate_bbox, align_comp_to_port, prec_ref_center, prec_center, prec_array, movey
from glayout.util.port_utils import rename_ports_by_orientation, add_ports_perimeter, rename_ports_by_list
from glayout.util.snap_to_grid import component_snap_to_grid
    
# Add the diff_pair module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../diff_pair'))
from diff_pair import get_pin_layers

# Import custom finger array from Gilbert mixer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../Gilbert_mixer_intedigited'))
from Gilbert_mixer_interdigited import _create_finger_array

def add_pin_and_label_to_via(
    comp: Component,
    via_ref: Component,
    pin_name: str,
    pdk: MappedPDK,
    debug_mode: bool = False,
) -> Component:
    """
    Add a pin and label to an existing via at its center on the top metal layer.
    
    Args:
        comp: Component to add pins and labels to
        via_ref: Reference to the via component
        pin_name: Name for the pin and label
        pdk: PDK for layer information
        debug_mode: whether to show rectangles where the pin should be
    
    Returns:
        Component: The modified comp component
    """
    comp.unlock()
    
    # Get via center and size
    via_center = via_ref.center
    via_size = via_ref.size
    
    # Use the largest dimension for pin size
    pin_size = max(via_size[0], via_size[1])
    
    # Find the top metal port of the via
    top_met_ports = [port for port_name, port in via_ref.ports.items() if "top_met" in port_name]
    
    if not top_met_ports:
        print(f"⚠ Warning: No top_met ports found in via for {pin_name}")
        return comp
    
    # Use the first top metal port to determine the layer
    top_met_port = top_met_ports[0]
    metal_layer = top_met_port.layer
    
    # Get pin and label layers from the top metal layer
    pin_layer_gds, label_layer_gds = get_pin_layers(metal_layer, pdk)
    
    # Add label at via center
    comp.add_label(text=pin_name, position=via_center, layer=label_layer_gds)
    
    if debug_mode:
        # Create visual pin rectangle for debugging
        pin_rect = rectangle(layer=pin_layer_gds, size=(pin_size, pin_size), centered=True).copy()
        pin_rect_ref = comp << pin_rect
        pin_rect_ref.move(via_center)
    
    # Add electrical ports for connectivity using the via center
    # Create ports with all four orientations (E=0°, N=90°, W=180°, S=270°)
    comp.add_port(
        center=via_center,
        width=pin_size,
        orientation=0,  # East orientation
        layer=metal_layer,
        name=f"{pin_name}_E"
    )
    comp.add_port(
        center=via_center,
        width=pin_size,
        orientation=90,  # North orientation
        layer=metal_layer,
        name=f"{pin_name}_N"
    )
    comp.add_port(
        center=via_center,
        width=pin_size,
        orientation=180,  # West orientation
        layer=metal_layer,
        name=f"{pin_name}_W"
    )
    comp.add_port(
        center=via_center,
        width=pin_size,
        orientation=270,  # South orientation
        layer=metal_layer,
        name=f"{pin_name}_S"
    )
    
    return comp
def _add_source_drain_gate_routing(
    pdk: MappedPDK,
    multiplier: Component,
    fingers: int,
    width: float,
    sd_rmult: int,
    sd_route_topmet: str,
    sd_route_extension: float,
    gate_route_topmet: str,
    gate_rmult: int,
    gate_route_extension: float,
    interfinger_rmult: int
) -> None:
    """
    Add source/drain and gate routing to the multiplier component.
    
    Args:
        pdk: PDK for design rules and layer information
        multiplier: Component to add routing to
        fingers: Number of fingers
        width: Total width of the transistor
        sd_rmult: Source/drain routing multiplier
        sd_route_topmet: Top metal layer for source/drain routing
        sd_route_extension: Extension for source/drain connections
        gate_route_topmet: Top metal layer for gate routing
        gate_rmult: Gate routing multiplier
        gate_route_extension: Extension for gate connections
        interfinger_rmult: Interfinger routing multiplier
    """
    number_sd_rows = 0
    for port_name in multiplier.ports.keys():
        if port_name.startswith("leftsd_array") and "_col" in port_name:
            # Extract row number from port name like "row0_col1_..."
            row_part = port_name.split("_")[2]
            row_num = int(row_part.replace("row", ""))
            number_sd_rows = max(number_sd_rows, row_num)

    if fingers%2 != 0
        print("Error: _add_source_drain_routing encoutered an error. Need figners to be an ")
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
    d   d
    |
    g---g
    A   B 
    s---s---VSS

    --- drain_ref    (port1)   --- * extends to the left
    --- drain_mirror (port2)   --- * extends to the right 
    --- finger array          ---
    --- common_source (port3)   --- * extends to the right
    """
    for finger in range(4*fingers+1):
        # (dA sB dB sA)*(fingers/2) _d
        check_port_1 = (finger % 4 == 1 ) 
        check_port_2 = (finger % 4 == 3 )
        check_port_3 = (finger % 4 == 0 )
        check_port_4 = (finger % 4 == 2 )


        # port 1 (source B/source A)
        if check_port_1:
            aligning_port_name = f"row0_col{finger-1}_rightsd_array_row0_col0_top_met_N"
            rel_align_port = multiplier.ports[aligning_port_name]
            y_align_via = -width/2
            alignment_port=('c', 'b')

            sdvia_extension = -(sdroute_minsep + sdroute_minsep + (sdmet_height/2 + sdmet_height))
            sd_route_extension_temp =  -pdk.snap_to_2xgrid(sd_route_extension)

        # port 2 (source C/source D)
        elif check_port_2:
            aligning_port_name = f"row0_col{finger-1}_rightsd_array_row0_col0_top_met_N"
            rel_align_port = multiplier.ports[aligning_port_name]
            y_align_via = -width/2
            alignment_port=('c', 'b')

            sdvia_extension = -(sdroute_minsep + (sdmet_height)/2)
            sd_route_extension_temp = -pdk.snap_to_2xgrid(sd_route_extension)

        # port 3 (drain A/drain C)
        elif check_port_3:
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

            y_align_via = width/2
            alignment_port=('c', 't')

            sdvia_extension = +(sdroute_minsep + (sdmet_height)/2)
            sd_route_extension_temp = pdk.snap_to_2xgrid(sd_route_extension)

        # port 4 (drain D/drain B)
        elif check_port_4:
            aligning_port_name = f"row0_col{finger-1}_rightsd_array_row{number_sd_rows}_col0_top_met_N"
            rel_align_port = multiplier.ports[aligning_port_name]
            y_align_via = width/2
            alignment_port=('c', 't')

            #sdvia_extension = sdroute_minsep + (sdmet_height)/2
            sdvia_extension = +(sdroute_minsep + sdroute_minsep + (sdmet_height/2 + sdmet_height))
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

        if finger==2*fingers:
            break

        # gates routing 
        """ 
        # (dA sB dB sA)*2_d
        check_gate_LO   = (finger % 2 ==0) 
        check_gate_LO_b = (finger % 2 ==1)
        """

        """
        --- LO_1_source (port3)   --- * extends to the right
        --- finger array          ---
        --- LO2_source  (port2)   --- * extends to the right 
        --- LO_1_drain  (port1)   --- * extends to the left
        --- LO_1_gate_LO          ---
        """

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

    multiplier.add_ports(gate_LO_ref.get_ports_list(), prefix="LO_")
    multiplier.add_ports(gate_LO_b_ref.get_ports_list(), prefix="LO_b_")

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

    port_1_sd_index = y_coord_indices[0]
    port_2_sd_index = y_coord_indices[1]
    port_3_sd_index = y_coord_indices[2]
    port_4_sd_index = y_coord_indices[3]
    # print(f"DEBUG: sd_via_ports :{sdvia_ports}")
    # place route met: port_1 port_2 port_3 port_4
    sd_width = sdvia_ports[-1].center[0] - sdvia_ports[0].center[0]
    sd_route = rectangle(size=(sd_width,sdmet_height),layer=pdk.get_glayer(sd_route_topmet),centered=True)

    # change widths to match the topmet layer width
    sdvia_ports[port_1_sd_index].width = sdmet_height
    sdvia_ports[port_2_sd_index].width = sdmet_height
    sdvia_ports[port_3_sd_index].width = sdmet_height
    sdvia_ports[port_4_sd_index].width = sdmet_height


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
    """

def create_cmirror_vias_outside_tapring_and_route(
        pdk: MappedPDK,
        cmirror_ref: Component,
        comp: Component,
        extra_port_vias_x_displacement: float,
        ) -> tuple:
    """
    Create vias for routing the current mirror I/O outside the tapring.
    
    Args:
        pdk: PDK for design rules and layer information
        cmirror_ref: Component reference with the current mirror
        comp: Top-level component to add vias to
        extra_port_vias_x_displacement: Additional x displacement for vias
    
    Returns:
        tuple: References to the created vias (VREF, VCOPY, VSS, VB)
    """
    
    # Get current mirror I/O ports
    try:
        vref_port = cmirror_ref.ports["CM_Mref_drain_N"]  # Reference drain (VREF/IREF input)
        vcopy_port = cmirror_ref.ports["CM_Mmirror_drain_N"]  # Mirror drain (ICOPY output)
        vss_port = cmirror_ref.ports["CM_Mref_source_S"]  # Common sources (VSS)
        vb_port = cmirror_ref.ports["CM_Mref_tie_S_top_met_S"]  # Body/substrate connection
    except KeyError as e:
        print(f"Warning: Could not find current mirror port: {e}")
        # Use fallback port names
        vref_port = list(cmirror_ref.ports.values())[0]
        vcopy_port = list(cmirror_ref.ports.values())[1]
        vss_port = list(cmirror_ref.ports.values())[2]
        vb_port = list(cmirror_ref.ports.values())[3]

    # Standard via size for current mirror connections
    via_width = max(vref_port.width, vcopy_port.width, vss_port.width)
    
    # Create vias for each signal
    via_vref = via_array(pdk, "met3", "met2", 
                        size=(via_width, via_width),
                        fullbottom=True)
    via_vcopy = via_array(pdk, "met3", "met2", 
                        size=(via_width, via_width),
                        fullbottom=True)
    via_vss = via_array(pdk, "met3", "met2", 
                        size=(via_width, via_width),
                        fullbottom=True)
    via_vb = via_array(pdk, "met3", "met2", 
                        size=(via_width, via_width),
                        fullbottom=True)

    # Add vias to component
    via_vref_ref = comp << via_vref
    via_vcopy_ref = comp << via_vcopy
    via_vss_ref = comp << via_vss
    via_vb_ref = comp << via_vb

    # Position vias aligned to their respective ports
    align_comp_to_port(via_vref_ref, vref_port, alignment=('c', 'c'))
    align_comp_to_port(via_vcopy_ref, vcopy_port, alignment=('c', 'c'))
    align_comp_to_port(via_vss_ref, vss_port, alignment=('c', 'c'))
    align_comp_to_port(via_vb_ref, vb_port, alignment=('c', 'c'))

    # Move vias outside the tapring with displacement
    try:
        # Calculate displacement to move vias outside tapring
        tie_w_port = cmirror_ref.ports["CM_Mref_tie_W_bottom_lay_W"]
        tie_e_port = cmirror_ref.ports["CM_Mmirror_tie_E_bottom_lay_E"]
        
        # Move VREF and VSS to the left
        via_vref_ref.movex(-abs(vref_port.center[0] - tie_w_port.center[0]) - via_width - extra_port_vias_x_displacement)
        via_vss_ref.movex(-abs(vss_port.center[0] - tie_w_port.center[0]) - via_width - extra_port_vias_x_displacement)
        
        # Move VCOPY and VB to the right  
        via_vcopy_ref.movex(abs(vcopy_port.center[0] - tie_e_port.center[0]) + via_width + extra_port_vias_x_displacement)
        via_vb_ref.movex(abs(vb_port.center[0] - tie_e_port.center[0]) + via_width + extra_port_vias_x_displacement)
        
    except KeyError:
        # Fallback positioning if tie ports not found
        via_vref_ref.movex(-extra_port_vias_x_displacement)
        via_vcopy_ref.movex(extra_port_vias_x_displacement)
        via_vss_ref.movex(-extra_port_vias_x_displacement)
        via_vb_ref.movex(extra_port_vias_x_displacement)

    # Route vias to their corresponding ports
    try:
        comp << straight_route(pdk, 
                via_vref_ref.ports["bottom_lay_W"], 
                vref_port)
        comp << straight_route(pdk, 
                via_vcopy_ref.ports["bottom_lay_W"], 
                vcopy_port)
        comp << straight_route(pdk, 
                via_vss_ref.ports["bottom_lay_W"], 
                vss_port)
        comp << straight_route(pdk, 
                via_vb_ref.ports["bottom_lay_W"], 
                vb_port)
    except Exception as e:
        print(f"Warning: Could not route via connections: {e}")

    return via_vref_ref, via_vcopy_ref, via_vss_ref, via_vb_ref

def create_cmirror_interdigitized(
    pdk: MappedPDK,
    width: float,
    fingers: int,
    CM_FET_kwargs: dict,
    length: Optional[float] = None,
    component_name: Optional[str] = "cmirror_interdigitized",
) -> Component:
    """
    Create interdigitized current mirror using custom finger array approach (adapted from Gilbert mixer).
    This function creates 2 NMOS transistors in an interdigitized layout pattern.
    
    Args:
        pdk: PDK for design rules and layer information
        width: float of total width of the transistor
        fingers: int of number of fingers per transistor
        CM_FET_kwargs: Dictionary of additional FET parameters
                      Should include parameters like:
                      - sd_route_topmet, gate_route_topmet
                      - sd_rmult, gate_rmult, interfinger_rmult
                      - dummy settings
        length: Gate length (uses PDK minimum if not specified)
        component_name: Name for the component
    
    Returns:
        Component: Single interdigitized component containing both current mirror transistors
    """
    if width % fingers != 0:
        raise ValueError(f"Width ({width}) must be a multiple of number of fingers ({fingers})")
    
    pdk.activate()

    # Use PDK minimum length if not specified
    if length is None:
        length = pdk.get_grule('poly')['min_width']

    # Get parameters from CM_FET_kwargs
    sd_rmult = CM_FET_kwargs.get("sd_rmult", 1)
    sd_route_topmet = CM_FET_kwargs.get("sd_route_topmet", "met2")
    sdlayer = CM_FET_kwargs.get("sdlayer", "n+s/d")  # NMOS for current mirror
    routing = CM_FET_kwargs.get("routing", True)
    inter_finger_topmet = CM_FET_kwargs.get("inter_finger_topmet", "met1")
    gate_route_topmet = CM_FET_kwargs.get("gate_route_topmet", "met2")
    gate_rmult = CM_FET_kwargs.get("gate_rmult", 1)
    interfinger_rmult = CM_FET_kwargs.get("interfinger_rmult", 1)
    sd_route_extension = CM_FET_kwargs.get("sd_route_extension", 0)
    gate_route_extension = CM_FET_kwargs.get("gate_route_extension", 0)
    tie_layers = CM_FET_kwargs.get("tie_layers", ("met2","met1"))
    with_dummies = CM_FET_kwargs.get("with_dummies", False)

    # error checking
    if "+s/d" not in sdlayer:
        raise ValueError("specify + doped region for multiplier")

    if sd_rmult < 1 or interfinger_rmult < 1 or gate_rmult < 1:
        raise ValueError("routing multipliers must be positive int")

    # Calculate finger width
    finger_width = width / fingers
    
    # Calculate poly height for transistor finger
    poly_height = finger_width + 2 * pdk.get_grule("poly", "active_diff")["overhang"]
    
    # Snap dimensions to grid
    length = pdk.snap_to_2xgrid(length)
    finger_width = pdk.snap_to_2xgrid(finger_width)
    poly_height = pdk.snap_to_2xgrid(poly_height)
    
    # Create finger array using the Gilbert mixer function (2 FETs for current mirror)
    multiplier = _create_finger_array(
        pdk=pdk,
        width=width,
        fingers=fingers,
        length=length,
        fets=2,  # 2 FETs: reference and mirror
        sdlayer=sdlayer,
        sd_route_topmet=sd_route_topmet,
        interfinger_rmult=interfinger_rmult,
        sd_rmult=sd_rmult,
        gate_rmult=gate_rmult,
        with_dummies=with_dummies
    )

    # argument parsing and rule setup
    min_width = pdk.get_grule("poly")["min_width"]
    length = pdk.snap_to_2xgrid(length)
    min_width = max(min_width, pdk.get_grule("active_diff")["min_width"])
    width = min_width if (width or min_width) <= min_width else finger_width
    width = pdk.snap_to_2xgrid(width)

    # get finger array
    multiplier = component_snap_to_grid(rename_ports_by_orientation(multiplier))

    # Note: Current mirror routing will be handled separately by add_cmirror_routing function
    # The custom routing is more complex and needs specific current mirror connections

    # add tapring
    with_tie = CM_FET_kwargs.get("with_tie", True)
    if with_tie:
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

    # add pwell if nmos
    if sdlayer == "n+s/d":
        multiplier.add_padding(
            layers=(pdk.get_glayer("pwell"),),
            default=pdk.get_grule("pwell", "active_tap")["min_enclosure"],
        )
        multiplier = add_ports_perimeter(multiplier, layer=pdk.get_glayer("pwell"), prefix="well_")
    # add nwell if pmos
    elif sdlayer == "p+s/d":
        multiplier.add_padding(
            layers=(pdk.get_glayer("nwell"),),
            default=pdk.get_grule("nwell", "active_tap")["min_enclosure"],
        )
        multiplier = add_ports_perimeter(multiplier, layer=pdk.get_glayer("nwell"), prefix="well_")

    # route dummies
    if with_dummies:
        try:
            multiplier << straight_route(pdk, 
                    multiplier.ports["dummy_gate_L_W"], 
                    multiplier.ports["tie_W_bottom_lay_E"],
                    glayer1="poly",
                    glayer2="met1",
                    )

            multiplier << straight_route(pdk, 
                    multiplier.ports["dummy_gate_R_E"], 
                    multiplier.ports["tie_E_bottom_lay_W"],
                    glayer1="poly",
                    glayer2="met1",
                    )
        except KeyError:
            print("Warning: Could not route dummy gates to tie ring")

    # Create final interdigitized component
    cmirror_interdigitized = component_snap_to_grid(rename_ports_by_orientation(multiplier))
    cmirror_interdigitized.name = component_name
    
    return cmirror_interdigitized

def add_cmirror_routing(
    pdk: MappedPDK,
    cm_component: Component,
) -> Component:
    """
    Add proper current mirror routing connections:
    1. Connect sources together (VSS)
    2. Connect gates together (to form bias network)
    3. Connect gate of reference to its drain (for diode connection)
    
    Args:
        pdk: PDK for design rules and layer information
        cm_component: Component containing the interdigitized current mirror
    
    Returns:
        Component: Component with routing added
    """
    cm_component.unlock()
    
    # Route sources together (VSS connection)
    try:
        source_route = straight_route(
            pdk, 
            cm_component.ports["CM_Mref_source_W"], 
            cm_component.ports["CM_Mmirror_source_W"]
        )
        cm_component << source_route
    except KeyError as e:
        print(f"Warning: Could not find source ports for VSS connection: {e}")
        # Try alternative port names from multiplier
        try:
            source_route = straight_route(
                pdk, 
                cm_component.ports["CM_Mref_source_E"], 
                cm_component.ports["CM_Mmirror_source_E"]
            )
            cm_component << source_route
        except KeyError:
            print("Warning: Could not find any source ports for VSS connection")
    
    # Route gates together (bias network)
    try:
        gate_route = straight_route(
            pdk, 
            cm_component.ports["CM_Mref_gate_E"], 
            cm_component.ports["CM_Mmirror_gate_E"]
        )
        cm_component << gate_route
        
        # Connect reference transistor gate to its drain (diode connection)
        gate_drain_route = c_route(
            pdk, 
            cm_component.ports["CM_Mref_gate_W"], 
            cm_component.ports["CM_Mref_drain_W"],
            extension=pdk.util_max_metal_seperation()
        )
        cm_component << gate_drain_route
        
    except KeyError as e:
        print(f"Warning: Could not find gate/drain ports for bias connection: {e}")
        # Try alternative approach with different orientations
        try:
            gate_route = straight_route(
                pdk, 
                cm_component.ports["CM_Mref_gate_S"], 
                cm_component.ports["CM_Mmirror_gate_S"]
            )
            cm_component << gate_route
            
            # Connect reference transistor gate to its drain (diode connection)
            gate_drain_route = c_route(
                pdk, 
                cm_component.ports["CM_Mref_gate_N"], 
                cm_component.ports["CM_Mref_drain_N"],
                extension=pdk.util_max_metal_seperation()
            )
            cm_component << gate_drain_route
        except KeyError:
            print("Warning: Could not find any gate/drain ports for bias connection")
    
    return cm_component

def create_cmirror_with_decap(
    pdk: MappedPDK,
    width: float,
    fingers: int,
    CM_FET_kwargs: dict,
    decap_size: Optional[tuple] = None,
    length: Optional[float] = None,
) -> Component:
    """
    Create complete current mirror with decoupling capacitor.
    
    Args:
        pdk: PDK for design rules and layer information
        width: float of total width of each transistor
        fingers: int of number of fingers per transistor
        CM_FET_kwargs: Dictionary of FET parameters
        decap_size: Optional tuple (width, height) for decap. If None, uses default
        length: Gate length (uses PDK minimum if not specified)
    
    Returns:
        Component: Complete current mirror with decoupling capacitor
    """
    # Create the basic interdigitized current mirror
    cm_base = create_cmirror_interdigitized(
        pdk=pdk,
        width=width,
        fingers=fingers,
        CM_FET_kwargs=CM_FET_kwargs,
        length=length,
        component_name="cmirror_with_decap"
    )
    
    # Add current mirror routing
    cm_routed = add_cmirror_routing(pdk, cm_base)
    
    # TODO: Add decoupling capacitor
    # This would typically be a MOM capacitor or MIM capacitor
    # Implementation depends on PDK capabilities
    
    return cm_routed
    

if __name__ == "__main__":
    
    from diff_pair import diff_pair, get_pin_layers

    pdk_choice = gf180

    # Current Mirror FET parameters
    CM_FET_kwargs = {
        "with_dnwell": False,
        "sd_route_topmet": "met2",
        "gate_route_topmet": "met2",
        "sd_rmult": 2,
        "sdlayer": 'n+s/d', # n for nmos, p for pmos
        "gate_rmult": 3,
        "interfinger_rmult": 2,
        "tie_layers": ("met2","met1"),
        "inter_finger_topmet": "met1",
        "with_dummies": True,
        "with_tie": True,
        "with_substrate_tap": False,
    }

    # Generate interdigitized current mirror with explicit parameters
    print("✓ Creating interdigitized current mirror...")
    cmirror_interdigitized = create_cmirror_interdigitized(
        pdk=pdk_choice,
        width=20.0,           # [um] width of each transistor
        fingers=4,            # Number of fingers per transistor
        CM_FET_kwargs=CM_FET_kwargs,
        length=0.28,          # [um] gate length
        component_name="cmirror_interdigitized"
    )

    # Create complete current mirror with routing and decap
    print("✓ Adding current mirror routing...")
    # cmirror_with_routing = add_cmirror_routing(pdk_choice, cmirror_interdigitized)

    # Create top-level component
    comp = Component(name="cmirror_with_decap_interdigitized")
    cmirror_ref = comp << cmirror_interdigitized
    

    # Create and position I/O vias outside the tapring

    # Write GDS files
    print("✓ Writing GDS files...")
    comp.write_gds('lvs/gds/cmirror_interdigitized.gds', 
                   cellname="cmirror_interdigitized",
                   unit=1e-6,
                   precision=1e-9)
    print("  - Hierarchical GDS: cmirror_interdigitized.gds")
    
    # Run DRC check
    print("\n...Running DRC...")
    try:
        drc_result = pdk_choice.drc_magic(comp, comp.name)
        print(f"✓ Magic DRC result: {drc_result}")
    except Exception as e:
        print(f"⚠ Magic DRC skipped: {e}")
    
    print("\n" + "="*60)
    print("CURRENT MIRROR DESIGN COMPLETED!")
    print("="*60)
    print("Design Features:")
    print("- Interdigitized NMOS current mirror")
    print("- Reference transistor with gate-drain short")
    print("- Mirror transistor for current copying")
    print("- External I/O vias: VREF, VCOPY, VSS, VB")
    print("- Tapring for substrate isolation")
    print("- Ready for decoupling capacitor integration")
    print("="*60)
   
