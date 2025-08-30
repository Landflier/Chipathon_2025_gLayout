#!/usr/bin/env python3

import os
import sys
from gdsfactory import Component
from gdsfactory.components import rectangle
from glayout import MappedPDK

# Add the diff_pair module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../diff_pair'))

def add_via_pins_and_labels(
    top_level: Component,
    via_ref: Component,
    pin_name: str,
    pdk: MappedPDK,
    pin_layer: str = "met4",
    debug_mode: bool = True,
) -> Component:
    """
    Add pins and labels to a via for external connectivity.
    
    Args:
        top_level: Component to add pins and labels to
        via_ref: Reference to the via component
        pin_name: Name for the pin and label
        pdk: PDK for layer information
        pin_layer: Metal layer for the pin (default: "met4")
        debug_mode: Whether to add visual labels (default: True)
    
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
    print(f"DEBUG: offset: {offset}")
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
    
    
if __name__ == "__main__":
    from diff_pair import diff_pair, get_pin_layers
    from glayout import gf180
    from glayout.util.comp_utils import evaluate_bbox, move, movex, movey
    from glayout.routing.straight_route import straight_route
    from glayout.routing.c_route import c_route
    from glayout.routing.L_route import L_route
    from glayout import via_stack, via_array
    
    pdk_choice = gf180
    RF_FET_kwargs = {
        "with_tie": False,
        "with_dnwell": False,
        "sd_route_topmet": "met2",
        "gate_route_topmet": "met2",
        "sd_route_left": True,
        "sd_rmult" : 2,
        "rmult": None,
        "gate_rmult": 4,
        "interfinger_rmult": 2,
        "substrate_tap_layers": ("met2","met1"),
        "dummy_routes": False
    }

    # Generate differential pair with explicit parameters
    RF_diff_pair = diff_pair(
        pdk=pdk_choice,
        placement="vertical",
        width=(10.0, 10.0),          # Width in micrometers
        # length parameter omitted to use PDK minimum length
        fingers=(5, 5),            # Number of fingers
        multipliers=(1, 1),        # Multipliers
        dummy_1=(True, True),      # Dummy devices for M1
        dummy_2=(True, True),      # Dummy devices for M2
        tie_layers1=("met2", "met1"),  # Tie layers for M1
        tie_layers2=("met2", "met1"),  # Tie layers for M2
        connected_sources=False,    # Connect sources together
        debug_mode = False,                  # dont add terminal labels and visual pins
        component_name = "RF_diff_pair",   # Component's name
        gate_pin_offset_x = 2,               # offset of the gate pins in the x direction
        M1_kwargs=RF_FET_kwargs,              # Additional M1 parameters
        M2_kwargs=RF_FET_kwargs              # Additional M2 parameters
    )

    LO_FET_kwargs = {
        "with_tie": False,
        "with_dnwell": False,
        "sd_route_topmet": "met2",
        "gate_route_topmet": "met2",
        "sd_route_left": True,
        "sd_rmult" : 4,
        "rmult": None,
        "gate_rmult": 4,
        "interfinger_rmult": 2,
        "substrate_tap_layers": ("met2","met1"),
        "dummy_routes": False
    }

    # Generate differential pair with explicit parameters
    LO_diff_pair_left = diff_pair(
        pdk=pdk_choice,
        placement="vertical",
        width=(20.0, 20.0),          # Width in micrometers
        fingers=(5, 5),            # Number of fingers
        multipliers=(1, 1),        # Multipliers
        dummy_1=(True, True),      # Dummy devices for M1
        dummy_2=(True, True),      # Dummy devices for M2
        tie_layers1=("met2", "met1"),  # Tie layers for M1
        tie_layers2=("met2", "met1"),  # Tie layers for M2
        connected_sources=True,    # Connect sources together
        debug_mode = False,                  # dont add terminal labels and visual pins
        component_name = "LO_diff_pair_1",   # Component's name
        M1_kwargs=LO_FET_kwargs,             # Additional M1 parameters
        M2_kwargs=LO_FET_kwargs              # Additional M2 parameters
    )

    LO_diff_pair_right = diff_pair(
        pdk=pdk_choice,
        placement="vertical",
        width=(20.0, 20.0),          # Width in micrometers
        fingers=(5, 5),            # Number of fingers
        multipliers=(1, 1),        # Multipliers
        dummy_1=(True, True),      # Dummy devices for M1
        dummy_2=(True, True),      # Dummy devices for M2
        tie_layers1=("met2", "met1"),  # Tie layers for M1
        tie_layers2=("met2", "met1"),  # Tie layers for M2
        connected_sources=True,    # Connect sources together
        debug_mode = False,                  # dont add terminal labels and visual pins
        component_name = "LO_diff_pair_2",   # Component's name
        M1_kwargs=LO_FET_kwargs,             # Additional M1 parameters
        M2_kwargs=LO_FET_kwargs              # Additional M2 parameters
    )

    comp = Component( name = "Gilbert_cell" )

    RF_diff_pair_ref = comp << RF_diff_pair
    LO_diff_pair_left_ref = comp << LO_diff_pair_left
    LO_diff_pair_right_ref = comp << LO_diff_pair_right

    # Print available ports for debugging
    # print(f"DEBUG: RF ports: {list(RF_diff_pair_ref.ports.keys())}")
    # print(f"DEBUG: LO_left ports: {list(LO_diff_pair_left_ref.ports.keys())}")
    # print(f"DEBUG: LO_right ports: {list(LO_diff_pair_right_ref.ports.keys())}")

    bbox_RF = evaluate_bbox(RF_diff_pair)
    bbox_LO = evaluate_bbox(LO_diff_pair_left)

    RF_current_x, RF_current_y = RF_diff_pair_ref.center
    LO_current_x, LO_current_y = LO_diff_pair_right_ref.center

    # get minimal separtion needed for tapring separations
    sep_met1 = pdk_choice.get_grule('met1', 'met1')['min_separation']
    sep_met2 = pdk_choice.get_grule('met2', 'met2')['min_separation']
    sep_met3 = pdk_choice.get_grule('met3', 'met3')['min_separation']
    # sep_pplus = pdk_choice.get_grule('pplus', 'pplus')['min_separation']

    sep = max(sep_met1, sep_met2)

    # Calculate total height of both LO pairs plus separation between them
    total_LO_height = 2 * bbox_LO[1] + sep
    
    # Calculate new positions - move() expects absolute positions
    # First, position them to the right of RF with proper separation
    new_x = bbox_RF[0] + sep
    
    # For Y positioning: center the combined LO pairs with RF center
    # The combined center should be at RF_current_y
    # So position them symmetrically around RF_current_y
    right_new_y = RF_current_y + (bbox_LO[1] + sep)/2
    left_new_y = RF_current_y - (bbox_LO[1] + sep)/2
    
    # Position LO pairs so their combined center aligns with RF center
    # Calculate relative movements from current positions
    right_current_x, right_current_y = LO_diff_pair_right_ref.center
    left_current_x, left_current_y = LO_diff_pair_left_ref.center
    
    # Calculate relative movements needed
    right_dx = new_x - right_current_x
    right_dy = right_new_y - right_current_y
    left_dx = new_x - left_current_x
    left_dy = left_new_y - left_current_y
    
    # Apply relative movements
    LO_diff_pair_right_ref = move(LO_diff_pair_right_ref, (right_dx, right_dy))
    LO_diff_pair_left_ref = move(LO_diff_pair_left_ref, (left_dx, left_dy))
    
    # Route the LO pairs' (left and right) sources to the drains of the RF_diff_pair

    ## choose ports to route
    lo_1_M1_source_port_name = "LO_diff_pair_1_M1_SOURCE_W"
    lo_2_M2_source_port_name = "LO_diff_pair_2_M2_SOURCE_W"
    rf_M1_drain_port_name = "RF_diff_pair_M1_DRAIN_N"
    rf_M2_drain_port_name = "RF_diff_pair_M2_DRAIN_S"

    rf_sd_layer = RF_FET_kwargs["sd_route_topmet"]
    
    try:
        route_lo1 = L_route(
            pdk_choice, 
            LO_diff_pair_left_ref.ports[lo_1_M1_source_port_name], 
            RF_diff_pair_ref.ports[rf_M2_drain_port_name],
            vglayer="met3"
       )
        route_lo2 = L_route(
            pdk_choice, 
            LO_diff_pair_right_ref.ports[lo_2_M2_source_port_name], 
            RF_diff_pair_ref.ports[rf_M1_drain_port_name],
            vglayer="met3"
       )

        # Vias at the end of the L routings, i.e on the drains of the RF FETs
        sd_width = RF_diff_pair_ref.ports[rf_M1_drain_port_name].width
        via_rf_m1 = via_array(pdk_choice, "met3", rf_sd_layer, 
                size=(sd_width, sd_width),
                fullbottom=True,
                lay_every_layer=True)
        via_rf_m2 = via_array(pdk_choice, "met3", rf_sd_layer, 
                size=(sd_width, sd_width),
                fullbottom=True,
                lay_every_layer=True)

        via_rf_m1_ref = comp << via_rf_m1
        via_rf_m2_ref = comp << via_rf_m2
        
        via_rf_m1_ref.move(RF_diff_pair_ref.ports[rf_M1_drain_port_name].center)
        via_rf_m2_ref.move(RF_diff_pair_ref.ports[rf_M2_drain_port_name].center)
        
        # Add pins and labels to RF vias
        add_via_pins_and_labels(comp, via_rf_m1_ref, "I_bias_p", pdk_choice, pin_layer="met3", debug_mode=True)
        add_via_pins_and_labels(comp, via_rf_m2_ref, "I_bias_n", pdk_choice, pin_layer="met3", debug_mode=True)
        
        comp << route_lo2
        comp << route_lo1
    except Exception as e:
        print(f"DEBUG: L_route route failed: {e}")


    ## Get the LO drain port names (using the updated naming scheme)
    lo_left_m1_drain = "LO_diff_pair_1_M1_DRAIN_E"  
    lo_right_m1_drain = "LO_diff_pair_2_M1_DRAIN_E"
    lo_left_m2_drain = "LO_diff_pair_1_M2_DRAIN_E"  
    lo_right_m2_drain = "LO_diff_pair_2_M2_DRAIN_E"

    ## get the ports
    lo_left_M1_drain = LO_diff_pair_left_ref.ports[lo_left_m1_drain]
    lo_right_M1_drain = LO_diff_pair_right_ref.ports[lo_right_m1_drain]
    lo_left_M2_drain = LO_diff_pair_left_ref.ports[lo_left_m2_drain]
    lo_right_M2_drain = LO_diff_pair_right_ref.ports[lo_right_m2_drain]
    
    # Use the new function to create vias and routing
    lo_sd_layer = LO_FET_kwargs["sd_route_topmet"]  # Should be "met2"
    lo_left_bbox = evaluate_bbox(LO_diff_pair_left_ref)
    # print(f"DEBUG: lo_left_bbox coordinates before via_IFs: {lo_left_bbox}")
    via_IF_pos_ref, via_IF_neg_ref = create_vias_and_route(
        comp, 
        lo_left_M1_drain, lo_right_M1_drain,  # First pair (M1 drains)
        lo_left_M2_drain, lo_right_M2_drain,  # Second pair (M2 drains)
        pdk_choice,
        offset = lo_left_M1_drain.width,
        lo_bbox=lo_left_bbox[0],  # Use actual bbox width
        route_hlayer=lo_sd_layer,
        route_vlayer="met3",
    )
    
    # Add pins and labels to IF output vias
    add_via_pins_and_labels(comp, via_IF_pos_ref, "V_out_p", pdk_choice, pin_layer="met4", debug_mode=True)
    add_via_pins_and_labels(comp, via_IF_neg_ref, "V_out_n", pdk_choice, pin_layer="met4", debug_mode=True)


    ## Get the LO drain port names (using the updated naming scheme)
    lo_left_m1_gate = "LO_diff_pair_1_M1_GATE_E"  
    lo_right_m1_gate = "LO_diff_pair_2_M1_GATE_E"
    lo_left_m2_gate = "LO_diff_pair_1_M2_GATE_E"  
    lo_right_m2_gate = "LO_diff_pair_2_M2_GATE_E"

    ## get the ports
    lo_left_M1_gate = LO_diff_pair_left_ref.ports[lo_left_m1_gate]
    lo_right_M1_gate = LO_diff_pair_right_ref.ports[lo_right_m1_gate]
    lo_left_M2_gate = LO_diff_pair_left_ref.ports[lo_left_m2_gate]
    lo_right_M2_gate = LO_diff_pair_right_ref.ports[lo_right_m2_gate]
    
    # Use the new function to create vias and routing
    lo_sd_layer = LO_FET_kwargs["gate_route_topmet"]  # Should be "met2"
    lo_left_bbox = evaluate_bbox(LO_diff_pair_left_ref)

    print(f"DEBUG: lo_left_bbox coordinates after via_IFs: {lo_left_bbox}")
    offset = 2*(via_IF_neg_ref.center[0] - via_IF_pos_ref.center[0]) + lo_left_M1_gate.width/2 + lo_left_M1_drain.width/2
    via_LO_ref, via_LO_b_ref = create_vias_and_route(
        comp, 
        lo_left_M1_gate, lo_right_M1_gate,  # First pair (M1 gates)
        lo_left_M2_gate, lo_right_M2_gate,  # Second pair (M2 gates)
        pdk_choice,
        lo_bbox=lo_left_bbox[0],  # Use actual bbox width
        offset = offset, 
        route_hlayer=lo_sd_layer,
        route_vlayer="met3",
    )
    
    # Add pins and labels to LO input vias
    add_via_pins_and_labels(comp, via_LO_ref, "V_LO", pdk_choice, pin_layer="met4", debug_mode=True)
    add_via_pins_and_labels(comp, via_LO_b_ref, "V_LO_b", pdk_choice, pin_layer="met4", debug_mode=True)

 
    # Add labels directly to RF gate ports
    rf_m1_gate_port = RF_diff_pair_ref.ports["RF_diff_pair_M1_GATE_E"]
    rf_m2_gate_port = RF_diff_pair_ref.ports["RF_diff_pair_M2_GATE_E"]
    
    # Get label layer
    pin_layer_gds, label_layer_gds = get_pin_layers(rf_m1_gate_port.layer, pdk_choice)
    
    # Add labels directly
    comp.add_label(text="RF_POS", position=rf_m1_gate_port.center, layer=label_layer_gds)
    comp.add_label(text="RF_NEG", position=rf_m2_gate_port.center, layer=label_layer_gds)
    
    print(f"Added RF gate labels at M1: {rf_m1_gate_port.center}, M2: {rf_m2_gate_port.center}")

    
    # Flatten the component for easier extraction
    flat_comp = comp.flatten()
    flat_comp.name = "Gilbert_cell"
    
    # Write both hierarchical and flattened GDS files
    print("✓ Writing GDS files...")
    comp.write_gds('Gilbert_cell_hierarchical.gds', cellname="Gilbert_cell")
    flat_comp.write_gds('Gilbert_cell.gds', cellname="Gilbert_cell")
    print("  - Hierarchical GDS: Gilbert_cell_hierarchical.gds")
    print("  - Flattened GDS: Gilbert_cell.gds (recommended for extraction)")
    
    # Simple DRC checks (skip if they fail due to Nix paths)

    print("\n...Running DRC...")
    
    try:
        drc_result = pdk_choice.drc_magic(comp, comp.name)
        print(f"✓ Magic DRC result: {drc_result}")
    except Exception as e:
        print(f"⚠ Magic DRC skipped: {e}")

    print("\n" + "="*60)
    print("TEST COMPLETED - GDS file generated successfully!")
    print("="*60)
    
    
