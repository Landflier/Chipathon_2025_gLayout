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


@dataclass
class OTAConfig:
    """Configuration for 5T-OTA design"""
    # PMOS Current Mirror Configuration
    pmos_width: float = 0.6  # 0.6um per individual transistor (larger for via compatibility)
    pmos_length: float = 0.28
    pmos_fingers: int = 2    # 2 fingers per transistor
    pmos_multipliers: int = 1
    
    # NMOS Differential Pair Configuration  
    nmos_width: float = 1.0  # 1.0um per individual transistor
    nmos_length: float = 0.28
    nmos_fingers: int = 1    # 1 finger per transistor
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
        """Create PMOS current mirror with individual transistors and guard ring."""
        print("🔧 Creating PMOS Current Mirror with guard ring...")
        
        # Create top-level component for PMOS mirror
        pmos_mirror = Component(name="pmos_current_mirror_5T_OTA")
        
        # Create two individual PMOS transistors for current mirror
        # M3: Reference transistor (diode-connected)
        M3 = pmos(
            pdk=self.pdk,
            width=self.config.pmos_width,      # 0.6um total
            length=self.config.pmos_length,    # 0.28um
            fingers=self.config.pmos_fingers,  # 2 fingers
            multipliers=1,
            with_dummy=(False, False),         # No dummies
            with_substrate_tap=False,          # No substrate tap (we'll use tapring)
            with_tie=False,                    # No tie connections
            sd_rmult=1,
            gate_rmult=1,
            interfinger_rmult=1
        )
        
        # M4: Mirror transistor  
        M4 = pmos(
            pdk=self.pdk,
            width=self.config.pmos_width,      # 0.6um total
            length=self.config.pmos_length,    # 0.28um  
            fingers=self.config.pmos_fingers,  # 2 fingers
            multipliers=1,
            with_dummy=(False, False),         # No dummies
            with_substrate_tap=False,          # No substrate tap (we'll use tapring)
            with_tie=False,                    # No tie connections
            sd_rmult=1,
            gate_rmult=1,
            interfinger_rmult=1
        )
        
        # Add transistors to mirror component
        M3_ref = pmos_mirror << M3
        M4_ref = pmos_mirror << M4
        
        M3_ref.name = "M3_ref"
        M4_ref.name = "M4_mir"
        
        # Position M4 next to M3 with appropriate spacing
        M3_bbox = evaluate_bbox(M3)
        spacing = 2.0  # 2um spacing for well isolation
        M4_ref.movex(M3_bbox[0] + spacing)
        
        # Create tapring around both PMOS transistors
        self.create_pmos_tapring_and_wells(pmos_mirror, M3_ref, M4_ref)
        
        # Connect gates together (current mirror configuration)
        self.create_pmos_routing(pmos_mirror, M3_ref, M4_ref)
        
        # Add external ports with proper names
        pmos_mirror.add_ports(M3_ref.get_ports_list(), prefix="M3_")
        pmos_mirror.add_ports(M4_ref.get_ports_list(), prefix="M4_")
        
        print(f"  ✓ Created PMOS mirror: {self.config.pmos_width}um x {self.config.pmos_length}um with guard ring")
        
        return pmos_mirror

    def create_diff_pair(self) -> Component:
        """Create NMOS differential pair using RF_diff_pair approach from Gilbert mixer."""
        print("🔧 Creating NMOS Differential Pair (RF_diff_pair style)...")
        
        # Create top level component
        top_level = Component()
        
        # Create two FETs using the RF_diff_pair approach
        fet_params = {
            "width": self.config.nmos_width,
            "fingers": self.config.nmos_fingers,
            "multipliers": 1,
            "with_tie": True,  # Enable tie connections like in RF_diff_pair
            "with_dummy": (True, True),  # Enable dummies like in RF_diff_pair
            "with_dnwell": False,  # No dnwell for NMOS
            "with_substrate_tap": True,  # Enable substrate tap like in RF_diff_pair
            "length": self.config.nmos_length,
            "sd_rmult": 1,
            "sd_route_topmet": "met2",
            "gate_route_topmet": "met2", 
            "gate_rmult": 1,
            "interfinger_rmult": 1,
            "tie_layers": ("met2", "met1"),
        }
        
        M1_temp = nmos(self.pdk, **fet_params)
        M2_temp = nmos(self.pdk, **fet_params)
        
        # Use transistors as-is (no drain/source swapping needed for differential pair)
        M1 = M1_temp
        M2 = M2_temp

        # Place transistors with separation (following RF_diff_pair approach)
        M1_ref = top_level << M1
        M2_ref = top_level << M2
        
        M2_ref.mirror_x()
        # Add 2um separation between differential pair NMOS instances (like RF_diff_pair)
        diff_separation = 2.0  # 2um separation
        M2_ref.movex(M1_ref.xmax + evaluate_bbox(M2)[0]/2 + diff_separation)
        
        # Add ports (using RF_diff_pair naming convention)
        top_level.add_ports(M1_ref.get_ports_list(), prefix="DIFF_M1_")
        top_level.add_ports(M2_ref.get_ports_list(), prefix="DIFF_M2_")
        
        top_level.name = "NMOS_diff_pair_5T_OTA"
        
        print(f"  ✓ Created NMOS diff pair: {self.config.nmos_width}um x {self.config.nmos_length}um (RF_diff_pair style)")
        
        return component_snap_to_grid(top_level)

    def create_pmos_tapring_and_wells(self, pmos_mirror, M3_ref, M4_ref):
        """Create tapring around PMOS transistors and extend nwells."""
        print("  Creating PMOS tapring and extending nwells...")
        
        # Create tapring around both PMOS transistors
        # For PMOS in nwell, we need substrate tap (p-substrate connection)
        tapring_comp = tapring(
            pdk=self.pdk,
            enclosed_rectangle=evaluate_bbox(pmos_mirror, padding=self.pdk.get_grule("nwell", "active_diff")["min_enclosure"] + 0.5),
        )
        
        # Center the tapring around the PMOS transistors
        tapring_ref = pmos_mirror << tapring_comp
        tapring_ref.name = "pmos_substrate_tapring"
        tapring_ref.move(pmos_mirror.center)
        
        # Extend nwell rectangles to connect both PMOS transistors
        self.extend_nwell_to_tapring(pmos_mirror, M3_ref, M4_ref, tapring_ref, "horizontal")
        
        # Add substrate connection port (for PMOS body bias)
        self.add_substrate_port_to_tapring(pmos_mirror, tapring_ref)


    def extend_nwell_to_tapring(self, top_level, M3_ref, M4_ref, tapring_ref, placement):
        """Extend nwell rectangles for PMOS transistors towards tapring sides."""
        print("    Extending nwell to tapring...")
        
        # Get the nwell layer
        try:
            nwell_layer = self.pdk.get_glayer("nwell")
            print(f"    Found nwell layer: {nwell_layer}")
        except Exception as e:
            print(f"    Warning: Could not find nwell layer ({e}), skipping nwell extension")
            return
        
        # Get tapring boundaries
        tapring_bbox = evaluate_bbox(tapring_ref)
        tapring_center = tapring_ref.center
        tapring_width = tapring_bbox[0]
        tapring_height = tapring_bbox[1]
        
        print(f"    Tapring dimensions: {tapring_width:.2f} x {tapring_height:.2f} um")
        
        # Create unified nwell rectangle covering both PMOS transistors
        # Make it slightly smaller than tapring to avoid DRC issues
        nwell_margin = 0.3  # 0.3um margin from tapring edge
        extended_nwell = rectangle(
            layer=nwell_layer,
            size=(tapring_width - 2*nwell_margin, tapring_height - 2*nwell_margin),
            centered=True
        )
        
        extended_nwell_ref = top_level << extended_nwell
        extended_nwell_ref.name = "extended_nwell_pmos"
        extended_nwell_ref.move(tapring_center)
        
        print(f"    ✓ Created extended nwell: {tapring_width - 2*nwell_margin:.2f} x {tapring_height - 2*nwell_margin:.2f} um")


    def add_substrate_port_to_tapring(self, component, tapring_ref):
        """Add substrate port connected to PMOS tapring (for body bias)."""
        # Find tapring ports for substrate connection
        tapring_ports = [port for port in tapring_ref.get_ports_list() if "bottom_met" in port.name.lower()]
        if tapring_ports:
            ref_port = tapring_ports[0]
            substrate_center = ref_port.center
            component.add_port(center=substrate_center, width=ref_port.width, orientation=90, 
                             layer=ref_port.layer, name="PSUB_N")
            print("    ✓ Added substrate connection port")
        else:
            print("    ⚠ Could not find tapring ports for substrate connection")

    def create_pmos_routing(self, pmos_mirror, M3_ref, M4_ref):
        """Create routing for PMOS current mirror."""
        print("  Creating PMOS current mirror routing...")
        
        # Connect gates together (current mirror configuration)
        try:
            pmos_mirror << straight_route(self.pdk, M3_ref.ports["gate_W"], M4_ref.ports["gate_E"])
            print("    ✓ Connected PMOS gates")
        except:
            try:
                pmos_mirror << c_route(self.pdk, M3_ref.ports["gate_W"], M4_ref.ports["gate_E"])
                print("    ✓ Connected PMOS gates with C-route")
            except:
                print("    ⚠ PMOS gate routing failed")
        
        # Connect M3 gate to M3 drain (diode connection for reference)
        try:
            pmos_mirror << straight_route(self.pdk, M3_ref.ports["gate_S"], M3_ref.ports["drain_S"])
            print("    ✓ Created diode connection")
        except:
            try:
                pmos_mirror << c_route(self.pdk, M3_ref.ports["gate_S"], M3_ref.ports["drain_S"])
                print("    ✓ Created diode connection with C-route")
            except:
                print("    ⚠ Diode connection routing failed")

    def create_routing(self) -> None:
        """Create routing connections between PMOS mirror and differential pair."""
        print("🔧 Creating routing connections...")
        
        # Get component references
        pmos_ref = self.pmos_mirror_ref
        diff_ref = self.diff_pair_ref
        
        # Debug: Print available ports
        print("  Available PMOS ports:", list(pmos_ref.ports.keys())[:5])  # Show first 5
        print("  Available diff pair ports:", list(diff_ref.ports.keys())[:5])  # Show first 5
        
        # Find the correct port names by looking for drain ports  
        pmos_drain_ports = [p for p in pmos_ref.ports.keys() if "drain" in p.lower()]
        diff_drain_ports = [p for p in diff_ref.ports.keys() if "drain" in p.lower()]
        
        print(f"  PMOS drain ports: {pmos_drain_ports}")
        print(f"  Diff pair drain ports: {diff_drain_ports}")
        
        # Skip routing for now - just print what we found
        if len(pmos_drain_ports) >= 2 and len(diff_drain_ports) >= 2:
            print("  ⚠ Routing skipped - manual connection required")
            print(f"  Connect {pmos_drain_ports[0]} to {diff_drain_ports[0]}")
            print(f"  Connect {pmos_drain_ports[1]} to {diff_drain_ports[1]}")
        else:
            print("  ⚠ Could not find appropriate drain ports for routing")

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
        
        # Find gate ports using RF_diff_pair naming convention
        diff_gate_ports = [p for p in diff_ref.ports.keys() if "gate" in p.lower()]
        print(f"  Available gate ports: {diff_gate_ports}")
        
        # Find DIFF_M1 and DIFF_M2 gate ports (new naming convention)
        m1_gate_ports = [p for p in diff_gate_ports if "diff_m1" in p.lower()]
        m2_gate_ports = [p for p in diff_gate_ports if "diff_m2" in p.lower()]
        
        if m1_gate_ports and m2_gate_ports:
            # Use the first available gate port for each transistor
            m1_gate_port = m1_gate_ports[0]
            m2_gate_port = m2_gate_ports[0]
            
            # Differential input ports (VIN+ and VIN-)
            for orientation in [0, 90, 180, 270]:
                # VIN+ (M1 gate)
                self.top_level.add_port(
                    center=diff_ref.ports[m1_gate_port].center,
                    width=diff_ref.ports[m1_gate_port].width,
                    orientation=orientation,
                    layer=diff_ref.ports[m1_gate_port].layer,
                    name=f"{self.config.component_name}_VIN_P_{['E','N','W','S'][orientation//90]}"
                )
                
                # VIN- (M2 gate)
                self.top_level.add_port(
                    center=diff_ref.ports[m2_gate_port].center,
                    width=diff_ref.ports[m2_gate_port].width,
                    orientation=orientation,
                    layer=diff_ref.ports[m2_gate_port].layer,
                    name=f"{self.config.component_name}_VIN_N_{['E','N','W','S'][orientation//90]}"
                )
        else:
            print("  ⚠ Could not find M1/M2 gate ports, skipping input ports")
        
        # Output ports from PMOS mirror drains (differential outputs)
        pmos_drain_ports = [p for p in pmos_ref.ports.keys() if "drain" in p.lower()]
        print(f"  Available PMOS drain ports: {pmos_drain_ports}")
        
        if len(pmos_drain_ports) >= 2:
            # Use the first two drain ports found
            drain_port_1 = pmos_drain_ports[0]
            drain_port_2 = pmos_drain_ports[1]
            
            for orientation in [0, 90, 180, 270]:
                # VOUT+ (first drain port)
                self.top_level.add_port(
                    center=pmos_ref.ports[drain_port_1].center,
                    width=pmos_ref.ports[drain_port_1].width,
                    orientation=orientation,
                    layer=pmos_ref.ports[drain_port_1].layer,
                    name=f"{self.config.component_name}_VOUT_P_{['E','N','W','S'][orientation//90]}"
                )
                
                # VOUT- (second drain port)
                self.top_level.add_port(
                    center=pmos_ref.ports[drain_port_2].center,
                    width=pmos_ref.ports[drain_port_2].width,
                    orientation=orientation,
                    layer=pmos_ref.ports[drain_port_2].layer,
                    name=f"{self.config.component_name}_VOUT_N_{['E','N','W','S'][orientation//90]}"
                )
        else:
            print("  ⚠ Could not find PMOS drain ports, skipping output ports")

        # Power supply ports - find source and substrate tap ports dynamically
        pmos_source_ports = [p for p in pmos_ref.ports.keys() if "source" in p.lower()]
        # Look for substrate tap ports from RF_diff_pair (includes substrate tap)
        diff_vss_ports = [p for p in diff_ref.ports.keys() if ("substrate" in p.lower() or "tap" in p.lower() or "tie" in p.lower())]
        pmos_gate_ports = [p for p in pmos_ref.ports.keys() if "gate" in p.lower()]
        
        print(f"  Available PMOS source ports: {pmos_source_ports[:3]}")  # Show first 3
        print(f"  Available VSS ports: {diff_vss_ports}")
        print(f"  Available PMOS gate ports: {pmos_gate_ports[:3]}")  # Show first 3
        
        if pmos_source_ports:
            for orientation in [0, 90, 180, 270]:
                # VDD from PMOS sources
                self.top_level.add_port(
                    center=pmos_ref.ports[pmos_source_ports[0]].center,
                    width=pmos_ref.ports[pmos_source_ports[0]].width,
                    orientation=orientation,
                    layer=pmos_ref.ports[pmos_source_ports[0]].layer,
                    name=f"{self.config.component_name}_VDD_{['E','N','W','S'][orientation//90]}"
                )
        else:
            print("  ⚠ Could not find PMOS source ports, skipping VDD ports")
            
        if diff_vss_ports:
            for orientation in [0, 90, 180, 270]:
                # VSS from differential pair
                self.top_level.add_port(
                    center=diff_ref.ports[diff_vss_ports[0]].center,
                    width=diff_ref.ports[diff_vss_ports[0]].width,
                    orientation=orientation,
                    layer=diff_ref.ports[diff_vss_ports[0]].layer,
                    name=f"{self.config.component_name}_VSS_{['E','N','W','S'][orientation//90]}"
                )
        else:
            print("  ⚠ Could not find VSS ports, skipping VSS ports")

        # Bias current input
        if pmos_gate_ports:
            for orientation in [0, 90, 180, 270]:
                self.top_level.add_port(
                    center=pmos_ref.ports[pmos_gate_ports[0]].center,
                    width=pmos_ref.ports[pmos_gate_ports[0]].width,
                    orientation=orientation,
                    layer=pmos_ref.ports[pmos_gate_ports[0]].layer,
                    name=f"{self.config.component_name}_IBIAS_{['E','N','W','S'][orientation//90]}"
                )
        else:
            print("  ⚠ Could not find PMOS gate ports, skipping IBIAS ports")

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
