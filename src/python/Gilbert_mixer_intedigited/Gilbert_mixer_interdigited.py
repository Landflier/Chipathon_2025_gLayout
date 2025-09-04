#!/usr/bin/env python3

import os
import sys
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
    length: float,
    width: float,
    fingers: int,
    LO_FET_kwargs: dict
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
    
    # Calculate finger width
    finger_width = width / fingers
    
    # Get parameters from LO_FET_kwargs
    sd_rmult = LO_FET_kwargs.get("sd_rmult", 1)
    sd_route_topmet = LO_FET_kwargs.get("sd_route_topmet", "met2")
    
    # Use PDK minimum length if not specified
    if length is None:
        length = pdk.get_grule('poly')['min_width']
    
    # Calculate poly height for transistor
    poly_height = finger_width + 2 * pdk.get_grule("poly", "active_diff")["overhang"]
    
    # Interdigitized finger generation logic (based on __gen_fingers_macro)
    # Snap dimensions to grid
    length = pdk.snap_to_2xgrid(length)
    finger_width = pdk.snap_to_2xgrid(finger_width)
    poly_height = pdk.snap_to_2xgrid(poly_height)
    sizing_ref_viastack = via_stack(pdk, "active_diff", "met1")
    
    # figure out poly (gate) spacing: s/d metal doesnt overlap transistor, s/d min seperation criteria is met
    sd_viaxdim = evaluate_bbox(via_stack(pdk, "active_diff", "met1"))[0]
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
        "sd_rmult" : 1,
        "rmult": None,
        "gate_rmult": 2,
        "interfinger_rmult": 2,
        "substrate_tap_layers": ("met2","met1"),
    }

    # Generate differential pair with explicit parameters
    LO_diff_pairs = create_LO_diff_pairs(
        pdk=pdk_choice,
        length=0.28,          # [um], length of channel
        width=20.0,           # [um],  width of channel
        fingers=5,            # Number of fingers
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
    
    print("\n...Running DRC...")
    
    try:
        drc_result = pdk_choice.drc_magic(comp, comp.name)
        print(f"✓ Magic DRC result: {drc_result}")
    except Exception as e:
        print(f"⚠ Magic DRC skipped: {e}")

    print("\n" + "="*60)
    print("TEST COMPLETED - GDS file generated successfully!")
    print("="*60)
    
    
