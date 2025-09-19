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

# Add the Cmirror_with_decap module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../Cmirror_with_decap'))
from Cmirror_with_decap import CmirrorWithDecap, CMirrorConfig
    

if __name__ == "__main__":
    from glayout import gf180
    
    # Initialize PDK
    pdk_choice = gf180
    
    print("="*60)
    print("BIASING NETWORK - 4 CURRENT MIRRORS WITH DECAP")
    print("="*60)
    
    # =================================================================
    # PMOS Current Mirror with Decap (1x)
    # =================================================================
    print("\n🔧 Creating PMOS Current Mirror with Decap...")
    
    pmos_config = CMirrorConfig(
        sd_rmult=4,
        sd_route_topmet="met2",
        gate_route_topmet="met2",
        gate_rmult=2,
        interfinger_rmult=2,
        tie_layers=("met2", "met1"),
        inter_finger_topmet="met1",
        sd_route_extension=0.0,
        gate_route_extension=0,
        sdlayer="p+s/d",
        routing=True,
        with_dummies=False,
        with_tie=True,
        with_dnwell=False,
        with_decap=True
    )
    
    pmos_mirror = CmirrorWithDecap(
        pdk=pdk_choice,
        width_ref=2.0,
        width_mir=6.0,
        fingers_ref=4,
        fingers_mir=12,
        length=0.4,
        cmirror_config=pmos_config,
        component_name="pmos_Cmirror_with_decap"
    )
    
    print("  Building PMOS mirror...")
    pmos_component = pmos_mirror.build()
    
    # =================================================================
    # NMOS Current Mirror 1 with Decap 
    # =================================================================
    print("\n🔧 Creating NMOS Current Mirror 1 with Decap...")
    
    nmos1_config = CMirrorConfig(
        sd_rmult=2,
        sd_route_topmet="met2",
        gate_route_topmet="met2",
        gate_rmult=2,
        interfinger_rmult=2,
        tie_layers=("met2", "met1"),
        inter_finger_topmet="met1",
        sd_route_extension=0.0,
        gate_route_extension=0,
        sdlayer="n+s/d",
        routing=True,
        with_dummies=False,
        with_tie=True,
        with_dnwell=False,
        with_decap=True
    )
    
    nmos1_mirror = CmirrorWithDecap(
        pdk=pdk_choice,
        width_ref=1.5,
        width_mir=7.5,
        fingers_ref=2,
        fingers_mir=10,
        length=1.0,
        cmirror_config=nmos1_config,
        component_name="nmos1_Cmirror_with_decap"
    )
    
    print("  Building NMOS1 mirror...")
    nmos1_component = nmos1_mirror.build()
    
    # =================================================================
    # NMOS Current Mirror 2 with Decap 
    # =================================================================
    print("\n🔧 Creating NMOS Current Mirror 2 with Decap...")
    
    nmos2_config = CMirrorConfig(
        sd_rmult=2,
        sd_route_topmet="met2",
        gate_route_topmet="met2",
        gate_rmult=2,
        interfinger_rmult=2,
        tie_layers=("met2", "met1"),
        inter_finger_topmet="met1",
        sd_route_extension=0.0,
        gate_route_extension=0,
        sdlayer="n+s/d",
        routing=True,
        with_dummies=False,
        with_tie=True,
        with_dnwell=False,
        with_decap=True
    )
    
    nmos2_mirror = CmirrorWithDecap(
        pdk=pdk_choice,
        width_ref=1.5,
        width_mir=7.5,
        fingers_ref=2,
        fingers_mir=10,
        length=1.0,
        cmirror_config=nmos2_config,
        component_name="nmos2_Cmirror_with_decap"
    )
    
    print("  Building NMOS2 mirror...")
    nmos2_component = nmos2_mirror.build()
    
    # =================================================================
    # NMOS Current Mirror 3 with Decap 
    # =================================================================
    print("\n🔧 Creating NMOS Current Mirror 3 with Decap...")
    
    nmos3_config = CMirrorConfig(
        sd_rmult=2,
        sd_route_topmet="met2",
        gate_route_topmet="met2",
        gate_rmult=2,
        interfinger_rmult=2,
        tie_layers=("met2", "met1"),
        inter_finger_topmet="met1",
        sd_route_extension=0.0,
        gate_route_extension=0,
        sdlayer="n+s/d",
        routing=True,
        with_dummies=False,
        with_tie=True,
        with_dnwell=False,
        with_decap=True
    )
    
    nmos3_mirror = CmirrorWithDecap(
        pdk=pdk_choice,
        width_ref=1.5,
        width_mir=1.5,
        fingers_ref=2,
        fingers_mir=2,
        length=1.0,
        cmirror_config=nmos3_config,
        component_name="nmos3_Cmirror_with_decap"
    )
    
    print("  Building NMOS3 mirror...")
    nmos3_component = nmos3_mirror.build()
    
    # =================================================================
    # Create Top-Level Biasing Network Component
    # =================================================================
    print("\n🔧 Creating Top-Level Biasing Network Component...")
    
    # Create the top-level component
    biasing_network = Component(name="Biasing_network_with_local_mirrors")
    
    # Add all current mirrors to the top-level component
    print("  Adding PMOS mirror to top-level...")
    pmos_ref = biasing_network << pmos_component
    
    print("  Adding NMOS mirrors to top-level...")
    nmos1_ref = biasing_network << nmos1_component
    nmos2_ref = biasing_network << nmos2_component  
    nmos3_ref = biasing_network << nmos3_component
    
    # Position the components in a 2x2 grid layout
    print("  Positioning components...")
    
    # Calculate spacing based on component sizes
    pmos_bbox = evaluate_bbox(pmos_component)
    nmos1_bbox = evaluate_bbox(nmos1_component)
    nmos2_bbox = evaluate_bbox(nmos2_component)
    nmos3_bbox = evaluate_bbox(nmos3_component)
    
    # Add spacing between components
    x_spacing = 20.0  # 20um spacing
    y_spacing = 10.0  # 20um spacing
    
    # Position PMOS at top-left (reference position)
    pmos_ref.movex(0)
    pmos_ref.movey(max(nmos1_bbox[1], nmos2_bbox[1]) + y_spacing)
    
    # Position NMOS1 at bottom-left  
    nmos1_ref.movex(0)
    nmos1_ref.movey(0)
    
    # Position NMOS2 at bottom-right
    nmos2_ref.mirror_x()
    nmos2_ref.movex(max(pmos_bbox[0], nmos1_bbox[0]) + x_spacing)
    nmos2_ref.movey(0)
    
    # Position NMOS3 at top-right
    nmos3_ref.movex(max(pmos_bbox[0], nmos1_bbox[0]) + x_spacing)
    nmos3_ref.movey(max(nmos1_bbox[1], nmos2_bbox[1]) + y_spacing)
    
    # Add ports from all components with prefixes
    print("  Adding component ports...")
    biasing_network.add_ports(pmos_ref.get_ports_list(), prefix="PMOS_")
    biasing_network.add_ports(nmos1_ref.get_ports_list(), prefix="NMOS1_")
    biasing_network.add_ports(nmos2_ref.get_ports_list(), prefix="NMOS2_")
    biasing_network.add_ports(nmos3_ref.get_ports_list(), prefix="NMOS3_")
    
    # Write the combined GDS file
    print("  Writing combined GDS file...")
    biasing_network.write_gds(
        'lvs/gds/Biasing_network_with_local_mirrors.gds',
        cellname="Biasing_network_with_local_mirrors",
        unit=1e-6,
        precision=5e-9
    )
    
    # Run DRC on the complete biasing network
    print("  Running complete biasing network DRC...")
    try:
        biasing_drc = pdk_choice.drc_magic(biasing_network, "Biasing_network_with_local_mirrors")
        if biasing_drc:
            print(f"  ✓ Biasing Network DRC: {biasing_drc}")
    except Exception as e:
        print(f"  ⚠ Biasing Network DRC skipped: {e}")
    
    # =================================================================
    # Summary
    # =================================================================
    print("\n" + "="*60)
    print("✅ BIASING NETWORK WITH LOCAL MIRRORS COMPLETED!")
    print("="*60)
   
