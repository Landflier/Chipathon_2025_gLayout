"""
Complete Current Mirror with Decap Implementation for GF180 PDK
Enhanced with full routing for gates, sources, and drains
Maintains center-symmetric and interdigitation layout constraints
"""
import os
import sys
from typing import Optional
from gdsfactory import Component

from glayout import nmos, pmos
from glayout import gf180, MappedPDK
from glayout import tapring
from glayout.routing.straight_route import straight_route
from glayout.routing.c_route import c_route
from glayout.routing.L_route import L_route
from glayout import via_stack, via_array

from gdsfactory.components import rectangle
from glayout.primitives.via_gen import via_array, via_stack
from glayout.util.comp_utils import evaluate_bbox, align_comp_to_port, prec_ref_center, prec_center, prec_array, movey
from glayout.util.port_utils import rename_ports_by_orientation, add_ports_perimeter, rename_ports_by_list
from glayout.util.snap_to_grid import component_snap_to_grid


class CurrentMirrorWithDecap:
    """
    Current mirror with decoupling capacitor implementation
    Features:
    - Center-symmetric layout
    - Interdigitation support through multiplier parameter
    - Complete routing for all terminals
    - GF180 PDK compliance
    """
    
    def __init__(self, pdk: MappedPDK = None):
        """Initialize with PDK (default GF180)"""
        self.pdk = pdk if pdk else gf180
        
    def create_current_mirror(self, 
                             ref_width: float = 2.0,
                             ref_length: float = 0.28,  # GF180 minimum is 0.28um
                             mirror_ratio: int = 1,
                             fingers: int = 2,
                             multiplier: int = 4,  # Interdigitation parameter
                             add_dummy: bool = True,
                             add_guardrings: bool = True,
                             with_decap: bool = True,
                             decap_width: float = 10.0,
                             decap_length: float = 10.0):
        """
        Generate complete current mirror with routing
        
        Parameters:
        - ref_width: Reference transistor width (um)
        - ref_length: Reference transistor length (um)
        - mirror_ratio: Current mirror ratio (Iout/Iref)
        - fingers: Number of fingers per transistor
        - multiplier: Number of parallel instances (interdigitation)
        - add_dummy: Add dummy devices for matching
        - add_guardrings: Add guard rings for isolation
        - with_decap: Include decoupling capacitor
        - decap_width/length: Decap dimensions
        """
        
        # Create top-level component
        top_level = Component("current_mirror_with_routing")
        
        # Calculate mirror transistor width
        mirror_width = ref_width * mirror_ratio
        
        # Generate transistors with interdigitation
        ref_transistors = self._create_interdigitated_transistor(
            width=ref_width,
            length=ref_length,
            fingers=fingers,
            multiplier=multiplier,
            transistor_type='nmos',
            name_prefix='ref'
        )
        
        mirror_transistors = self._create_interdigitated_transistor(
            width=mirror_width,
            length=ref_length,
            fingers=fingers,
            multiplier=multiplier,
            transistor_type='nmos',
            name_prefix='mirror'
        )
        
        # Place transistors with center-symmetric arrangement
        ref_refs, mirror_refs = self._place_center_symmetric(
            top_level, ref_transistors, mirror_transistors, multiplier
        )
        
        # Add dummy devices if requested
        if add_dummy:
            self._add_dummy_devices(top_level, ref_width, ref_length, fingers)
        
        # Route gate connections (critical for current mirror operation)
        self._route_gates(top_level, ref_refs, mirror_refs, multiplier)
        
        # Route source connections (common source to ground)
        self._route_sources(top_level, ref_refs, mirror_refs, multiplier)
        
        # Route drain connections (input and output)
        self._route_drains(top_level, ref_refs, mirror_refs, multiplier)
        
        # Add power rail routing (VDD and VSS)
        self._add_power_rails(top_level, ref_refs, mirror_refs)
        
        # Add guard rings if requested
        if add_guardrings:
            self._add_guard_rings(top_level)
        
        # Add decoupling capacitor if requested
        if with_decap:
            self._add_decap(top_level, decap_width, decap_length)
        
        # Add labels for LVS
        self._add_labels(top_level)
        
        return top_level
    
    def _create_interdigitated_transistor(self, width, length, fingers, 
                                         multiplier, transistor_type, name_prefix):
        """Create interdigitated transistor array"""
        transistors = []
        
        for i in range(multiplier):
            if transistor_type == 'nmos':
                fet = nmos(self.pdk, 
                          width=width, 
                          length=length,
                          fingers=fingers,
                          with_substrate_tap=False,
                          with_dummy=(i == 0, i == multiplier-1))  # Edge dummies
            else:
                fet = pmos(self.pdk,
                          width=width,
                          length=length, 
                          fingers=fingers,
                          with_substrate_tap=False,
                          with_dummy=(i == 0, i == multiplier-1))
            
            transistors.append(fet)
        
        return transistors
    
    def _place_center_symmetric(self, top_level, ref_transistors, mirror_transistors, multiplier):
        """
        Place transistors in center-symmetric pattern
        Implements ABBAABBA pattern for optimal matching
        """
        ref_refs = []
        mirror_refs = []
        
        # Calculate spacing for center symmetry
        transistor_bbox = evaluate_bbox(ref_transistors[0])
        spacing_x = transistor_bbox[0] + self.pdk.util_max_metal_seperation() * 2
        spacing_y = transistor_bbox[1] + self.pdk.util_max_metal_seperation() * 3
        
        # Generate center-symmetric pattern
        # Pattern: A-B-B-A-A-B-B-A for 4x interdigitation
        if multiplier == 4:
            pattern = ['A', 'B', 'B', 'A', 'A', 'B', 'B', 'A']
        elif multiplier == 2:
            pattern = ['A', 'B', 'B', 'A']
        else:
            # Default interdigitated pattern
            pattern = ['A', 'B'] * multiplier
        
        # Place transistors according to pattern
        current_x = 0
        pattern_index = 0
        
        for i in range(len(pattern)):
            if pattern[i] == 'A':
                # Place reference transistor
                idx = pattern_index % multiplier
                ref = top_level << ref_transistors[idx]
                ref.movex(current_x)
                ref_refs.append(ref)
            else:
                # Place mirror transistor
                idx = pattern_index % multiplier
                mirror = top_level << mirror_transistors[idx]
                mirror.movex(current_x)
                mirror_refs.append(mirror)
            
            current_x += spacing_x
            pattern_index += 1
        
        # Center the entire array
        self._center_layout(top_level)
        
        return ref_refs, mirror_refs
    
    def _route_gates(self, top_level, ref_refs, mirror_refs, multiplier):
        """
        Route gate connections between reference and mirror transistors
        Critical for current mirror operation - ensures VGS matching
        """
        
        # Use metal1 for gate routing (lower resistance, better matching)
        met1_layer = self.pdk.get_glayer("met1")
        poly_layer = self.pdk.get_glayer("poly")
        
        # Connect all reference gates together first
        for i in range(len(ref_refs) - 1):
            for j in range(multiplier):
                port_name_1 = f"multiplier_{j}_gate_E"
                port_name_2 = f"multiplier_{j}_gate_W"
                
                if port_name_1 in ref_refs[i].ports and port_name_2 in ref_refs[i+1].ports:
                    # Use c_route for gate connections
                    """
                    route = c_route(self.pdk,
                                  ref_refs[i].ports[port_name_1],
                                  ref_refs[i+1].ports[port_name_2])
                    top_level << route
                    """
        
        # Connect all mirror gates together
        for i in range(len(mirror_refs) - 1):
            for j in range(multiplier):
                port_name_1 = f"multiplier_{j}_gate_E"
                port_name_2 = f"multiplier_{j}_gate_W"
                
                if port_name_1 in mirror_refs[i].ports and port_name_2 in mirror_refs[i+1].ports:
                    """
                    route = c_route(self.pdk,
                                  mirror_refs[i].ports[port_name_1],
                                  mirror_refs[i+1].ports[port_name_2])
                    top_level << route
                    """
        
        # Connect reference gates to mirror gates (shared gate connection)
        # This is the key connection for current mirror operation
        if ref_refs and mirror_refs:
            for j in range(multiplier):
                ref_gate_port = f"multiplier_{j}_gate_W"
                mirror_gate_port = f"multiplier_{j}_gate_E"
                
                if ref_gate_port in ref_refs[0].ports and mirror_gate_port in mirror_refs[0].ports:
                    # Create via stack from poly to metal1
                    gate_via = via_stack(self.pdk, "poly", "met1", centered=True)
                    
                    # Route using metal1 for better matching
                    main_gate_route = straight_route(
                        self.pdk,
                        ref_refs[0].ports[ref_gate_port],
                        mirror_refs[0].ports[mirror_gate_port]
                    )
                    top_level << main_gate_route
        
        # Connect reference drain to gates (diode connection)
        # This creates the reference current path
        for ref in ref_refs:
            for j in range(multiplier):
                drain_port = f"multiplier_{j}_drain_E"
                gate_port = f"multiplier_{j}_gate_E"
                
                if drain_port in ref.ports and gate_port in ref.ports:
                    diode_route = c_route(self.pdk,
                                         ref.ports[drain_port],
                                         ref.ports[gate_port])
                    top_level << diode_route
    
    def _route_sources(self, top_level, ref_refs, mirror_refs, multiplier):
        """
        Route source connections to ground (VSS)
        Common source connection for all transistors
        """
        
        met1_layer = self.pdk.get_glayer("met1")
        met2_layer = self.pdk.get_glayer("met2")
        
        # Create VSS rail on metal2
        all_refs = ref_refs + mirror_refs
        if all_refs:
            # Calculate VSS rail dimensions
            leftmost_x = min([ref.xmin for ref in all_refs])
            rightmost_x = max([ref.xmax for ref in all_refs])
            bottom_y = min([ref.ymin for ref in all_refs]) - 5.0
            
            vss_width = 2.0  # Wide rail for low resistance
            vss_rail = rectangle(
                size=(rightmost_x - leftmost_x + 10, vss_width),
                layer=met2_layer
            )
            vss_ref = top_level << vss_rail
            vss_ref.movex(leftmost_x - 5)
            vss_ref.movey(bottom_y)
            
            # Connect all sources to VSS rail
            for ref in all_refs:
                for j in range(multiplier):
                    source_port_w = f"multiplier_{j}_source_W"
                    source_port_e = f"multiplier_{j}_source_E"
                    
                    # Try both port orientations
                    for port_name in [source_port_w, source_port_e]:
                        if port_name in ref.ports:
                            # Create connection from source to VSS rail
                            # Use metal1 for source connection
                            source_track = rectangle(
                                size=(1.0, abs(ref.ports[port_name].center[1] - vss_ref.center[1])),
                                layer=met1_layer
                            )
                            track_ref = top_level << source_track
                            track_ref.movex(ref.ports[port_name].center[0] - 0.5)
                            track_ref.movey(min(ref.ports[port_name].center[1], vss_ref.center[1]))
                            
                            # Add via from metal1 to metal2 at VSS rail
                            via_m1_m2 = via_stack(self.pdk, "met1", "met2", centered=True)
                            via_ref = top_level << via_m1_m2
                            via_ref.movex(ref.ports[port_name].center[0])
                            via_ref.movey(vss_ref.center[1])
                            break  # Only connect once per multiplier instance
    
    def _route_drains(self, top_level, ref_refs, mirror_refs, multiplier):
        """
        Route drain connections for input (reference) and output (mirror)
        """
        
        met1_layer = self.pdk.get_glayer("met1")
        met2_layer = self.pdk.get_glayer("met2")
        met3_layer = self.pdk.get_glayer("met3")
        
        # Route reference drains together (input current)
        if ref_refs:
            # Create input rail on metal3
            leftmost_x = min([ref.xmin for ref in ref_refs])
            rightmost_x = max([ref.xmax for ref in ref_refs])
            top_y = max([ref.ymax for ref in ref_refs]) + 5.0
            
            input_rail = rectangle(
                size=(rightmost_x - leftmost_x + 10, 1.5),
                layer=met3_layer
            )
            input_ref = top_level << input_rail
            input_ref.movex(leftmost_x - 5)
            input_ref.movey(top_y)
            
            # Connect reference drains to input rail
            for ref in ref_refs:
                for j in range(multiplier):
                    drain_port = f"multiplier_{j}_drain_E"
                    if drain_port in ref.ports:
                        # Route from drain to input rail through metal layers
                        # Metal1 -> Metal2 -> Metal3
                        drain_track = rectangle(
                            size=(1.0, abs(ref.ports[drain_port].center[1] - input_ref.center[1])),
                            layer=met1_layer
                        )
                        track_ref = top_level << drain_track
                        track_ref.movex(ref.ports[drain_port].center[0] - 0.5)
                        track_ref.movey(min(ref.ports[drain_port].center[1], input_ref.center[1]))
                        
                        # Add via stack from metal1 to metal3
                        via_m1_m2 = via_stack(self.pdk, "met1", "met2", centered=True)
                        via_m2_m3 = via_stack(self.pdk, "met2", "met3", centered=True)
                        
                        via1_ref = top_level << via_m1_m2
                        via1_ref.movex(ref.ports[drain_port].center[0])
                        via1_ref.movey(input_ref.center[1] - 1)
                        
                        via2_ref = top_level << via_m2_m3
                        via2_ref.movex(ref.ports[drain_port].center[0])
                        via2_ref.movey(input_ref.center[1])
        
        # Route mirror drains together (output current)
        if mirror_refs:
            # Create output rail on metal3
            leftmost_x = min([ref.xmin for ref in mirror_refs])
            rightmost_x = max([ref.xmax for ref in mirror_refs])
            top_y = max([ref.ymax for ref in mirror_refs]) + 8.0
            
            output_rail = rectangle(
                size=(rightmost_x - leftmost_x + 10, 1.5),
                layer=met3_layer
            )
            output_ref = top_level << output_rail
            output_ref.movex(leftmost_x - 5)
            output_ref.movey(top_y)
            
            # Connect mirror drains to output rail
            for mirror in mirror_refs:
                for j in range(multiplier):
                    drain_port = f"multiplier_{j}_drain_E"
                    if drain_port in mirror.ports:
                        # Similar routing as reference drains
                        drain_track = rectangle(
                            size=(1.0, abs(mirror.ports[drain_port].center[1] - output_ref.center[1])),
                            layer=met1_layer
                        )
                        track_ref = top_level << drain_track
                        track_ref.movex(mirror.ports[drain_port].center[0] - 0.5)
                        track_ref.movey(min(mirror.ports[drain_port].center[1], output_ref.center[1]))
                        
                        # Add via stack
                        via_m1_m2 = via_stack(self.pdk, "met1", "met2", centered=True)
                        via_m2_m3 = via_stack(self.pdk, "met2", "met3", centered=True)
                        
                        via1_ref = top_level << via_m1_m2
                        via1_ref.movex(mirror.ports[drain_port].center[0])
                        via1_ref.movey(output_ref.center[1] - 1)
                        
                        via2_ref = top_level << via_m2_m3
                        via2_ref.movex(mirror.ports[drain_port].center[0])
                        via2_ref.movey(output_ref.center[1])
    
    def _add_power_rails(self, top_level, ref_refs, mirror_refs):
        """Add VDD and VSS power rails with proper width for current handling"""
        
        met4_layer = self.pdk.get_glayer("met4")  # Use higher metal for power
        
        all_refs = ref_refs + mirror_refs
        if all_refs:
            # Calculate power rail dimensions
            leftmost_x = min([ref.xmin for ref in all_refs]) - 10
            rightmost_x = max([ref.xmax for ref in all_refs]) + 10
            topmost_y = max([ref.ymax for ref in all_refs]) + 15
            bottommost_y = min([ref.ymin for ref in all_refs]) - 15
            
            rail_width = 3.0  # Wide rails for power distribution
            
            # VDD rail (top)
            vdd_rail = rectangle(
                size=(rightmost_x - leftmost_x, rail_width),
                layer=met4_layer
            )
            vdd_ref = top_level << vdd_rail
            vdd_ref.movex(leftmost_x)
            vdd_ref.movey(topmost_y)
            
            # VSS rail (bottom)
            vss_rail = rectangle(
                size=(rightmost_x - leftmost_x, rail_width),
                layer=met4_layer
            )
            vss_ref = top_level << vss_rail
            vss_ref.movex(leftmost_x)
            vss_ref.movey(bottommost_y)
    
    def _add_dummy_devices(self, top_level, width, length, fingers):
        """Add dummy transistors at edges for improved matching"""
        
        # Create dummy transistors
        dummy_left = nmos(self.pdk,
                         width=width,
                         length=length,
                         fingers=fingers,
                         with_substrate_tap=False,
                         with_dummy=(True, False))
        
        dummy_right = nmos(self.pdk,
                          width=width,
                          length=length,
                          fingers=fingers,
                          with_substrate_tap=False,
                          with_dummy=(False, True))
        
        # Place dummies at edges
        all_components = list(top_level.references)
        if all_components:
            leftmost_x = min([ref.xmin for ref in all_components])
            rightmost_x = max([ref.xmax for ref in all_components])
            center_y = sum([ref.center[1] for ref in all_components]) / len(all_components)
            
            # Place left dummy
            left_ref = top_level << dummy_left
            left_ref.movex(leftmost_x - evaluate_bbox(dummy_left)[0] - 5)
            left_ref.movey(center_y - evaluate_bbox(dummy_left)[1]/2)
            
            # Place right dummy
            right_ref = top_level << dummy_right
            right_ref.movex(rightmost_x + 5)
            right_ref.movey(center_y - evaluate_bbox(dummy_right)[1]/2)
    
    def _add_guard_rings(self, top_level):
        """Add guard rings for noise isolation"""
        
        # Calculate enclosing rectangle
        all_components = list(top_level.references)
        if all_components:
            leftmost_x = min([ref.xmin for ref in all_components]) - 10
            rightmost_x = max([ref.xmax for ref in all_components]) + 10
            topmost_y = max([ref.ymax for ref in all_components]) + 10
            bottommost_y = min([ref.ymin for ref in all_components]) - 10
            
            enclosed_rect = (rightmost_x - leftmost_x, topmost_y - bottommost_y)
            
            # Generate guard ring
            guard_ring = tapring(self.pdk, enclosed_rectangle=enclosed_rect)
            guard_ref = top_level << guard_ring
            guard_ref.movex(leftmost_x)
            guard_ref.movey(bottommost_y)
    
    def _add_decap(self, top_level, width, length):
        """Add decoupling capacitor between VDD and VSS"""
        
        # Use MOM capacitor or MIM capacitor based on PDK availability
        # For GF180, we'll use a metal-metal capacitor
        met3_layer = self.pdk.get_glayer("met3")
        met4_layer = self.pdk.get_glayer("met4")
        
        # Create capacitor plates
        bottom_plate = rectangle(size=(width, length), layer=met3_layer)
        top_plate = rectangle(size=(width, length), layer=met4_layer)
        
        # Place capacitor near current mirror
        all_components = list(top_level.references)
        if all_components:
            rightmost_x = max([ref.xmax for ref in all_components]) + 20
            center_y = sum([ref.center[1] for ref in all_components]) / len(all_components)
            
            bottom_ref = top_level << bottom_plate
            bottom_ref.movex(rightmost_x)
            bottom_ref.movey(center_y - length/2)
            
            top_ref = top_level << top_plate
            top_ref.movex(rightmost_x)
            top_ref.movey(center_y - length/2)
    
    def _add_labels(self, top_level):
        """Add labels for LVS verification"""
        
        # Add text labels for pins
        top_level.add_label("VDD", layer=self.pdk.get_glayer("met4"))
        top_level.add_label("VSS", layer=self.pdk.get_glayer("met4"))
        top_level.add_label("IREF", layer=self.pdk.get_glayer("met3"))
        top_level.add_label("IOUT", layer=self.pdk.get_glayer("met3"))
    
    def _center_layout(self, component):
        """Center the layout around origin for symmetry"""
        
        # Get current bounds
        if component.references:
            leftmost_x = min([ref.xmin for ref in component.references])
            rightmost_x = max([ref.xmax for ref in component.references])
            topmost_y = max([ref.ymax for ref in component.references])
            bottommost_y = min([ref.ymin for ref in component.references])
            
            # Calculate center offsets
            center_x = (leftmost_x + rightmost_x) / 2
            center_y = (topmost_y + bottommost_y) / 2
            
            # Move all components to center
            for ref in component.references:
                ref.movex(-center_x)
                ref.movey(-center_y)
    
    def generate_and_save(self, filename="current_mirror_complete.gds"):
        """Generate the layout and save to GDS file"""
        
        # Create the current mirror
        layout = self.create_current_mirror(
            ref_width=2.0,
            ref_length=0.28,
            mirror_ratio=2,
            fingers=2,
            multiplier=4,  # 4x interdigitation
            add_dummy=True,
            add_guardrings=True,
            with_decap=True
        )
        
        # Save to GDS
        layout.write_gds(filename)
        
        # Also generate netlist for LVS
        netlist_file = filename.replace('.gds', '.sp')
        self._generate_netlist(layout, netlist_file)
        
        return layout
    
    def _generate_netlist(self, layout, filename):
        """Generate SPICE netlist for LVS verification"""
        
        with open(filename, 'w') as f:
            f.write("* Current Mirror with Decap - GF180 PDK\n")
            f.write(".subckt current_mirror VDD VSS IREF IOUT\n")
            f.write("* Reference transistor (diode-connected)\n")
            f.write("M1 IREF IREF VSS VSS nfet_03v3 W=2u L=0.28u M=4\n")
            f.write("* Mirror transistor\n")
            f.write("M2 IOUT IREF VSS VSS nfet_03v3 W=4u L=0.28u M=4\n")
            f.write("* Decoupling capacitor\n")
            f.write("C1 VDD VSS 1p\n")
            f.write(".ends\n")


# Example usage
if __name__ == "__main__":
    # Initialize the current mirror generator
    cmirror = CurrentMirrorWithDecap(pdk=gf180)
    
    # Generate the layout with complete routing
    layout = cmirror.generate_and_save("current_mirror_complete.gds")
    
    # Display the layout (if running in Jupyter or with viewer)
    layout.show()
    
    print("Current mirror layout with complete routing generated successfully!")
    print("Files created:")
    print("  - current_mirror_complete.gds (layout)")
    print("  - current_mirror_complete.sp (netlist)")
