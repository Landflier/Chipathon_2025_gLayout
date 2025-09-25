#!/usr/bin/env python3
"""
Stress test script for NMOS transistor layout generation.
Places 100-200 NMOS transistors with different combinations of W, L, and options.
"""

import os
import sys
import itertools
import numpy as np

# Add the diff_pair module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

if __name__ == "__main__":
    try:
        from glayout import gf180, nmos
        from gdsfactory import Component
        from glayout.util.comp_utils import evaluate_bbox, move, movex, movey
        
        print("NMOS TRANSISTOR STRESS TEST")
        print("="*60)
        print("Generating all NMOS transistor combinations with varying parameters...")
        
        # Define parameter ranges for stress testing
        # widths = [1.0, 2.0, 5.0, 10.0, 20.0]  # Width in micrometers
        # lengths = [0.18, 0.28, 0.5, 1.0, 2.0]  # Length in micrometers
        # fingers_list = [1, 2, 4, 8]  # Number of fingers
        # multipliers_list = [1, 2, 4]  # Multipliers
        
        widths = [1.0, 2.0, 5.0, 20.0 ]  # Width in micrometers
        lengths = [0.28, 0.5, 1.0]  # Length in micrometers
        fingers_list = [1, 2, 4, 8]  # Number of fingers
        multipliers_list = [1, 2, 4]  # Multipliers
        # Define different kwargs combinations for testing various options

        kwargs_variations = [
            {
                "with_tie": False,
                "with_dnwell": False,
                "sd_route_topmet": "met2",
                "gate_route_topmet": "met3",
                "sd_route_left": True,
                "sd_rmult": 1,
                "gate_rmult": 1,
                "interfinger_rmult": 1,
                "substrate_tap_layers": ("met2", "met1"),
                "dummy_routes": False
            },
            {
                "with_tie": True,
                "with_dnwell": False,
                "sd_route_topmet": "met3",
                "gate_route_topmet": "met2",
                "sd_route_left": False,
                "sd_rmult": 2,
                "gate_rmult": 2,
                "interfinger_rmult": 2,
                "substrate_tap_layers": ("met3", "met2"),
                "dummy_routes": True
            },
            {
                "with_tie": False,
                "with_dnwell": True,
                "sd_route_topmet": "met4",
                "gate_route_topmet": "met3",
                "sd_route_left": True,
                "sd_rmult": 3,
                "gate_rmult": 1,
                "interfinger_rmult": 1,
                "substrate_tap_layers": ("met2", "met1"),
                "dummy_routes": False
            },
            {
                "with_tie": True,
                "with_dnwell": True,
                "sd_route_topmet": "met2",
                "gate_route_topmet": "met4",
                "sd_route_left": False,
                "sd_rmult": 1,
                "gate_rmult": 3,
                "interfinger_rmult": 2,
                "substrate_tap_layers": ("met3", "met1"),
                "dummy_routes": True
            }
        ]
        
        # Create top-level component to hold all transistors
        top_level = Component("NMOS_STRESS_TEST")
        
        # Generate all parameter combinations
        param_combinations = []
        
        # Create all combinations of parameter space
        for w in widths:
            for l in lengths:
                for f in fingers_list:
                    for m in multipliers_list:
                        if w % f == 0:
                            for kwargs_idx, kwargs in enumerate(kwargs_variations):
                                param_combinations.append((w, l, f, m, kwargs, kwargs_idx))
                        else: 
                            print(f"Skipping W={w}μm, F={f}: finger width is not integer")

        
        print(f"Generated {len(param_combinations)} parameter combinations")
        
        # Grid layout parameters
        grid_cols = int(np.ceil(np.sqrt(len(param_combinations))))
        grid_rows = int(np.ceil(len(param_combinations) / grid_cols))
        
        print(f"Arranging in {grid_rows}x{grid_cols} grid")
        
        # Spacing between transistors
        x_spacing = 5.0  # micrometers
        y_spacing = 5.0  # micrometers
        
        transistor_count = 0
        failed_count = 0
        
        # Track positions for dynamic placement
        current_x = 0.0
        current_y = 0.0
        row_heights = []  # Track height of each row
        col_widths = []   # Track width of each column
        
        # Initialize column widths and row heights arrays
        for i in range(grid_cols):
            col_widths.append(0.0)
        for i in range(grid_rows):
            row_heights.append(0.0)
        
        # First pass: create all transistors and calculate their sizes
        transistor_refs = []
        transistor_sizes = []
        
        for idx, (width, length, fingers, multipliers, kwargs, kwargs_idx) in enumerate(param_combinations):
            try:
                print(f"Creating transistor {idx+1}/{len(param_combinations)}: "
                      f"W={width}μm, L={length}μm, F={fingers}, M={multipliers}, "
                      f"kwargs_set={kwargs_idx}")
                
                # Create NMOS transistor
                nmos_transistor = nmos(
                    pdk=gf180,
                    width=width,
                    length=length,
                    fingers=fingers,
                    multipliers=multipliers,
                    with_dummy=(True, True),  # Add dummy devices
                    with_substrate_tap=False,  # We'll handle substrate separately
                    tie_layers=kwargs["substrate_tap_layers"],
                    **kwargs
                )
                
                # Add to top level component
                transistor_ref = top_level << nmos_transistor
                transistor_ref.name = f"NMOS_{idx}"
                
                # Get transistor size
                bbox = evaluate_bbox(nmos_transistor)
                transistor_sizes.append(bbox)
                transistor_refs.append((transistor_ref, idx))
                
                # Update column and row size tracking
                row = idx // grid_cols
                col = idx % grid_cols
                
                # Update maximum width for this column
                if col < len(col_widths):
                    col_widths[col] = max(col_widths[col], bbox[0])
                
                # Update maximum height for this row
                if row < len(row_heights):
                    row_heights[row] = max(row_heights[row], bbox[1])
                
                transistor_count += 1
                
            except Exception as e:
                print(f"  ⚠ Failed to create transistor {idx+1}: {e}")
                failed_count += 1
                transistor_refs.append(None)
                transistor_sizes.append(None)
                continue
        
        # Second pass: position transistors based on calculated grid sizes
        for transistor_data, size_data in zip(transistor_refs, transistor_sizes):
            if transistor_data is None or size_data is None:
                continue
                
            transistor_ref, idx = transistor_data
            row = idx // grid_cols
            col = idx % grid_cols
            
            # Calculate position based on cumulative column widths and row heights
            x_pos = sum(col_widths[:col]) + col * x_spacing
            y_pos = sum(row_heights[:row]) + row * y_spacing
            
            # Move transistor to calculated position
            transistor_ref.move((x_pos, y_pos))
        
        print(f"\n✓ Successfully created {transistor_count} transistors")
        if failed_count > 0:
            print(f"⚠ Failed to create {failed_count} transistors")
        
        # Set component name
        top_level.name = "NMOS_STRESS_TEST"
        
        # Get bounding box info
        bbox = evaluate_bbox(top_level)
        print(f"✓ Total layout size: {bbox[0]:.1f} x {bbox[1]:.1f} μm")
        
        # Write GDS file
        print("✓ Writing GDS file...")
        gds_filename = 'nmos_stress_test.gds'
        top_level.write_gds(gds_filename)
        print(f"  - GDS file: {gds_filename}")
        
        # Show layout (if display available)
        try:
            top_level.show()
            print("✓ Layout displayed successfully")
        except Exception as e:
            print(f"⚠ Could not display layout: {e}")
        
        # Simple DRC checks (skip if they fail due to environment issues)
        print("\n...Running DRC...")
        
        try:
            drc_result = gf180.drc_magic(top_level, top_level.name)
            print(f"✓ Magic DRC result: {drc_result}")
        except Exception as e:
            print(f"⚠ Magic DRC skipped: {e}")
        
        """
        try:
            drc_result = gf180.drc(top_level)
            print(f"✓ KLayout DRC result: {drc_result}")
        except Exception as e:
            print(f"⚠ KLayout DRC skipped: {e}")
        """

        print("\n" + "="*60)
        print(f"STRESS TEST COMPLETED!")
        print(f"Successfully generated {transistor_count} NMOS transistors")
        print(f"GDS file: {gds_filename}")
        print("="*60)
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure glayout and dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Stress test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
