#!/usr/bin/env python3
"""
Simple test script for differential pair layout generation.
Based on the original __main__ block from diff_pair.py
"""

import os
import sys
from gdsfactory import Component

# Add the diff_pair module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'diff_pair'))

if __name__ == "__main__":
    from diff_pair import diff_pair
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
        "gate_route_topmet": "met1",
        "sd_route_left": True,
        "sd_rmult" : 2,
        "rmult": None,
        "gate_rmult": 2,
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
        component_name = "RF_diff_pair",   # Component's name
        M1_kwargs=RF_FET_kwargs,              # Additional M1 parameters
        M2_kwargs=RF_FET_kwargs              # Additional M2 parameters
    )

    LO_FET_kwargs = {
        "with_tie": False,
        "with_dnwell": False,
        "sd_route_topmet": "met2",
        "gate_route_topmet": "met3",
        "sd_route_left": True,
        "sd_rmult" : 2,
        "rmult": None,
        "gate_rmult": 2,
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
        component_name = "LO_diff_pair_2",   # Component's name
        M1_kwargs=LO_FET_kwargs,             # Additional M1 parameters
        M2_kwargs=LO_FET_kwargs              # Additional M2 parameters
    )

    comp = Component( name = "Gilbert_cell" )

    RF_diff_pair_ref = comp << RF_diff_pair
    LO_diff_pair_left_ref = comp << LO_diff_pair_left
    LO_diff_pair_right_ref = comp << LO_diff_pair_right

    # Print available ports for debugging
    print(f"DEBUG: RF ports: {list(RF_diff_pair_ref.ports.keys())}")
    print(f"DEBUG: LO_left ports: {list(LO_diff_pair_left_ref.ports.keys())}")
    print(f"DEBUG: LO_right ports: {list(LO_diff_pair_right_ref.ports.keys())}")

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
        
        comp << route_lo2
        comp << route_lo1
    except Exception as e:
        print(f"DEBUG: L_route route failed: {e}")



    # Routing the LO drains towards VDD and outside pins
    ## Get the LO drain port names (using the updated naming scheme)
    lo_left_m1_drain = "LO_diff_pair_1_M1_DRAIN_E"  
    lo_right_m1_drain = "LO_diff_pair_2_M1_DRAIN_E"
    lo_left_m2_drain = "LO_diff_pair_1_M2_DRAIN_E"  
    lo_right_m2_drain = "LO_diff_pair_2_M2_DRAIN_E"

    ## Check if the ports exist and get their centers
    lo_left_M1_drain = LO_diff_pair_left_ref.ports[lo_left_m1_drain]
    lo_right_M1_drain = LO_diff_pair_right_ref.ports[lo_right_m1_drain]
    lo_left_M2_drain = LO_diff_pair_left_ref.ports[lo_left_m2_drain]
    lo_right_M2_drain = LO_diff_pair_right_ref.ports[lo_right_m2_drain]
    
    ## Get port properties
    drain_width = lo_left_M1_drain.width
    lo_left_M1_center = lo_left_M1_drain.center
    lo_right_M1_center = lo_right_M1_drain.center
    lo_left_M2_center = lo_left_M2_drain.center
    lo_right_M2_center = lo_right_M2_drain.center
    
    # Calculate Y position (middle of the two drain centers)
    via_M1_y = (lo_left_M1_center[1] + lo_right_M1_center[1]) / 2
    via_M2_y = (lo_left_M2_center[1] + lo_right_M2_center[1]) / 2
    
    # Get tapring boundaries
    # For the right border of taprings, we need the rightmost edge of each tapring
    lo_left_bbox = evaluate_bbox(LO_diff_pair_left_ref)
    
    # Calculate via X positions: 0.5um right of the right border of each tapring
    via_M1_drains_LO_x = lo_left_M1_center[0] + lo_left_bbox[0] / 2 + 1.0  # Right edge of left tapring + 0.5um
    via_M2_drains_LO_x = lo_left_M2_center[0] + lo_left_bbox[0] / 2 + 1.0 + drain_width + sep_met3  # Right edge of left tapring + 0.5um

    # Create vias - using drain/drain layer from LO FET kwargs
    lo_sd_layer = LO_FET_kwargs["sd_route_topmet"]  # Should be "met2"
    
    # Create vias (square, matching the drain port width)
    via_drains_M1_LO = via_array(pdk_choice, "met4", "met3", 
                       size=(drain_width, drain_width),
                       fullbottom=True)
    via_drains_M2_LO = via_array(pdk_choice, "met4", "met3", 
                       size=(drain_width, drain_width),
                       fullbottom=True)
    
    # Add vias to component and position them
    via_drains_M1_LO_ref = comp << via_drains_M1_LO
    via_drains_M2_LO_ref = comp << via_drains_M2_LO
    
    via_drains_M1_LO_ref.move((via_M1_drains_LO_x, via_M1_y))
    via_drains_M2_LO_ref.move((via_M2_drains_LO_x, via_M2_y))
    
 
    route_lo_drain_1_M1 = L_route(
        pdk_choice, 
        lo_left_M1_drain,
        via_drains_M1_LO_ref['top_met_N'],
        hglayer=lo_sd_layer,
        vglayer="met3"
    )
    route_lo_drain_2_M1 = L_route(
        pdk_choice, 
        lo_right_M1_drain,
        via_drains_M1_LO_ref['top_met_N'],
        hglayer=lo_sd_layer,
        vglayer="met3"
    )

    route_lo_drain_1_M2 = L_route(
        pdk_choice, 
        lo_left_M2_drain,
        via_drains_M2_LO_ref['top_met_N'],
        hglayer=lo_sd_layer,
        vglayer="met3"
    )
    route_lo_drain_2_M2 = L_route(
        pdk_choice, 
        lo_right_M2_drain,
        via_drains_M2_LO_ref['top_met_N'],
        hglayer=lo_sd_layer,
        vglayer="met3"
    )
    
    comp << route_lo_drain_1_M1
    comp << route_lo_drain_2_M1
    comp << route_lo_drain_1_M2
    comp << route_lo_drain_2_M2

    # Write GDS file
    print("✓ Writing GDS file...")
    comp.write_gds('Gilbert_cell.gds')
    print("  - GDS file: Gilbert_cell.gds")
    
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
    
    
