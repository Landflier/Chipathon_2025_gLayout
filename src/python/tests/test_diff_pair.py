#!/usr/bin/env python3
"""
Simple test script for differential pair layout generation.
Based on the original __main__ block from diff_pair.py
"""

import os
import sys

# Add the diff_pair module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',  'diff_pair'))

if __name__ == "__main__":
    try:
        from diff_pair import diff_pair
        from glayout import gf180
        
        print("DIFFERENTIAL PAIR LAYOUT GENERATION TEST")
        print("="*60)
        M1_kwargs = {
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

        M2_kwargs = {
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
        comp = diff_pair(
            pdk=gf180,
            placement="vertical",
            width=(18.0, 18.0),          # Width in micrometers
            # length parameter omitted to use PDK minimum length
            fingers=(3, 3),            # Number of fingers
            multipliers=(1, 1),        # Multipliers
            dummy_1=(True, True),      # Dummy devices for M1
            dummy_2=(True, True),      # Dummy devices for M2
            tie_layers1=("met2", "met1"),  # Tie layers for M1
            tie_layers2=("met2", "met1"),  # Tie layers for M2
            sd_rmult=1,                # Source/drain routing multiplier
            connected_sources=True,    # Connect sources together
            M1_kwargs=M1_kwargs,              # Additional M1 parameters
            M2_kwargs=M2_kwargs               # Additional M2 parameters
        )
        
        # Set component name
        comp.name = "DIFF_PAIR"
        
        # Print basic info
        print(f"✓ Created differential pair: {comp.name}")
        
        # Write GDS file
        print("✓ Writing GDS file...")
        comp.write_gds('out_diff_pair.gds')
        print("  - GDS file: out_diff_pair.gds")
        
        # Show layout (if display available)
        try:
            comp.show()
            print("✓ Layout displayed successfully")
        except Exception as e:
            print(f"⚠ Could not display layout: {e}")
        
        # Simple DRC checks (skip if they fail due to Nix paths)
        print("\n...Running DRC...")
        
        try:
            drc_result = gf180.drc_magic(comp, comp.name)
            print(f"✓ Magic DRC result: {drc_result}")
        except Exception as e:
            print(f"⚠ Magic DRC skipped: {e}")
        
        """
        try:
            drc_result = gf180.drc(comp)
            print(f"✓ KLayout DRC result: {drc_result}")
        except Exception as e:
            print(f"⚠ KLayout DRC skipped: {e}")
        """
        
        print("\n" + "="*60)
        print("TEST COMPLETED - GDS file generated successfully!")
        print("="*60)
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure glayout and dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
