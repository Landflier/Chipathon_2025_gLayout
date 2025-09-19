#!/usr/bin/env python3

import os
import sys
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from gdsfactory import Component
from gdsfactory.components import rectangle
from gdsfactory.cell import cell
from gdsfactory.component import copy

from glayout import gf180, MappedPDK
from glayout import nmos, pmos, tapring, mimcap
from glayout.routing.straight_route import straight_route
from glayout.routing.c_route import c_route
from glayout.routing.L_route import L_route
from glayout import via_stack, via_array
from glayout.primitives.via_gen import via_array, via_stack
from glayout.util.comp_utils import (
    evaluate_bbox, to_float, to_decimal, prec_array, 
    prec_center, prec_ref_center, movey, align_comp_to_port
)
from glayout.util.port_utils import (
    rename_ports_by_orientation, rename_ports_by_list, 
    add_ports_perimeter, print_ports
)
from glayout.util.snap_to_grid import component_snap_to_grid
from glayout.spice import Netlist
    
# Add the diff_pair module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../diff_pair'))
from diff_pair import get_pin_layers
    

if __name__ == "__main__":
    from glayout import gf180
    
    # Initialize PDK
    pdk_choice = gf180
    
    # Configure current mirror FETs
    """
    cmirror_nmos_config = CMirrorConfig(
        sd_rmult=2,
        sd_route_topmet="met2",
        gate_route_topmet="met2",
        gate_rmult=2,
        interfinger_rmult=2,
        tie_layers=("met2", "met1"),
        inter_finger_topmet="met1",
        sd_route_extension=0.0,
        gate_route_extension=0,
        sdlayer = "n+s/d",
        routing=True,
        with_dummies=False,
        with_tie=True,
        with_dnwell = False,
        with_decap = True
    )
    
    # Create current mirror instance
    cmirror_nmos = CmirrorWithDecap(
        pdk=pdk_choice,
        width_ref = 1.5,
        width_mir = 7.5,
        fingers_ref = 1,
        fingers_mir = 5,
        # width_ref=7.5,
        # width_mir=1.5,
        # fingers_ref=5,
        # fingers_mir=1,
        length=0.28,
        cmirror_config=cmirror_nmos_config,
        component_name="nmos_Cmirror_with_decap"
    )
    
    # Build the current mirror
    print("Building current mirror...")
    component = cmirror_nmos.build()

    # Run DRC
    print("\n...Running DRC...")
    drc_result = cmirror_nmos.run_drc()
    if drc_result:
        print(f"✓ Magic DRC result: {drc_result}")
    
    # Write GDS
    print("✓ Writing GDS files...")
    cmirror_nmos.write_gds('lvs/gds/nmos_Cmirror_with_decap.gds')
    print("  - Hierarchical GDS: nmos_Cmirror_with_decap.gds")

    
    
    # Configure current mirror FETs
    """
    cmirror_pmos_config = CMirrorConfig(
        sd_rmult=2,
        sd_route_topmet="met2",
        gate_route_topmet="met2",
        gate_rmult=2,
        interfinger_rmult=2,
        tie_layers=("met2", "met1"),
        inter_finger_topmet="met1",
        sd_route_extension=0.0,
        gate_route_extension=0,
        sdlayer = "p+s/d",
        routing=True,
        with_dummies=False,
        with_tie=True,
        with_dnwell = False,
        with_decap = True
    )
    
    # Create current mirror instance
    cmirror_pmos = CmirrorWithDecap(
        pdk=pdk_choice,
        width_ref=2,
        width_mir=4,
        fingers_ref=4,
        fingers_mir=8,
        length=0.28,
        cmirror_config=cmirror_pmos_config,
        component_name="pmos_Cmirror_with_decap"
    )
    
    # Build the current mirror
    print("Building current mirror...")
    component_2 = cmirror_pmos.build()
    
    # Write GDS
    print("✓ Writing GDS files...")
    cmirror_pmos.write_gds('lvs/gds/pmos_Cmirror_with_decap.gds')
    print("  - Hierarchical GDS: pmos_Cmirror_with_decap.gds")
    # Run DRC
    print("\n...Running DRC...")
    drc_result = cmirror_pmos.run_drc()
    if drc_result:
        print(f"✓ Magic DRC result: {drc_result}")
    
    print("\n" + "="*60)
    print("CURRENT MIRROR DESIGN COMPLETED!")
    print("="*60)
   
