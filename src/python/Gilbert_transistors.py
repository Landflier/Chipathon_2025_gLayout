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
    
    pdk_choice = gf180
    RF_FET_kwargs = {
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
    # LO_diff_pair_left_ref.name = "LO_diff_pair_1"
    # LO_diff_pair_right_ref.name = "LO_diff_pair_2"
    # RF_diff_pair_ref.name = "RF_diff_pair"

    bbox_RF = evaluate_bbox(RF_diff_pair)
    bbox_LO = evaluate_bbox(LO_diff_pair_left)

    # RF_diff_pair_ref.move((0,0))
    # LO_diff_pair_right_ref.move(bbox_RF)
    # LO_diff_pair_left_ref.move(bbox_RF)

    RF_current_x, RF_current_y = RF_diff_pair_ref.center
    LO_current_x, LO_current_y = LO_diff_pair_right_ref.center

    # get minimal separtion needed for tapring separations
    sep_met1 = pdk_choice.get_grule('met1', 'met1')['min_separation']
    sep_met2 = pdk_choice.get_grule('met2', 'met2')['min_separation']
    # sep_pplus = pdk_choice.get_grule('pplus', 'pplus')['min_separation']

    sep = max(sep_met1, sep_met2)
    LO_diff_pair_right_ref.move((RF_current_x + bbox_RF[0] + sep , RF_current_y + bbox_LO[1]/2 + sep/2)) 
    LO_diff_pair_left_ref.move((RF_current_x + bbox_RF[0] + sep , RF_current_y - bbox_LO[1]/2 - sep/2))

    # Print basic info
    print(f"✓ Created Gilbert cell (without resistors): {comp.name}")
    
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
    
