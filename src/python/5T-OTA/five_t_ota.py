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
from diff_pair import diff_pair

# Add the Cmirror_with_decap module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../Cmirror_with_decap'))
from Cmirror_with_decap import CmirrorWithDecap, CMirrorConfig


@dataclass
class OTAConfig:
    """Configuration for 5T-OTA design"""
    # PMOS Current Mirror Configuration
    pmos_width: float = 0.3
    pmos_length: float = 0.28
    pmos_fingers: int = 1
    pmos_multipliers: int = 1
    
    # NMOS Differential Pair Configuration  
    nmos_width: float = 1.0
    nmos_length: float = 0.28
    nmos_fingers: int = 1
    nmos_multipliers: int = 1
    
    # Layout Configuration
    placement: str = "vertical"  # "vertical" or "horizontal"
    component_spacing: float = 2.0  # Spacing between components in um
    
    # Routing Configuration
    routing_metal: str = "met2"
    via_metal: str = "met1"
    
    # Debug and naming
    debug_mode: bool = True
    component_name: str = "5T_OTA"


class FiveTOTA:
    """
    Class for creating 5T-OTA layouts.
    
    The 5T-OTA consists of:
    1. PMOS current mirror (2 transistors) for active load and biasing
    2. NMOS differential pair (2 transistors) for input amplification
    3. Proper routing and connectivity between stages
    
    Design specifications:
    - PMOS mirror: 0.3um width, 0.28um length (min), without decap
    - Diff pair: 1.0um width, 0.28um length (min)
    """
    
    def __init__(
        self,
        pdk: MappedPDK,
        ota_config: Optional[OTAConfig] = None,
    ):
        """
        Initialize the 5T-OTA with configuration parameters.
        
        Args:
            pdk: PDK for design rules and layer information
            ota_config: Configuration for OTA design parameters
        """
        self.pdk = pdk
        self.pdk.activate()
        
        # Use default config if none provided
        if ota_config is None:
            ota_config = OTAConfig()
        self.config = ota_config
        
        # Store component references
        self.pmos_mirror = None
        self.diff_pair_comp = None
        self.top_level = None

    def create_pmos_mirror(self) -> Component:
        """Create PMOS current mirror without decap as specified."""
        print("🔧 Creating PMOS Current Mirror...")
        
        # Configuration for PMOS current mirror (without decap as requested)
        pmos_config = CMirrorConfig(
            sd_rmult=2,
            sd_route_topmet=self.config.routing_metal,
            gate_route_topmet=self.config.routing_metal,
            gate_rmult=1,
            interfinger_rmult=1,
            tie_layers=(self.config.routing_metal, self.config.via_metal),
            inter_finger_topmet=self.config.via_metal,
            sd_route_extension=0.0,
            gate_route_extension=0,
            sdlayer="p+s/d",
            routing=True,
            with_dummies=True,
            with_tie=True,
            with_dnwell=False,
            with_decap=False  # No decap as requested
        )
        
        # Create PMOS current mirror with specified dimensions
        pmos_mirror = CmirrorWithDecap(
            pdk=self.pdk,
            width_ref=self.config.pmos_width,  # 0.3um
            width_mir=self.config.pmos_width,  # 0.3um (matched for current mirror)
            fingers_ref=self.config.pmos_fingers,
            fingers_mir=self.config.pmos_fingers,
            length=self.config.pmos_length,  # 0.28um (min length)
            cmirror_config=pmos_config,
            component_name="pmos_current_mirror_5T_OTA"
        )
        
        return pmos_mirror.build()

    def create_diff_pair(self) -> Component:
        """Create NMOS differential pair as specified."""
        print("🔧 Creating NMOS Differential Pair...")
        
        # Create differential pair with specified dimensions
        diff_pair_comp = diff_pair(
            pdk=self.pdk,
            placement=self.config.placement,
            width=(self.config.nmos_width, self.config.nmos_width),  # 1.0um each
            length=(self.config.nmos_length, self.config.nmos_length),  # 0.28um each (min length)
            fingers=(self.config.nmos_fingers, self.config.nmos_fingers),
            multipliers=(self.config.nmos_multipliers, self.config.nmos_multipliers),
            dummy_1=(True, True),
            dummy_2=(True, True),
            connected_sources=True,  # Common source connection
            debug_mode=self.config.debug_mode,
            component_name="diff_pair_5T_OTA",
            vss_port_placement="S"  # VSS at bottom
        )
        
        return diff_pair_comp

    def create_routing(self) -> None:
        """Create routing connections between PMOS mirror and differential pair."""
        print("🔧 Creating routing connections...")
        
        # Get component references
        pmos_ref = self.pmos_mirror_ref
        diff_ref = self.diff_pair_ref
        
        try:
            # Connect PMOS mirror drains to differential pair drains
            # Mirror reference drain to diff pair M1 drain
            self.top_level << straight_route(
                self.pdk, 
                pmos_ref.ports["REF_DRAIN_S"], 
                diff_ref.ports["diff_pair_5T_OTA_M1_DRAIN_N"]
            )
            
            # Mirror output drain to diff pair M2 drain  
            self.top_level << straight_route(
                self.pdk,
                pmos_ref.ports["MIR_DRAIN_S"],
                diff_ref.ports["diff_pair_5T_OTA_M2_DRAIN_N"]
            )
            
            print("  ✓ Successfully connected PMOS drains to diff pair drains")
            
        except Exception as e:
            print(f"  ⚠ Routing connection failed, trying alternative routing: {e}")
            try:
                # Try C-routing as backup
                self.top_level << c_route(
                    self.pdk, 
                    pmos_ref.ports["REF_DRAIN_S"], 
                    diff_ref.ports["diff_pair_5T_OTA_M1_DRAIN_N"]
                )
                
                self.top_level << c_route(
                    self.pdk,
                    pmos_ref.ports["MIR_DRAIN_S"],
                    diff_ref.ports["diff_pair_5T_OTA_M2_DRAIN_N"]
                )
                print("  ✓ Successfully connected using C-routing")
            except Exception as e2:
                print(f"  ⚠ C-routing also failed: {e2}")

    def position_components(self) -> None:
        """Position PMOS mirror and differential pair components."""
        print("🔧 Positioning components...")
        
        # Get bounding boxes for spacing calculations
        pmos_bbox = evaluate_bbox(self.pmos_mirror)
        diff_bbox = evaluate_bbox(self.diff_pair_comp)
        
        # Position differential pair at origin (reference)
        self.diff_pair_ref.movex(0)
        self.diff_pair_ref.movey(0)
        
        # Position PMOS mirror above differential pair
        spacing_y = self.config.component_spacing
        pmos_y_position = diff_bbox[1] + spacing_y + pmos_bbox[1]/2
        
        self.pmos_mirror_ref.movex(0)  # Center horizontally
        self.pmos_mirror_ref.movey(pmos_y_position)
        
        print(f"  ✓ Positioned diff pair at origin")
        print(f"  ✓ Positioned PMOS mirror at y={pmos_y_position:.2f}um")

    def add_ota_ports(self) -> None:
        """Add external ports for the 5T-OTA."""
        print("🔧 Adding OTA external ports...")
        
        # Input ports from differential pair gates
        diff_ref = self.diff_pair_ref
        pmos_ref = self.pmos_mirror_ref
        
        # Differential input ports (VIN+ and VIN-)
        for orientation in [0, 90, 180, 270]:
            # VIN+ (M1 gate)
            self.top_level.add_port(
                center=diff_ref.ports["diff_pair_5T_OTA_M1_GATE_E"].center,
                width=diff_ref.ports["diff_pair_5T_OTA_M1_GATE_E"].width,
                orientation=orientation,
                layer=diff_ref.ports["diff_pair_5T_OTA_M1_GATE_E"].layer,
                name=f"{self.config.component_name}_VIN_P_{['E','N','W','S'][orientation//90]}"
            )
            
            # VIN- (M2 gate)
            self.top_level.add_port(
                center=diff_ref.ports["diff_pair_5T_OTA_M2_GATE_E"].center,
                width=diff_ref.ports["diff_pair_5T_OTA_M2_GATE_E"].width,
                orientation=orientation,
                layer=diff_ref.ports["diff_pair_5T_OTA_M2_GATE_E"].layer,
                name=f"{self.config.component_name}_VIN_N_{['E','N','W','S'][orientation//90]}"
            )
        
        # Output ports from PMOS mirror drains (differential outputs)
        for orientation in [0, 90, 180, 270]:
            # VOUT+ (typically the reference side)
            self.top_level.add_port(
                center=pmos_ref.ports["REF_DRAIN_S"].center,
                width=pmos_ref.ports["REF_DRAIN_S"].width,
                orientation=orientation,
                layer=pmos_ref.ports["REF_DRAIN_S"].layer,
                name=f"{self.config.component_name}_VOUT_P_{['E','N','W','S'][orientation//90]}"
            )
            
            # VOUT- (mirror side)
            self.top_level.add_port(
                center=pmos_ref.ports["MIR_DRAIN_S"].center,
                width=pmos_ref.ports["MIR_DRAIN_S"].width,
                orientation=orientation,
                layer=pmos_ref.ports["MIR_DRAIN_S"].layer,
                name=f"{self.config.component_name}_VOUT_N_{['E','N','W','S'][orientation//90]}"
            )

        # Power supply ports
        for orientation in [0, 90, 180, 270]:
            # VDD from PMOS sources
            self.top_level.add_port(
                center=pmos_ref.ports["REF_SOURCE_N"].center,
                width=pmos_ref.ports["REF_SOURCE_N"].width,
                orientation=orientation,
                layer=pmos_ref.ports["REF_SOURCE_N"].layer,
                name=f"{self.config.component_name}_VDD_{['E','N','W','S'][orientation//90]}"
            )
            
            # VSS from differential pair
            self.top_level.add_port(
                center=diff_ref.ports["diff_pair_5T_OTA_VSS_S"].center,
                width=diff_ref.ports["diff_pair_5T_OTA_VSS_S"].width,
                orientation=orientation,
                layer=diff_ref.ports["diff_pair_5T_OTA_VSS_S"].layer,
                name=f"{self.config.component_name}_VSS_{['E','N','W','S'][orientation//90]}"
            )

        # Bias current input
        for orientation in [0, 90, 180, 270]:
            self.top_level.add_port(
                center=pmos_ref.ports["REF_GATE_W"].center,
                width=pmos_ref.ports["REF_GATE_W"].width,
                orientation=orientation,
                layer=pmos_ref.ports["REF_GATE_W"].layer,
                name=f"{self.config.component_name}_IBIAS_{['E','N','W','S'][orientation//90]}"
            )

        print("  ✓ Added differential input ports (VIN+, VIN-)")
        print("  ✓ Added differential output ports (VOUT+, VOUT-)")
        print("  ✓ Added power supply ports (VDD, VSS)")
        print("  ✓ Added bias current port (IBIAS)")

    def build(self) -> Component:
        """
        Build the complete 5T-OTA layout.
        
        Returns:
            Component: Complete 5T-OTA layout component
        """
        print("\n" + "="*60)
        print("5T-OTA LAYOUT GENERATION")
        print("="*60)
        print(f"PMOS Mirror: {self.config.pmos_width}um width, {self.config.pmos_length}um length")
        print(f"Diff Pair: {self.config.nmos_width}um width, {self.config.nmos_length}um length")
        print("="*60)
        
        # Create top-level component
        self.top_level = Component(name=self.config.component_name)
        
        # Create sub-components
        self.pmos_mirror = self.create_pmos_mirror()
        self.diff_pair_comp = self.create_diff_pair()
        
        # Add components to top level
        print("🔧 Adding components to top level...")
        self.pmos_mirror_ref = self.top_level << self.pmos_mirror
        self.diff_pair_ref = self.top_level << self.diff_pair_comp
        
        self.pmos_mirror_ref.name = "pmos_current_mirror"
        self.diff_pair_ref.name = "differential_pair"
        
        # Position components
        self.position_components()
        
        # Create routing connections
        self.create_routing()
        
        # Add external ports
        self.add_ota_ports()
        
        # Snap to grid for clean layout
        self.top_level = component_snap_to_grid(self.top_level)
        
        print("\n" + "="*60)
        print("✅ 5T-OTA LAYOUT COMPLETED!")
        print("="*60)
        print(f"Component name: {self.config.component_name}")
        print(f"Total ports: {len(self.top_level.ports)}")
        
        return self.top_level


if __name__ == "__main__":
    # Example usage
    from glayout import gf180
    
    print("="*60)
    print("5T-OTA EXAMPLE USAGE")
    print("="*60)
    
    # Initialize PDK
    pdk_choice = gf180
    
    # Create configuration with specified parameters
    ota_config = OTAConfig(
        pmos_width=0.3,      # 0.3um as specified
        pmos_length=0.28,    # min length as specified  
        nmos_width=1.0,      # 1.0um as specified
        nmos_length=0.28,    # min length as specified
        component_name="5T_OTA_example",
        debug_mode=True
    )
    
    # Create 5T-OTA instance
    ota = FiveTOTA(
        pdk=pdk_choice,
        ota_config=ota_config
    )
    
    # Build the layout
    ota_component = ota.build()
    
    # Write GDS file
    print("📝 Writing GDS file...")
    ota_component.write_gds(
        'lvs/gds/5T_OTA.gds',
        cellname="5T_OTA",
        unit=1e-6,
        precision=5e-9
    )
    
    # Run DRC if available
    print("🔍 Running DRC...")
    try:
        drc_result = pdk_choice.drc_magic(ota_component, "5T_OTA")
        if drc_result:
            print(f"  ✓ DRC: {drc_result}")
    except Exception as e:
        print(f"  ⚠ DRC skipped: {e}")
    
    # Print port summary
    print("\n📋 Port Summary:")
    print(f"Total ports: {len(ota_component.ports)}")
    for port_name in sorted(ota_component.ports.keys()):
        print(f"  - {port_name}")
    
    print("\n✅ 5T-OTA example completed successfully!")
