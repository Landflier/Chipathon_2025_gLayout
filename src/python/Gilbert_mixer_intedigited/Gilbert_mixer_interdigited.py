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
from glayout import nmos, pmos, tapring
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
from diff_pair import swap_drain_source_ports, get_pin_layers


@dataclass
class LOFETConfig:
    """Configuration for LO differential pair FETs"""
    sd_rmult: int = 1
    sd_route_topmet: str = "met2"
    sdlayer: str = "n+s/d"
    routing: bool = True
    inter_finger_topmet: str = "met1"
    gate_route_topmet: str = "met2"
    gate_rmult: int = 1
    interfinger_rmult: int = 1
    sd_route_extension: float = 0.0
    gate_route_extension: float = 0.0
    tie_layers: Tuple[str, str] = ("met2", "met1")
    with_dummies: bool = False


@dataclass
class RFFETConfig:
    """Configuration for RF differential pair FETs"""
    with_dnwell: bool = False
    sd_route_topmet: str = "met2"
    gate_route_topmet: str = "met2"
    sd_rmult: int = 1
    gate_rmult: int = 1
    interfinger_rmult: int = 1
    tie_layers: Tuple[str, str] = ("met2", "met1")
    inter_finger_topmet: str = "met1"
    with_dummies: bool = True
    with_tie: bool = True
    with_substrate_tap: bool = False


class GilbertMixerInterdigited:
    """
    Class for creating interdigited Gilbert cell mixer layouts.
    
    This class encapsulates all functionality for generating an interdigited
    Gilbert cell mixer with LO and RF differential pairs.
    """
    
    def __init__(
        self,
        pdk: MappedPDK,
        lo_width: float,
        lo_fingers: int,
        rf_width: float,
        rf_fingers: int,
        lo_length: Optional[float] = None,
        rf_length: Optional[float] = None,
        lo_fet_config: Optional[LOFETConfig] = None,
        rf_fet_config: Optional[RFFETConfig] = None,
        extra_port_vias_x_displacement: float = 0,
        component_name: str = "Gilbert_mixer_interdigited"
    ):
        """
        Initialize the Gilbert mixer with configuration parameters.
        
        Args:
            pdk: PDK for design rules and layer information
            lo_width: Width of LO transistors
            lo_fingers: Number of fingers for LO transistors
            rf_width: Width of RF transistors
            rf_fingers: Number of fingers for RF transistors
            lo_length: Length of LO transistors (uses PDK minimum if None)
            rf_length: Length of RF transistors (uses PDK minimum if None)
            lo_fet_config: Configuration for LO FETs
            rf_fet_config: Configuration for RF FETs
            extra_port_vias_x_displacement: Extra displacement for port vias
            component_name: Name for the top-level component
        """
        self.pdk = pdk
        self.pdk.activate()
        
        # Transistor dimensions
        self.lo_width = lo_width
        self.lo_fingers = lo_fingers
        self.rf_width = rf_width
        self.rf_fingers = rf_fingers
        
        # Use PDK minimum lengths if not specified
        min_length = pdk.get_grule('poly')['min_width']
        self.lo_length = lo_length if lo_length is not None else min_length
        self.rf_length = rf_length if rf_length is not None else min_length
        
        # FET configurations
        self.lo_fet_config = lo_fet_config or LOFETConfig()
        self.rf_fet_config = rf_fet_config or RFFETConfig()
        
        # Other parameters
        self.extra_port_vias_x_displacement = extra_port_vias_x_displacement
        self.component_name = component_name
        
        # Component references (populated during build)
        self.top_level: Optional[Component] = None
        self.lo_diff_pairs_ref: Optional[Component] = None
        self.rf_diff_pair_ref: Optional[Component] = None
        
        # Validate inputs
        self._validate_inputs()
    
    def _validate_inputs(self) -> None:
        """Validate input parameters."""
        if self.lo_width % self.lo_fingers != 0:
            raise ValueError(f"LO width ({self.lo_width}) must be a multiple of fingers ({self.lo_fingers})")
        
        if self.rf_width % self.rf_fingers != 0:
            raise ValueError(f"RF width ({self.rf_width}) must be a multiple of fingers ({self.rf_fingers})")
        
        if self.lo_fet_config.sd_rmult < 1 or self.lo_fet_config.interfinger_rmult < 1 or self.lo_fet_config.gate_rmult < 1:
            raise ValueError("LO routing multipliers must be positive integers")
        
        if self.rf_fet_config.sd_rmult < 1 or self.rf_fet_config.interfinger_rmult < 1 or self.rf_fet_config.gate_rmult < 1:
            raise ValueError("RF routing multipliers must be positive integers")
        
        if "+s/d" not in self.lo_fet_config.sdlayer:
            raise ValueError("Specify + doped region for LO multiplier")
    
    def _create_finger_array(
        self,
        width: float,
        fingers: int,
        length: float,
        fets: int,
        sdlayer: str,
        sd_route_topmet: str,
        interfinger_rmult: int,
        sd_rmult: int,
        gate_rmult: int,
        with_dummies: bool,
    ) -> Component:
        """
        Create a finger array with extra edge gates.
        
        This is a private method that creates the base finger array structure
        used by both LO and RF differential pairs.
        """
        # Calculate finger dimensions
        finger_width = width / fingers
        poly_height = finger_width + 2 * self.pdk.get_grule("poly", "active_diff")["overhang"]
        
        # Snap dimensions to grid
        length = self.pdk.snap_to_2xgrid(length)
        finger_width = self.pdk.snap_to_2xgrid(finger_width)
        poly_height = self.pdk.snap_to_2xgrid(poly_height)
        
        # Calculate poly spacing
        sd_viaxdim = interfinger_rmult * evaluate_bbox(via_stack(self.pdk, "active_diff", "met1"))[0]
        poly_spacing = 2 * self.pdk.get_grule("poly", "mcon")["min_separation"] + self.pdk.get_grule("mcon")["width"]
        poly_spacing = max(sd_viaxdim, poly_spacing)
        met1_minsep = self.pdk.get_grule("met1")["min_separation"]
        poly_spacing += met1_minsep if length < met1_minsep else 0
        
        # Create single finger
        finger = Component("finger")
        gate = finger << rectangle(size=(length, poly_height), layer=self.pdk.get_glayer("poly"), centered=True)
        sd_viaarr = via_array(self.pdk, "active_diff", "met1", size=(sd_viaxdim, finger_width), minus1=True, lay_bottom=False).copy()
        interfinger_correction = via_array(self.pdk, "met1", sd_route_topmet, size=(None, finger_width), lay_every_layer=True, num_vias=(1, None))
        sd_viaarr << interfinger_correction
        sd_viaarr_ref = finger << sd_viaarr
        sd_viaarr_ref.movex((poly_spacing + length) / 2)
        finger.add_ports(gate.get_ports_list(), prefix="gate_")
        finger.add_ports(sd_viaarr_ref.get_ports_list(), prefix="rightsd_")
        
        # Create finger array
        fingerarray = prec_array(finger, columns=fets*fingers, rows=1, spacing=(poly_spacing + length, 1), absolute_spacing=True)
        sd_via_ref_left = fingerarray << sd_viaarr
        sd_via_ref_left.movex(0 - (poly_spacing + length) / 2)
        fingerarray.add_ports(sd_via_ref_left.get_ports_list(), prefix="leftsd_")
        
        # Center finger array
        centered_farray = Component()
        fingerarray_ref_center = prec_ref_center(fingerarray)
        centered_farray.add(fingerarray_ref_center)
        centered_farray.add_ports(fingerarray_ref_center.get_ports_list())
        
        if with_dummies:
            # Add dummy gates at edges
            spacing = poly_spacing + length
            num_fingers = fets * fingers
            leftmost_finger_center = -(num_fingers - 1) * spacing / 2
            rightmost_finger_center = (num_fingers - 1) * spacing / 2
            
            left_dummy_gate = centered_farray << rectangle(
                size=(length, poly_height), 
                layer=self.pdk.get_glayer("poly"), 
                centered=True
            )
            left_dummy_gate.movex(leftmost_finger_center - spacing)
            
            right_dummy_gate = centered_farray << rectangle(
                size=(length, poly_height), 
                layer=self.pdk.get_glayer("poly"), 
                centered=True
            )
            right_dummy_gate.movex(rightmost_finger_center + spacing)
            
            centered_farray.add_ports(left_dummy_gate.get_ports_list(), prefix="dummy_gate_L_")
            centered_farray.add_ports(right_dummy_gate.get_ports_list(), prefix="dummy_gate_R_")
        
        # Create diffusion and doped region
        multiplier = rename_ports_by_orientation(centered_farray)
        diff_extra_enc = 2 * self.pdk.get_grule("mcon", "active_diff")["min_enclosure"]
        diff_dims = (diff_extra_enc + evaluate_bbox(multiplier)[0], finger_width)
        diff = multiplier << rectangle(size=diff_dims, layer=self.pdk.get_glayer("active_diff"), centered=True)
        
        sd_diff_ovhg = self.pdk.get_grule("n+s/d", "active_diff")["min_enclosure"]
        sdlayer_dims = [dim + 2 * sd_diff_ovhg for dim in diff_dims]
        sdlayer_ref = multiplier << rectangle(size=sdlayer_dims, layer=self.pdk.get_glayer("n+s/d"), centered=True)
        
        multiplier.add_ports(sdlayer_ref.get_ports_list(), prefix="plusdoped_")
        multiplier.add_ports(diff.get_ports_list(), prefix="diff_")
        
        return multiplier
    
    def _add_source_drain_gate_routing(
        self,
        multiplier: Component,
        fingers: int,
        width: float,
        sd_rmult: int,
        sd_route_topmet: str,
        sd_route_extension: float,
        gate_route_topmet: str,
        gate_rmult: int,
        gate_route_extension: float,
        interfinger_rmult: int,
    ) -> None:
       """Add vertical source/drain and gate routing to the multiplier component. I.e place ports above each finger or s/d region and route them

       ports (one port for each edge),
       --- LO_2_gate_Lo_b ---
       --- LO_2_source    --- * extends to the right 
       --- LO_2_drain     --- * extends to the left
       --- finger array  ---
       --- LO_1_drain    --- * extends to the left
       --- LO_1_source   --- * extends to the right
       --- LO_1_gate_Lo  ---

       (dA sB dD sC)*fingers_d
       """
        # Count SD rows
        number_sd_rows = 0
        for port_name in multiplier.ports.keys():
            if port_name.startswith("leftsd_array") and "_col" in port_name:
                row_part = port_name.split("_")[2]
                row_num = int(row_part.replace("row", ""))
                number_sd_rows = max(number_sd_rows, row_num)
        
        # Place vias and route
        sdvia = via_stack(self.pdk, "met1", sd_route_topmet)
        sdmet_height = sd_rmult * evaluate_bbox(sdvia)[1]
        sdroute_minsep = self.pdk.get_grule(sd_route_topmet)["min_separation"]
        sdvia_ports = []
        
        # Route fingers
        for finger in range(4*fingers+1):
            # Determine port assignments
            check_port_1 = (finger % 4 == 1)
            check_port_2 = (finger % 4 == 3)
            check_port_3 = (finger % 4 == 0)
            check_port_4 = (finger % 4 == 2)
            
            # Configure routing based on port type
            if check_port_1:
                aligning_port_name = f"row0_col{finger-1}_rightsd_array_row0_col0_top_met_N"
                rel_align_port = multiplier.ports[aligning_port_name]
                y_align_via = -width/2
                alignment_port = ('c', 'b')
                sdvia_extension = -(sdroute_minsep + sdroute_minsep + (sdmet_height/2 + sdmet_height))
                sd_route_extension_temp = -self.pdk.snap_to_2xgrid(sd_route_extension)
            elif check_port_2:
                aligning_port_name = f"row0_col{finger-1}_rightsd_array_row0_col0_top_met_N"
                rel_align_port = multiplier.ports[aligning_port_name]
                y_align_via = -width/2
                alignment_port = ('c', 'b')
                sdvia_extension = -(sdroute_minsep + (sdmet_height)/2)
                sd_route_extension_temp = -self.pdk.snap_to_2xgrid(sd_route_extension)
            elif check_port_3:
                if finger != 0:
                    aligning_port_name = f"row0_col{finger-1}_rightsd_array_row{number_sd_rows}_col0_top_met_N"
                    rel_align_port = multiplier.ports[aligning_port_name]
                else:
                    aligning_port_name = f"leftsd_top_met_N"
                    rel_align_port = multiplier.ports[aligning_port_name]
                    rel_align_port.width = rel_align_port.width / interfinger_rmult
                y_align_via = width/2
                alignment_port = ('c', 't')
                sdvia_extension = +(sdroute_minsep + (sdmet_height)/2)
                sd_route_extension_temp = self.pdk.snap_to_2xgrid(sd_route_extension)
            elif check_port_4:
                aligning_port_name = f"row0_col{finger-1}_rightsd_array_row{number_sd_rows}_col0_top_met_N"
                rel_align_port = multiplier.ports[aligning_port_name]
                y_align_via = width/2
                alignment_port = ('c', 't')
                sdvia_extension = +(sdroute_minsep + sdroute_minsep + (sdmet_height/2 + sdmet_height))
                sd_route_extension_temp = self.pdk.snap_to_2xgrid(sd_route_extension)
            
            # Create diffusion port
            diff_top_port = multiplier.add_port(
                center=(rel_align_port.center[0], y_align_via),
                width=rel_align_port.width,
                orientation=90,
                layer=rel_align_port.layer,
                name=f"diffusion_port_to_align_sd_{finger}"
            )
            
            # Route SD connections
            sd_track_y_displacement = sdvia_extension + sd_route_extension_temp
            sdvia_ref = align_comp_to_port(sdvia, diff_top_port, alignment=alignment_port)
            multiplier.add(sdvia_ref.movey(sd_track_y_displacement))
            multiplier << straight_route(self.pdk, diff_top_port, sdvia_ref.ports["bottom_met_N"])
            sdvia_ports += [sdvia_ref.ports["top_met_W"], sdvia_ref.ports["top_met_E"]]
            
            if finger == 4*fingers:
                break
            
            # Gate routing
            check_gate_LO = (finger % 2 == 0)
            check_gate_LO_b = (finger % 2 == 1)
            
            if check_gate_LO:
                aligning_gate_port_name = f"row0_col{finger}_gate_S"
                rel_gate_aligning_port = multiplier.ports[aligning_gate_port_name]
                gate_extension = -(3 * sdroute_minsep + 5/2 * sdmet_height + sd_route_extension + gate_route_extension)
                y_align_via = -width/2 + gate_extension
            elif check_gate_LO_b:
                aligning_gate_port_name = f"row0_col{finger}_gate_N"
                rel_gate_aligning_port = multiplier.ports[aligning_gate_port_name]
                gate_extension = 3 * sdroute_minsep + 5/2 * sdmet_height + sd_route_extension + gate_route_extension
                y_align_via = width/2 + gate_extension
            
            # Route gates vertically
            psuedo_Ngateroute = multiplier.add_port(
                center=(rel_gate_aligning_port.center[0], y_align_via),
                width=rel_gate_aligning_port.width,
                orientation=90,
                layer=rel_gate_aligning_port.layer,
                name=f"gate_port_vroute_{finger}"
            )
            psuedo_Ngateroute.y = self.pdk.snap_to_2xgrid(psuedo_Ngateroute.y)
            multiplier << straight_route(self.pdk, rel_gate_aligning_port, psuedo_Ngateroute)
        
        # Place horizontal gate routes
        gate_width = multiplier.ports[f"gate_port_vroute_{4*fingers-2}"].center[0] - multiplier.ports["gate_port_vroute_0"].center[0] + rel_gate_aligning_port.width
        gate_route = rename_ports_by_list(
            via_array(self.pdk, "poly", gate_route_topmet, size=(gate_width, None), num_vias=(None, gate_rmult), no_exception=True, fullbottom=True),
            [("top_met_", "gate_top_")]
        )
        
        # North and South gates
        gate_LO_b_ref = align_comp_to_port(gate_route.copy(), multiplier.ports[f"gate_port_vroute_{4*fingers-1}"], alignment=('l', 't'), layer=self.pdk.get_glayer("poly"))
        gate_LO_ref = align_comp_to_port(gate_route.copy(), multiplier.ports[f"gate_port_vroute_{4*fingers-2}"], alignment=('l', 'b'), layer=self.pdk.get_glayer("poly"))
        multiplier.add(gate_LO_b_ref)
        multiplier.add(gate_LO_ref)
        
        multiplier.add_ports(gate_LO_ref.get_ports_list(), prefix="LO_")
        multiplier.add_ports(gate_LO_b_ref.get_ports_list(), prefix="LO_b_")
        
        # Get unique y-coordinates for SD ports
        y_coords = [port.center[1] for port in sdvia_ports]
        unique_y_coords = list(set(y_coords))
        unique_y_coords.sort()
        
        y_coord_indices = []
        for unique_y in unique_y_coords:
            first_index = next(i for i, y in enumerate(y_coords) if y == unique_y)
            y_coord_indices.append(first_index)
        
        # Place SD route metal
        port_1_sd_index = y_coord_indices[0]
        port_2_sd_index = y_coord_indices[1]
        port_3_sd_index = y_coord_indices[2]
        port_4_sd_index = y_coord_indices[3]
        
        sd_width = sdvia_ports[-1].center[0] - sdvia_ports[0].center[0]
        sd_route = rectangle(size=(sd_width, sdmet_height), layer=self.pdk.get_glayer(sd_route_topmet), centered=True)
        
        # Update port widths
        sdvia_ports[port_1_sd_index].width = sdmet_height
        sdvia_ports[port_2_sd_index].width = sdmet_height
        sdvia_ports[port_3_sd_index].width = sdmet_height
        sdvia_ports[port_4_sd_index].width = sdmet_height
        
        # Add SD routes
        port_1_sd_route = align_comp_to_port(sd_route.copy(), sdvia_ports[port_1_sd_index], alignment=(None, 'c'))
        port_2_sd_route = align_comp_to_port(sd_route.copy(), sdvia_ports[port_2_sd_index], alignment=(None, 'c'))
        port_3_sd_route = align_comp_to_port(sd_route.copy(), sdvia_ports[port_3_sd_index], alignment=(None, 'c'))
        port_4_sd_route = align_comp_to_port(sd_route.copy(), sdvia_ports[port_4_sd_index], alignment=(None, 'c'))
        
        multiplier.add(port_1_sd_route)
        multiplier.add(port_2_sd_route)
        multiplier.add(port_3_sd_route)
        multiplier.add(port_4_sd_route)
        
        # Add ports
        multiplier.add_ports(port_1_sd_route.get_ports_list(), prefix="port_1_")
        multiplier.add_ports(port_2_sd_route.get_ports_list(), prefix="port_2_")
        multiplier.add_ports(port_3_sd_route.get_ports_list(), prefix="port_3_")
        multiplier.add_ports(port_4_sd_route.get_ports_list(), prefix="port_4_")
    
    def _add_pin_and_label_to_via(
        self,
        comp: Component,
        via_ref: Component,
        pin_name: str,
        debug_mode: bool = False,
    ) -> Component:
        """Add a pin and label to an existing via."""
        comp.unlock()
        
        # Get via center and size
        via_center = via_ref.center
        via_size = via_ref.size
        pin_size = max(via_size[0], via_size[1])
        
        # Find top metal port
        top_met_ports = [port for port_name, port in via_ref.ports.items() if "top_met" in port_name]
        
        if not top_met_ports:
            print(f"⚠ Warning: No top_met ports found in via for {pin_name}")
            return comp
        
        top_met_port = top_met_ports[0]
        metal_layer = top_met_port.layer
        
        # Get pin and label layers
        pin_layer_gds, label_layer_gds = get_pin_layers(metal_layer, self.pdk)
        
        # Add label
        comp.add_label(text=pin_name, position=via_center, layer=label_layer_gds)
        
        if debug_mode:
            pin_rect = rectangle(layer=pin_layer_gds, size=(pin_size, pin_size), centered=True).copy()
            pin_rect_ref = comp << pin_rect
            pin_rect_ref.move(via_center)
        
        # Add electrical ports
        comp.add_port(center=via_center, width=pin_size, orientation=0, layer=metal_layer, name=f"{pin_name}_E")
        comp.add_port(center=via_center, width=pin_size, orientation=90, layer=metal_layer, name=f"{pin_name}_N")
        comp.add_port(center=via_center, width=pin_size, orientation=180, layer=metal_layer, name=f"{pin_name}_W")
        comp.add_port(center=via_center, width=pin_size, orientation=270, layer=metal_layer, name=f"{pin_name}_S")
        
        return comp
    
    def create_LO_diff_pairs(self, tie: bool = True) -> Component:
        """Create interdigited LO differential pairs."""
        config = self.lo_fet_config
        
        # Create finger array
        multiplier = self._create_finger_array(
            width=self.lo_width,
            fingers=self.lo_fingers,
            length=self.lo_length,
            fets=4,
            sdlayer=config.sdlayer,
            sd_route_topmet=config.sd_route_topmet,
            interfinger_rmult=config.interfinger_rmult,
            sd_rmult=config.sd_rmult,
            gate_rmult=config.gate_rmult,
            with_dummies=config.with_dummies
        )
        
        # Snap dimensions
        min_width = self.pdk.get_grule("poly")["min_width"]
        min_width = max(min_width, self.pdk.get_grule("active_diff")["min_width"])
        width = self.pdk.snap_to_2xgrid(self.lo_width/self.lo_fingers)
        
        multiplier = component_snap_to_grid(rename_ports_by_orientation(multiplier))
        
        # Add routing
        if config.routing:
            self._add_source_drain_gate_routing(
                multiplier, self.lo_fingers, width,
                config.sd_rmult, config.sd_route_topmet, config.sd_route_extension,
                config.gate_route_topmet, config.gate_rmult, config.gate_route_extension,
                config.interfinger_rmult
            )
        
        # Add tap ring if requested
        if tie:
            tap_separation = max(
                self.pdk.get_grule("met2")["min_separation"],
                self.pdk.get_grule("met1")["min_separation"],
                self.pdk.get_grule("active_diff", "active_tap")["min_separation"],
            )
            tap_separation += self.pdk.get_grule("p+s/d", "active_tap")["min_enclosure"]
            tap_encloses = (
                2 * (tap_separation + multiplier.xmax),
                2 * (tap_separation + multiplier.ymax),
            )
            tiering_ref = multiplier << tapring(
                self.pdk,
                enclosed_rectangle=tap_encloses,
                sdlayer="p+s/d",
                horizontal_glayer=config.tie_layers[0],
                vertical_glayer=config.tie_layers[1],
            )
            multiplier.add_ports(tiering_ref.get_ports_list(), prefix="tie_")
        
        # Add pwell
        multiplier.add_padding(
            layers=(self.pdk.get_glayer("pwell"),),
            default=self.pdk.get_grule("pwell", "active_tap")["min_enclosure"],
        )
        multiplier = add_ports_perimeter(multiplier, layer=self.pdk.get_glayer("pwell"), prefix="well_")
        
        # Route dummies if present
        if config.with_dummies:
            multiplier << straight_route(
                self.pdk,
                multiplier.ports["dummy_gate_L_W"],
                multiplier.ports["tie_W_bottom_lay_E"],
                glayer1="poly",
                glayer2="met1",
            )
            multiplier << straight_route(
                self.pdk,
                multiplier.ports["dummy_gate_R_E"],
                multiplier.ports["tie_E_bottom_lay_W"],
                glayer1="poly",
                glayer2="met1",
            )
        
        # Finalize component
        lo_diff_pairs = component_snap_to_grid(rename_ports_by_orientation(multiplier))
        lo_diff_pairs.name = "LO_diff_pairs_interdigitized"
        lo_diff_pairs.add_ports(lo_diff_pairs.get_ports_list(), prefix="LO_")
        
        return lo_diff_pairs
    
    def create_RF_diff_pair(self) -> Component:
        """Create RF differential pair."""
        config = self.rf_fet_config
        
        # Create top level component
        top_level = Component()
        
        # Create two FETs
        fet_params = {
            "width": self.rf_width,
            "fingers": self.rf_fingers,
            "multipliers": 1,
            "with_tie": config.with_tie,
            "with_dummy": config.with_dummies,
            "with_dnwell": config.with_dnwell,
            "with_substrate_tap": config.with_substrate_tap,
            "length": self.rf_length,
            "sd_rmult": config.sd_rmult,
            "sd_route_topmet": config.sd_route_topmet,
            "gate_route_topmet": config.gate_route_topmet,
            "gate_rmult": config.gate_rmult,
            "interfinger_rmult": config.interfinger_rmult,
            "tie_layers": config.tie_layers,
        }
        
        M1_temp = nmos(self.pdk, **fet_params)
        M2_temp = nmos(self.pdk, **fet_params)
        
        # Swap drain and source of M1
        M1 = swap_drain_source_ports(M1_temp)
        M2 = M2_temp
        
        # Place transistors
        M1_ref = top_level << M1
        M2_ref = top_level << M2
        
        M2_ref.mirror_x()
        M2_ref.movex(M1_ref.xmax + evaluate_bbox(M2)[0]/2)
        
        # Add ports
        top_level.add_ports(M1_ref.get_ports_list(), prefix="RF_M1_")
        top_level.add_ports(M2_ref.get_ports_list(), prefix="RF_M2_")
        
        top_level.name = "RF_diff_pair"
        
        return component_snap_to_grid(top_level)
    
    def _create_LO_vias_outside_tapring_and_route(self) -> Tuple:
        """Create vias for routing LO pairs outside the tapring."""
        comp = self.top_level
        LO_diff_pairs_ref = self.lo_diff_pairs_ref
        
        # Get ports
        port_1 = LO_diff_pairs_ref.ports["port_1_W"]
        port_2 = LO_diff_pairs_ref.ports["port_2_E"]
        port_3 = LO_diff_pairs_ref.ports["port_3_W"]
        port_4 = LO_diff_pairs_ref.ports["port_4_E"]
        
        via_width = port_1.width
        
        # Create vias
        via_params = {
            "size": (via_width, via_width),
            "fullbottom": True
        }
        
        via_port_1 = via_array(self.pdk, "met3", "met2", **via_params)
        via_port_2 = via_array(self.pdk, "met3", "met2", **via_params)
        via_port_3 = via_array(self.pdk, "met3", "met2", **via_params)
        via_port_4 = via_array(self.pdk, "met3", "met2", **via_params)
        
        # Place vias
        via_port_1_ref = comp << via_port_1
        via_port_2_ref = comp << via_port_2
        via_port_3_ref = comp << via_port_3
        via_port_4_ref = comp << via_port_4
        
        # Align vias
        align_comp_to_port(via_port_1_ref, port_1, alignment=('c', 'c'))
        align_comp_to_port(via_port_2_ref, port_2, alignment=('c', 'c'))
        align_comp_to_port(via_port_3_ref, port_3, alignment=('c', 'c'))
        align_comp_to_port(via_port_4_ref, port_4, alignment=('c', 'c'))
        
        # Calculate displacements
        port_1_x_displacement = 1.5*(LO_diff_pairs_ref.ports["tie_W_bottom_lay_W"].center[0] - port_1.center[0]) - port_1.width - self.extra_port_vias_x_displacement
        port_2_x_displacement = 1.5*(LO_diff_pairs_ref.ports["tie_E_bottom_lay_E"].center[0] - port_2.center[0]) + port_2.width + self.extra_port_vias_x_displacement
        port_3_x_displacement = 2.5*(LO_diff_pairs_ref.ports["tie_W_bottom_lay_W"].center[0] - port_3.center[0]) - port_3.width - self.extra_port_vias_x_displacement
        port_4_x_displacement = 2.5*(LO_diff_pairs_ref.ports["tie_E_bottom_lay_E"].center[0] - port_4.center[0]) + port_4.width + self.extra_port_vias_x_displacement
        
        # Snap to grid and move
        port_1_x_displacement = self.pdk.snap_to_2xgrid(port_1_x_displacement)
        port_2_x_displacement = self.pdk.snap_to_2xgrid(port_2_x_displacement)
        port_3_x_displacement = self.pdk.snap_to_2xgrid(port_3_x_displacement)
        port_4_x_displacement = self.pdk.snap_to_2xgrid(port_4_x_displacement)
        
        via_port_1_ref.movex(port_1_x_displacement)
        via_port_2_ref.movex(port_2_x_displacement)
        via_port_3_ref.movex(port_3_x_displacement)
        via_port_4_ref.movex(port_4_x_displacement)
        
        # Route to vias
        comp << straight_route(self.pdk, port_1, via_port_1_ref["bottom_lay_E"])
        comp << straight_route(self.pdk, port_2, via_port_2_ref["bottom_lay_E"])
        comp << straight_route(self.pdk, port_3, via_port_3_ref["bottom_lay_E"])
        comp << straight_route(self.pdk, port_4, via_port_4_ref["bottom_lay_E"])
        
        # Create and route gate vias
        port_LO = LO_diff_pairs_ref.ports["LO_bottom_lay_W"]
        port_LO_b = LO_diff_pairs_ref.ports["LO_b_bottom_lay_E"]
        
        via_width = port_LO.width
        
        via_port_LO = via_array(self.pdk, "met3", "met2", size=(via_width, via_width), fullbottom=True)
        via_port_LO_b = via_array(self.pdk, "met3", "met2", size=(via_width, via_width), fullbottom=True)
        
        via_port_LO_ref = comp << via_port_LO
        via_port_LO_b_ref = comp << via_port_LO_b
        
        align_comp_to_port(via_port_LO_ref, port_LO, alignment=('c', 'c'))
        align_comp_to_port(via_port_LO_b_ref, port_LO_b, alignment=('c', 'c'))
        
        via_LO_x_displacement = port_3_x_displacement - 2*port_LO.width
        via_LO_b_x_displacement = port_4_x_displacement + 2*port_LO_b.width
        
        via_LO_x_displacement = self.pdk.snap_to_2xgrid(via_LO_x_displacement)
        via_LO_b_x_displacement = self.pdk.snap_to_2xgrid(via_LO_b_x_displacement)
        
        via_port_LO_ref.movex(via_LO_x_displacement)
        via_port_LO_b_ref.movex(via_LO_b_x_displacement)
        
        comp << straight_route(
            self.pdk, port_LO, via_port_LO_ref["bottom_lay_W"],
            glayer1="met2", via1_alignment=('c', 'c'), via2_alignment=('c', 'c')
        )
        comp << straight_route(
            self.pdk, port_LO_b, via_port_LO_b_ref["bottom_lay_W"],
            glayer1="met2", via1_alignment=('c', 'c'), via2_alignment=('c', 'c')
        )
        
        return via_port_LO_ref, via_port_LO_b_ref, via_port_1_ref, via_port_2_ref, via_port_3_ref, via_port_4_ref
    
    def _create_RF_vias_outside_tapring_and_route(self) -> Tuple:
        """Create vias for routing RF pairs outside the tapring."""
        comp = self.top_level
        RF_diff_pair_ref = self.rf_diff_pair_ref
        
        # Get ports
        RF_gate = RF_diff_pair_ref.ports["RF_M1_multiplier_0_gate_S"]
        RF_b_gate = RF_diff_pair_ref.ports["RF_M2_multiplier_0_gate_S"]
        M1_source = RF_diff_pair_ref.ports["RF_M1_source_W"]
        M2_source = RF_diff_pair_ref.ports["RF_M2_source_W"]
        
        gate_via_width = abs(RF_diff_pair_ref.ports["RF_M1_gate_E"].center[1] - RF_diff_pair_ref.ports["RF_M1_gate_W"].center[1]) + RF_gate.width
        source_via_width = M1_source.width
        
        # Create vias
        via_RF_gate = via_array(self.pdk, "met3", "met2", size=(gate_via_width, gate_via_width), fullbottom=True)
        via_RF_b_gate = via_array(self.pdk, "met3", "met2", size=(gate_via_width, gate_via_width), fullbottom=True)
        via_M1_source = via_array(self.pdk, "met3", "met2", size=(source_via_width, source_via_width), fullbottom=True)
        via_M2_source = via_array(self.pdk, "met3", "met2", size=(source_via_width, source_via_width), fullbottom=True)
        
        # Place vias
        via_RF_gate_ref = comp << via_RF_gate
        via_RF_b_gate_ref = comp << via_RF_b_gate
        via_M1_source_ref = comp << via_M1_source
        via_M2_source_ref = comp << via_M2_source
        
        # Align vias
        align_comp_to_port(via_RF_gate_ref, RF_gate, alignment=('c', 'b'))
        align_comp_to_port(via_RF_b_gate_ref, RF_b_gate, alignment=('c', 'b'))
        align_comp_to_port(via_M1_source_ref, M1_source, alignment=('c', 'c'))
        align_comp_to_port(via_M2_source_ref, M2_source, alignment=('c', 'c'))
        
        # Move vias outside tapring
        via_M1_source_ref.movex(-abs(RF_diff_pair_ref.ports["RF_M1_source_W"].center[0] - RF_diff_pair_ref.ports["RF_M1_tie_W_bottom_lay_W"].center[0]) - source_via_width)
        via_M2_source_ref.movex(abs(RF_diff_pair_ref.ports["RF_M2_source_W"].center[0] - RF_diff_pair_ref.ports["RF_M2_tie_W_bottom_lay_W"].center[0]) + source_via_width)
        
        via_RF_gate_ref.movex(-abs(RF_gate.center[0] - RF_diff_pair_ref.ports["RF_M1_tie_W_bottom_lay_W"].center[0]) - gate_via_width)
        via_RF_b_gate_ref.movex(abs(RF_b_gate.center[0] - RF_diff_pair_ref.ports["RF_M2_tie_W_bottom_lay_W"].center[0]) + gate_via_width)
        
        via_RF_gate_ref.movey(RF_gate.width)
        via_RF_b_gate_ref.movey(RF_gate.width)
        
        # Route to vias
        comp << straight_route(self.pdk, via_M1_source_ref.ports["bottom_lay_W"], M1_source)
        comp << straight_route(self.pdk, via_M2_source_ref.ports["bottom_lay_W"], M2_source)
        comp << straight_route(self.pdk, via_RF_gate_ref.ports["bottom_lay_W"], RF_gate)
        comp << straight_route(self.pdk, via_RF_b_gate_ref.ports["bottom_lay_W"], RF_b_gate)
        
        return via_RF_gate_ref, via_RF_b_gate_ref, via_M1_source_ref, via_M2_source_ref
    
    def build(self) -> Component:
        """
        Build the complete Gilbert mixer.
        
        This is the main method that orchestrates the creation of all components
        and their interconnections.
        
        Returns:
            Component: The complete Gilbert mixer component
        """
        # Create main component
        self.top_level = Component(name=self.component_name)
        
        # Create LO and RF differential pairs
        lo_diff_pairs = self.create_LO_diff_pairs(tie=True)
        rf_diff_pair = self.create_RF_diff_pair()
        
        # Place components
        self.lo_diff_pairs_ref = self.top_level << lo_diff_pairs
        self.rf_diff_pair_ref = self.top_level << rf_diff_pair
        
        # Align RF pair to southern side of LO guardring
        align_comp_to_port(
            self.rf_diff_pair_ref,
            self.lo_diff_pairs_ref.ports["well_S"],
            alignment=('c', 'b')
        )
        
        # Connect guard rings
        comp = self.top_level
        
        # Route between RF M1 and M2
        route_RF_guardrings = straight_route(
            self.pdk,
            self.rf_diff_pair_ref.ports['RF_M1_tie_E_top_met_E'],
            self.rf_diff_pair_ref.ports['RF_M2_tie_E_top_met_W'],
        )
        
        # Route RF to LO guardrings
        route_RF_M1_LO_guardrings = straight_route(
            self.pdk,
            self.rf_diff_pair_ref.ports['RF_M1_tie_N_top_met_N'],
            self.lo_diff_pairs_ref.ports['LO_tie_S_top_met_S'],
        )
        route_RF_M2_LO_guardrings = straight_route(
            self.pdk,
            self.rf_diff_pair_ref.ports['RF_M2_tie_N_top_met_N'],
            self.lo_diff_pairs_ref.ports['LO_tie_S_top_met_S'],
        )
        
        # Route RF M1 to M2 top and bottom
        route_RF_M1_M2_top_guardrings = straight_route(
            self.pdk,
            self.rf_diff_pair_ref.ports['RF_M1_tie_N_top_met_E'],
            self.rf_diff_pair_ref.ports['RF_M2_tie_N_top_met_E'],
        )
        route_RF_M1_M2_bot_guardrings = straight_route(
            self.pdk,
            self.rf_diff_pair_ref.ports['RF_M1_tie_S_top_met_E'],
            self.rf_diff_pair_ref.ports['RF_M2_tie_S_top_met_E'],
        )
        
        # Add all guard ring routes
        comp << route_RF_guardrings
        comp << route_RF_M1_LO_guardrings
        comp << route_RF_M2_LO_guardrings
        comp << route_RF_M1_M2_top_guardrings
        comp << route_RF_M1_M2_bot_guardrings
        
        # Add VSS via
        via_size = (1.42, 1.42)
        via_vss = via_array(
            self.pdk, "met2", "met3",
            size=via_size,
            lay_every_layer=True,
            fullbottom=True
        )
        via_vss_ref = comp << via_vss
        align_comp_to_port(
            via_vss_ref,
            self.lo_diff_pairs_ref.ports["LO_well_S"],
            alignment=('c', 'c')
        )
        self._add_pin_and_label_to_via(comp, via_vss_ref, "VSS", debug_mode=False)
        
        # Create vias outside tapring for LO
        LO_via_extension = abs(evaluate_bbox(self.lo_diff_pairs_ref)[0] - evaluate_bbox(self.rf_diff_pair_ref)[0])
        self.extra_port_vias_x_displacement = LO_via_extension
        
        (via_port_LO_ref, via_port_LO_b_ref, 
         via_port_1_ref, via_port_2_ref, 
         via_port_3_ref, via_port_4_ref) = self._create_LO_vias_outside_tapring_and_route()
        
        # Create vias outside tapring for RF
        (via_RF_gate_ref, via_RF_b_gate_ref,
         via_M1_source_ref, via_M2_source_ref) = self._create_RF_vias_outside_tapring_and_route()
        
        # Add pins and labels
        self._add_pin_and_label_to_via(comp, via_M1_source_ref, "I_bias_pos")
        self._add_pin_and_label_to_via(comp, via_M2_source_ref, "I_bias_neg")
        self._add_pin_and_label_to_via(comp, via_port_3_ref, "V_out_p")
        self._add_pin_and_label_to_via(comp, via_port_4_ref, "V_out_n")
        self._add_pin_and_label_to_via(comp, via_port_LO_ref, "V_LO")
        self._add_pin_and_label_to_via(comp, via_port_LO_b_ref, "V_LO_b")
        self._add_pin_and_label_to_via(comp, via_RF_gate_ref, "V_RF")
        self._add_pin_and_label_to_via(comp, via_RF_b_gate_ref, "V_RF_b")
        
        # Route common sources of LO to drains of RF FETs
        route_port1 = L_route(
            self.pdk,
            via_port_1_ref.ports['top_met_S'],
            self.rf_diff_pair_ref.ports['RF_M1_drain_W'],
            hglayer="met2",
            vglayer="met3"
        )
        route_port2 = L_route(
            self.pdk,
            via_port_2_ref.ports['top_met_S'],
            self.rf_diff_pair_ref.ports['RF_M2_drain_W'],
            hglayer="met2",
            vglayer="met3"
        )
        
        comp << route_port1
        comp << route_port2
        
        return comp
    
    def write_gds(self, filename: str = 'Gilbert_cell_interdigited.gds') -> None:
        """
        Write the component to a GDS file.
        
        Args:
            filename: Output GDS filename
        """
        if self.top_level is None:
            raise ValueError("Component not built yet. Call build() first.")
        
        self.top_level.write_gds(
            filename,
            cellname=self.component_name,
            unit=1e-6,
            precision=1e-9,
        )
    
    def run_drc(self) -> Optional[str]:
        """
        Run DRC on the component.
        
        Returns:
            Optional[str]: DRC result or None if DRC fails
        """
        if self.top_level is None:
            raise ValueError("Component not built yet. Call build() first.")
        
        try:
            drc_result = self.pdk.drc_magic(self.top_level, self.top_level.name)
            return drc_result
        except Exception as e:
            print(f"⚠ Magic DRC skipped: {e}")
            return None


# Example usage
if __name__ == "__main__":
    from glayout import gf180
    
    # Initialize PDK
    pdk_choice = gf180
    
    # Configure LO FETs
    lo_fet_config = LOFETConfig(
        sd_rmult=2,
        sd_route_topmet="met2",
        gate_route_topmet="met2",
        gate_rmult=3,
        interfinger_rmult=2,
        tie_layers=("met2", "met1"),
        inter_finger_topmet="met1",
        sd_route_extension=0.0,
        gate_route_extension=0,
        with_dummies=False
    )
    
    # Configure RF FETs
    rf_fet_config = RFFETConfig(
        with_dnwell=False,
        sd_route_topmet="met2",
        gate_route_topmet="met2",
        sd_rmult=2,
        gate_rmult=3,
        interfinger_rmult=2,
        tie_layers=("met2", "met1"),
        inter_finger_topmet="met1",
        with_dummies=True,
        with_tie=True,
        with_substrate_tap=False
    )
    
    # Create mixer instance
    mixer = GilbertMixerInterdigited(
        pdk=pdk_choice,
        lo_width=20.0,
        lo_fingers=5,
        rf_width=10.0,
        rf_fingers=5,
        lo_fet_config=lo_fet_config,
        rf_fet_config=rf_fet_config
    )
    
    # Build the mixer
    print("Building Gilbert mixer...")
    component = mixer.build()
    
    # Write GDS
    print("✓ Writing GDS files...")
    mixer.write_gds('lvs/gds/Gilbert_cell_interdigited.gds')
    print("  - Hierarchical GDS: Gilbert_cell_interdigited_class.gds")
    
    # Run DRC
    print("\n...Running DRC...")
    drc_result = mixer.run_drc()
    if drc_result:
        print(f"✓ Magic DRC result: {drc_result}")
    
    print("\n" + "="*60)
    print("TEST COMPLETED - GDS file generated successfully!")
    print("="*60)
