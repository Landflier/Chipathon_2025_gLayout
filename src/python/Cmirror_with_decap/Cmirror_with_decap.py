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


@dataclass
class CMirrorConfig:
    """Configuration for Current Mirror FETs"""
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
    with_tie: bool = True
    with_dnwell: bool = False
    with_decap: bool = False

class CmirrorWithDecap:
    """
    Class for creating current mirror with decoupling capacitor layouts.
    
    This class encapsulates all functionality for generating an interdigitized
    current mirror with proper routing and decoupling capacitor integration.
    """
    
    def __init__(
        self,
        pdk: MappedPDK,
        width_ref: float,
        width_mir: float,
        fingers_ref: int,
        fingers_mir: int,
        length: Optional[float] = None,
        cmirror_config: Optional[CMirrorConfig] = None,
        decap_size: Optional[Tuple[float, float]] = None,
        extra_port_vias_x_displacement: float = 0,
        component_name: str = "Cmirror_with_decap"
    ):
        """
        Initialize the current mirror with configuration parameters.
    
    Args:
            pdk: PDK for design rules and layer information
            width_ref: Width of reference transistory, with I_BIAS
            width_mir: Width of mirroring transistor, wtih I_OUT
            fingers_ref: Number of fingers for reference transistor
            fingers_mir: Number of fingers for mirror transistor
            length: Length of transistors (uses PDK minimum if None)
            cmirror_config: Configuration for current mirror FETs
            decap_size: Optional size for decoupling capacitor
            extra_port_vias_x_displacement: Extra displacement for port vias
            component_name: Name for the top-level component
        """
        self.pdk = pdk
        self.pdk.activate()
        
        # Transistor dimensions
        self.width_ref = width_ref
        self.fingers_ref = fingers_ref
        self.width_mir = width_mir
        self.fingers_mir = fingers_mir
        
        # Use PDK minimum lengths if not specified
        min_length = pdk.get_grule('poly')['min_width']
        self.length = length if length is not None else min_length
        
        # Configuration
        self.cmirror_config = cmirror_config or CMirrorConfig()
        
        # Other parameters
        self.decap_size = decap_size
        self.extra_port_vias_x_displacement = extra_port_vias_x_displacement
        self.component_name = component_name
        
        # Component references (populated during build)
        self.top_level: Optional[Component] = None
        self.cmirror_ref: Optional[Component] = None
        
        # Validate inputs
        self._validate_inputs()
    
    def _validate_inputs(self) -> None:

        if self.width_ref / self.fingers_ref != self.width_mir / self.fingers_mir:
           raise ValueError(f"Please make sure width_ref/fingers_ref = width_mir/fingers_mir. Currently {self.width_ref}/{self.fingers_ref} != {self.width_mir}/{self.fingers_mir}")

        """Validate input parameters."""
        # if self.width_ref % self.fingers_ref != 0:
        #     raise ValueError(f"Width ({self.width}) must be a multiple of fingers ({self.fingers})")
        
        if self.cmirror_config.sd_rmult < 1 or self.cmirror_config.interfinger_rmult < 1 or self.cmirror_config.gate_rmult < 1:
            raise ValueError("Routing multipliers must be positive integers")
        
        if "+s/d" not in self.cmirror_config.sdlayer:
            raise ValueError("Specify + doped region for current mirror")

        # interfingiring requires fingers_ref and fingers_mir to be both even.
        if (self.fingers_ref % 2 == 1) or (self.fingers_mir % 2 == 1):
            print("One of the finger numbers is odd. This impedes the currently implemented interfingering...")
            print("Doubling all fingers. This can lead to unreasonable finger widths...")
            self.fingers_ref = 2 * self.fingers_ref 
            self.fingers_mir = 2 * self.fingers_mir
            print("Either change W, fingers_ref, fingers_mir, or check layout after generation")
    
    def _create_finger_array(
        self,
        length: float, # in this implementation, the length of both transistors is the same. This makes interfingering easier
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
        used by the current mirror transistors.
        """
        # Calculate finger dimensions

        finger_width = self.width_mir / self.fingers_mir
        fingers = self.fingers_mir + self.fingers_ref
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
        fingerarray = prec_array(finger, columns=self.fingers_ref + self.fingers_mir, rows=1, spacing=(poly_spacing + length, 1), absolute_spacing=True)
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
        
        sd_diff_ovhg = self.pdk.get_grule(sdlayer, "active_diff")["min_enclosure"]
        sdlayer_dims = [dim + 2 * sd_diff_ovhg for dim in diff_dims]
        sdlayer_ref = multiplier << rectangle(size=sdlayer_dims, layer=self.pdk.get_glayer(sdlayer), centered=True)
        
        multiplier.add_ports(sdlayer_ref.get_ports_list(), prefix="plusdoped_")
        multiplier.add_ports(diff.get_ports_list(), prefix="diff_")
        
        return multiplier
    
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
    

    def _add_source_drain_gate_routing(
            self,
        multiplier: Component,
        sd_rmult: int,
        sd_route_topmet: str,
        sd_route_extension: float,
        gate_route_topmet: str,
        gate_rmult: int,
        gate_route_extension: float,
        interfinger_rmult: int
    ) -> None:
        """
            Add source/drain and gate routing to the multiplier component for current mirror.
            
            This method adapts the routing for a 2-FET current mirror configuration
            where we need proper connections for reference and mirror transistors.
        """
        """
        mosfet circuit:
        s/d denotes source drain
        '-' denotes connected
        d   d
        |
        g---g
        A   B 
        s---s---VSS

        --- drain_ref    (port1)   --- * extends to the left
        --- drain_mirror (port2)   --- * extends to the right 
        --- finger array          ---
        --- common_source (port3)   --- * extends to the right
        """
        number_sd_rows = 0
        for port_name in multiplier.ports.keys():
            if port_name.startswith("leftsd_array") and "_col" in port_name:
                # Extract row number from port name like "row0_col1_..."
                row_part = port_name.split("_")[2]
                row_num = int(row_part.replace("row", ""))
                number_sd_rows = max(number_sd_rows, row_num)

        # Create vias and routing for current mirror (2 FETs instead of 4)
        sdvia = via_stack(self.pdk, "met1", sd_route_topmet)
        sdmet_height = sd_rmult * evaluate_bbox(sdvia)[1]
        sdroute_minsep = self.pdk.get_grule(sd_route_topmet)["min_separation"]
        sdvia_ports = list()
        
        # Define routing configuration dictionary
        """
        routes are numbered the following way, wrt to the finger array
        '-' -> denotes a metal horizontal 'track', connecting all the s/d/gate vertical connections

        ---   top_track_2  ---
        ---   top_track_1  ---
             finger_array
        --- bottom_track_1 ---
        --- bottom_track_2 ---
        """
        routing_configs = {
            'top_track_1': {
                'y_align_via': lambda width: width/2,
                'alignment_port': ('c', 't'),
                'sdvia_extension': lambda sdroute_minsep, sdmet_height: +(sdroute_minsep + (sdmet_height)/2),
                'sd_route_extension_sign': +1
            },
            'top_track_2': {
                'y_align_via': lambda width: width/2,
                'alignment_port': ('c', 't'),
                'sdvia_extension': lambda sdroute_minsep, sdmet_height: +(sdroute_minsep + sdroute_minsep + (sdmet_height/2 + sdmet_height)),
                'sd_route_extension_sign': +1
            },
            'bottom_track_1': {
                'y_align_via': lambda width: -width/2,
                'alignment_port': ('c', 'b'),
                'sdvia_extension': lambda sdroute_minsep, sdmet_height: -(sdroute_minsep + (sdmet_height)/2),
                'sd_route_extension_sign': -1
            },
            'bottom_track_2': {
                'y_align_via': lambda width: -width/2,
                'alignment_port': ('c', 'b'),
                'sdvia_extension': lambda sdroute_minsep, sdmet_height: -(sdroute_minsep + sdroute_minsep + (sdmet_height/2 + sdmet_height)),
                'sd_route_extension_sign': -1
            },
        }
        

        def create_and_route_finger(config_key, port_name, port_suffix="", new_port_name="diffusion_port_to_align_sd", is_gate_routing=False):
            config = routing_configs[config_key]
            
            # Get alignment port
            rel_align_port = multiplier.ports[port_name]
            
            # Calculate y position
            if is_gate_routing:
                y_position = config['y_align_via'](width) + config['sdvia_extension'](sdroute_minsep, sdmet_height)
                port_name_prefix = "gate_port_vroute"
            else:
                y_position = config['y_align_via'](width)
                port_name_prefix = new_port_name
            
            # Create port
            port_to_route = multiplier.add_port(
                center=(rel_align_port.center[0], y_position),
                width=rel_align_port.width,
                orientation=90,
                layer=rel_align_port.layer,
                name=f"{port_name_prefix}_{port_suffix}"
            )
            
            if is_gate_routing:
                # For gate routing, just create vertical route and snap to grid
                port_to_route.y = self.pdk.snap_to_2xgrid(port_to_route.y)
                multiplier << straight_route(self.pdk, rel_align_port, port_to_route)
                return []
            else:
                # For SD routing, there is a via at the end of the route. 
                displacement = config['sdvia_extension'](sdroute_minsep, sdmet_height) + config['sd_route_extension_sign'] * self.pdk.snap_to_2xgrid(sd_route_extension)
                sdvia_ref = align_comp_to_port(sdvia, port_to_route, alignment=config['alignment_port'])
                multiplier.add(sdvia_ref.movey(displacement))
                multiplier << straight_route(self.pdk, port_to_route, sdvia_ref.ports["bottom_met_N"])

                # Rename ports within sdvia_ref with config_key prefix and port_suffix suffix
                sdvia_ref.ports["top_met_W"].name = f"{config_key}_top_met_W_{port_suffix}"
                sdvia_ref.ports["top_met_E"].name = f"{config_key}_top_met_E_{port_suffix}"
                sdvia_ref.ports["top_met_N"].name = f"{config_key}_top_met_N_{port_suffix}"
                sdvia_ref.ports["top_met_S"].name = f"{config_key}_top_met_S_{port_suffix}"
                # Add renamed ports to multiplier
                multiplier.add_ports([sdvia_ref.ports["top_met_W"], sdvia_ref.ports["top_met_E"], 
                                    sdvia_ref.ports["top_met_N"], sdvia_ref.ports["top_met_S"]])
                return [sdvia_ref.ports["top_met_W"], sdvia_ref.ports["top_met_E"]]


        width = self.width_ref / self.fingers_ref
        # Route s/d regions next to each finger
        """
        for our interfingered layout , we use the following convention:
        ---   top_track_2 --- common source (Ms Rs)
        ---   top_track_1  --- drain M(irror) FET (Md)
              finger_array
        ---   bottom_track_1  --- drain R(eference) FET / gates (Rd)
        """
        # Route fingers in the following manner: s(Xd Xs)*nf_r/4 (Yd Ys)*nf_m/2 (Xd Xs)*nf_r/4 
        if self.fingers_ref % 4 == 0 or self.fingers_mir % 4 == 0:
            # Determine which case we're in for config selection. ref stands for reference fet, and check if it has fingers divisible by 4
            ref_case = self.fingers_ref % 4 == 0
            # ref_case = 1: X=ref, Y=mir (X=R, Y=M)
            # ref_case = 0: X=mir, Y=ref (X=M, Y=R)
            
            for finger_couple in range(int((self.fingers_ref + self.fingers_mir)/2)):
                # Select config based on finger position and case
                in_middle_region = finger_couple >= self.fingers_ref/4 and finger_couple < self.fingers_ref/4 + self.fingers_mir/2
                
                # ref_case     is : s(Rd Rs)*nf_r/4 (Md Ms)*nf_m/2 (Rd Rs)*nf_r/4 
                # not ref_case is : s(Md Ms)*nf_m/4 (Rd Rs)*nf_r/2 (Md Ms)*nf_m/4 
                # thus ref_case an in_middle_region and not ref_case and not in_middle_region just selects M(irror) FET's s/d regions
                if (ref_case and in_middle_region) or (not ref_case and not in_middle_region):
                    # (Md Ms) -> route Md
                    port_name = f"row0_col{2*finger_couple}_rightsd_array_row{number_sd_rows}_col0_top_met_N"
                    config_key = 'top_track_1'
                else:
                    # (Rd Rs) -> route Rd
                    port_name = f"row0_col{2*finger_couple}_rightsd_array_row0_col0_top_met_N"
                    config_key = 'bottom_track_1'

                sdvia_ports += create_and_route_finger(
                    config_key=config_key,
                    port_name=port_name,
                    port_suffix=f"{finger_couple*2}"
                )

                # finger couple's right finger's s/d region always routes to common source (port 3)
                sdvia_ports += create_and_route_finger(
                    config_key='top_track_2',
                    port_name=f"row0_col{2*finger_couple+1}_rightsd_array_row{number_sd_rows}_col0_top_met_N",
                    port_suffix=f"{finger_couple*2+1}"
                )
            
                # route the initial s, before all repeated structures Rs or Ms
                if finger_couple == 0:
                    rel_align_port = multiplier.ports['leftsd_top_met_N']
                    rel_align_port.width = rel_align_port.width / interfinger_rmult

                    sdvia_ports += create_and_route_finger(
                        config_key='top_track_2',
                        port_name="leftsd_top_met_N",
                        port_suffix="special_0"
                    )

        # Route fingers in the following manner: d(Xs Xd)*abs(nf_x-nf_y)/4 (Xs Yd Ys Xd)*min(nf_y, nf_x) /2 (Xs Xd)*abs(nf_x-nf_y)/4
        else:
            # Determine which FET has more fingers. ref stands for reference fet.
            # Note if =, is covered in the check below
            ref_case = self.fingers_ref > self.fingers_mir
            # ref_case = 1: X=ref, Y=mir (X=R, Y=M)
            # ref_case = 0: X=mir, Y=ref (X=M, Y=R)
            cutoff_left  = abs(self.fingers_ref - self.fingers_mir)/4
            cutoff_right = (self.fingers_ref + self.fingers_mir)/2 - cutoff_left
            
            finger_couple = 0 
            while finger_couple < (int((self.fingers_ref + self.fingers_mir)/2)):
                # Select config based on finger position
                in_middle_region = finger_couple >= cutoff_left and finger_couple < cutoff_right
                
                # ref_case     is : d(Rs Rd)*(nf_r-nf_m)/4 (Rs Md Ms Rd)nf_m/2 (Rs Rd)*(nf_r-nf_m)/4
                # not ref_case is : d(Ms Md)*(nf_m-nf_r)/4 (Ms Rd Rs Md)nf_r/2 (Ms Md)*(nf_m-nf_r)/4
                if in_middle_region:
                    # Determine config keys based on ref_case
                    # ref_case: (Rs Md Ms Rd) -> route Md and Rd -> configs: top_track_1, bottom_track_1
                    # not ref_case: (Ms Rd Rs Md) -> route Rd and Md -> configs: bottom_track_1, top_track_1
                    config_key_1 = 'top_track_1' if ref_case else 'bottom_track_1'
                    config_key_2 = 'bottom_track_1' if ref_case else 'top_track_1'
                    
                    # route Yd (port_name_1) and then Xd (port_name_2)
                    port_name_1 = f"row0_col{2*finger_couple+1}_rightsd_array_row{number_sd_rows}_col0_top_met_N" if ref_case else f"row0_col{2*finger_couple+1}_rightsd_array_row0_col0_top_met_N" 
                    port_name_2 = f"row0_col{2*finger_couple+3}_rightsd_array_row0_col0_top_met_N" if ref_case else f"row0_col{2*finger_couple+3}_rightsd_array_row{number_sd_rows}_col0_top_met_N" 
                    

                    sdvia_ports += create_and_route_finger(
                        config_key=config_key_1,
                        port_name=port_name_1,
                        port_suffix=f"{2*finger_couple + 1}"
                    )

                    sdvia_ports += create_and_route_finger(
                        config_key=config_key_2,
                        port_name=port_name_2,
                        port_suffix=f"{2*finger_couple + 3}"
                    )

                    # since Xs and Ys are the same port, route both
                    sdvia_ports += create_and_route_finger(
                        config_key='top_track_2',
                        port_name=f"row0_col{2*finger_couple}_rightsd_array_row{number_sd_rows}_col0_top_met_N",
                        port_suffix=f"{2*finger_couple}"
                    )
                    sdvia_ports += create_and_route_finger(
                        config_key='top_track_2',
                        port_name=f"row0_col{2*finger_couple+2}_rightsd_array_row{number_sd_rows}_col0_top_met_N",
                        port_suffix=f"{2*finger_couple + 2}"
                    )

                    # Increment finger_couple by two, since we routed two couples of fingers
                    finger_couple += 2

                elif not in_middle_region:
                    # route the initial d, before all repeated structures
                    # ref_case: routing dR -> top_track_2
                    # not ref_case: routing dM -> top_track_1
                    if finger_couple == 0:
                        # Manual width adjustment for initial d
                        rel_align_port = multiplier.ports['leftsd_top_met_N']
                        rel_align_port.width = rel_align_port.width / interfinger_rmult

                        # Determine config key based on ref_case, dR or dM
                        config_key = 'bottom_track_1' if ref_case else 'top_track_1'
                        
                        sdvia_ports += create_and_route_finger(
                            config_key=config_key,
                            port_name="leftsd_top_met_N",
                            port_suffix="special_0"
                        )

                    # routing all couples (Xs Xd)
                    # ref_case: route Rd port -> top_track_2
                    # not ref_case: route Md port -> top_track_1
                    config_key = 'bottom_track_1' if ref_case else 'top_track_1'
                    
                    drain_port_name = f"row0_col{2*finger_couple+1}_rightsd_array_row{number_sd_rows}_col0_top_met_N"
                    source_port_name = f"row0_col{2*finger_couple}_rightsd_array_row0_col0_top_met_N"
        
                    # Route drain connection (Rd or Md depending on ref_case)
                    sdvia_ports += create_and_route_finger(
                        config_key=config_key,
                        port_name=drain_port_name,
                        port_suffix=f"{2*finger_couple + 1}"
                    )

                    # Route (Rs or Ms)
                    sdvia_ports += create_and_route_finger(
                        config_key='top_track_2',
                        port_name=source_port_name,
                        port_suffix=f"{2*finger_couple}"
                    )

                    finger_couple += 1

        for finger in range(self.fingers_ref + self.fingers_mir):
            gate_port_name = f"row0_col{finger}_gate_S"

            # Route gate to Rd drain connection 
            create_and_route_finger(
                config_key=config_key,
                port_name=gate_port_name,
                port_suffix=f"{finger}",
                is_gate_routing=True
            )
        # Place horizontal gate routes
        gate_width = multiplier.ports[f"diffusion_port_to_align_sd_{self.fingers_ref + self.fingers_mir - 1}"].center[0] \
                - multiplier.ports["leftsd_top_met_N"].center[0] \
                + multiplier.ports["leftsd_top_met_N"].width
        gate_route = rename_ports_by_list(
            via_array(self.pdk, "poly", gate_route_topmet, size=(gate_width, None), num_vias=(None, gate_rmult), no_exception=True, fullbottom=True),
            [("top_met_", "gate_top_")]
        )
        
        # Horizontal gate routes
        # gate_ref = align_comp_to_port(gate_route.copy(), multiplier.ports[f"diffusion_port_to_align_sd_special_0"], alignment=('r', 'b'), layer=self.pdk.get_glayer("poly"))
        gate_ref = align_comp_to_port(gate_route.copy(), multiplier.ports[f"bottom_track_1_top_met_E_{self.fingers_ref + self.fingers_mir - 1}"], alignment=('l', 'b'), layer=self.pdk.get_glayer("poly"))
        multiplier.add(gate_ref)
        
        # multiplier.add_ports(gate_ref.get_ports_list(), prefix="ref_drain_")
        
        # Horizontal route s/d 
        # Get unique y-coordinates for SD ports
        y_coords = [port.center[1] for port in sdvia_ports]
        unique_y_coords = list(set(y_coords))
        unique_y_coords.sort()
        
        y_coord_indices = []
        for unique_y in unique_y_coords:
            first_index = next(i for i, y in enumerate(y_coords) if y == unique_y)
            y_coord_indices.append(first_index)
        # Place SD route metal
        # port_0 is common_gate / ref_drain
        # port_1 is top_track_1 (E, W), and port_2 is top_track_2 (E,W)
        # port_1 -> mirror_drain (Md)
        # port_2 -> source, mirror_source, or common_source (Rs, Ms)
        port_0_sd_index = y_coord_indices[0]
        port_1_sd_index = y_coord_indices[1]
        port_2_sd_index = y_coord_indices[-1]
        
        sd_width = sdvia_ports[-1].center[0] - sdvia_ports[0].center[0]
        sd_width_gate = abs (multiplier.ports[f"leftsd_top_met_N"].center[0] - multiplier.ports[f"diffusion_port_to_align_sd_{self.fingers_ref + self.fingers_mir - 1}"].center[0]) + multiplier.ports[f"leftsd_top_met_N"].width

        sd_route = rectangle(size=(sd_width, sdmet_height), layer=self.pdk.get_glayer(sd_route_topmet), centered=True)
        sd_route_top = rectangle(size=(sd_width, sdmet_height), layer=self.pdk.get_glayer(sd_route_topmet), centered=True)
        sd_route_bot = rectangle(size=(sd_width_gate, sdmet_height), layer=self.pdk.get_glayer("met1"), centered=True)
        
        # Update port widths
        sdvia_ports[port_1_sd_index].width = sdmet_height
        sdvia_ports[port_2_sd_index].width = sdmet_height
        
        # Add SD routes
        # TODO: this is a bit cluncky, adding met2 on top of the gate via array. Since the array is very dificult to use as a single slab, and has 100s of ports

        # need two metal layers for port_0, since the gate vias and the sd vias can give DRC errors for met1 spacing.
        # So we lay met1 and met2 entirely over the gate port (bottom_track_1)
        port_0_sd_route_top_met = align_comp_to_port(sd_route_top.copy(), sdvia_ports[port_0_sd_index], alignment=(None, 'b'))
        port_0_sd_route_bot_met = align_comp_to_port(sd_route_bot.copy(), sdvia_ports[port_0_sd_index], alignment=(None, 'b'))
        port_1_sd_route = align_comp_to_port(sd_route.copy(), sdvia_ports[port_1_sd_index], alignment=(None, 'c'))
        port_2_sd_route = align_comp_to_port(sd_route.copy(), sdvia_ports[port_2_sd_index], alignment=(None, 'c'))
        
        port_2_sd_route = rename_ports_by_orientation(port_2_sd_route)
        multiplier.add(port_0_sd_route_top_met)
        multiplier.add(port_0_sd_route_bot_met)
        multiplier.add(port_1_sd_route)
        multiplier.add(port_2_sd_route)
        

        # Add ports
        multiplier.add_ports(port_0_sd_route_top_met.get_ports_list(), prefix="ref_drain_")
        multiplier.add_ports(port_1_sd_route.get_ports_list(), prefix="mir_drain_")
        multiplier.add_ports(port_2_sd_route.get_ports_list(), prefix="common_source_")

    def _create_cmirror_vias_outside_tapring_and_route(self) -> Tuple:
        """
        Create vias for routing the current mirror I/O outside the tapring.
        
        Returns:
            tuple: References to the created vias (VREF, VCOPY, VSS, VB)
        """
        comp = self.top_level
        cmirror_ref = self.cmirror_ref
        
        # Get current mirror I/O ports
        vref_port = cmirror_ref.ports["ref_drain_W"]  # Reference drain (VREF/IREF input)
        vmir_port = cmirror_ref.ports["mir_drain_W"]  # Mirror drain (ICOPY output)
        vss_port = cmirror_ref.ports["common_source_W"]  # Common sources (VSS)

        # Standard via size for current mirror connections
        via_width = max(vref_port.width, vmir_port.width, vss_port.width)
        
        # Create vias for each signal
        via_vref = via_array(self.pdk, "met3", "met2", 
                            size=(via_width, via_width),
                            fullbottom=True)
        via_vmir = via_array(self.pdk, "met3", "met2", 
                            size=(via_width, via_width),
                            fullbottom=True)
        via_vss = via_array(self.pdk, "met3", "met2", 
                            size=(via_width, via_width),
                            fullbottom=True)

        # Add vias to component
        via_vref_ref = comp << via_vref
        via_vmir_ref = comp << via_vmir
        via_vss_ref = comp << via_vss
        # Position vias aligned to their respective ports
        align_comp_to_port(via_vref_ref, vref_port, alignment=('c', 'c'))
        align_comp_to_port(via_vmir_ref, vmir_port, alignment=('c', 'c'))
        align_comp_to_port(via_vss_ref, vss_port, alignment=('c', 'c'))

        # Move vias outside the tapring with displacement
        # Calculate displacement to move vias outside tapring
        tie_w_port = cmirror_ref.ports["tie_W_bottom_lay_W"]
        tie_e_port = cmirror_ref.ports["tie_E_bottom_lay_E"]
        
        # Move VREF and VSS to the left
        via_vref_ref.movex(-abs(vref_port.center[0] - tie_w_port.center[0]) - via_width - self.extra_port_vias_x_displacement)
        via_vss_ref.movex(-abs(vss_port.center[0] - tie_w_port.center[0]) - via_width - self.extra_port_vias_x_displacement)
        
        # Move VCOPY and VB to the right  
        via_vmir_ref.movex(abs(vmir_port.center[0] - tie_e_port.center[0]) + via_width + self.extra_port_vias_x_displacement)
            

        # Route vias to their corresponding ports
        try:
            comp << straight_route(self.pdk, 
                    via_vref_ref.ports["bottom_lay_W"], 
                    vref_port)
            comp << straight_route(self.pdk, 
                    via_vmir_ref.ports["bottom_lay_W"], 
                    vmir_port)
            comp << straight_route(self.pdk, 
                    via_vss_ref.ports["bottom_lay_W"], 
                    vss_port)
        except Exception as e:
            print(f"Warning: Could not route via connections: {e}")

        return via_vref_ref, via_vmir_ref, via_vss_ref

    def create_cmirror_interdigitized(self) -> Component:
        """
        Create interdigitized current mirror using custom finger array approach.
        This method creates 2 NMOS transistors in an interdigitized layout pattern.
        
        Returns:
            Component: Single interdigitized component containing both current mirror transistors
        """
        config = self.cmirror_config
        
        # Create finger array
        multiplier = self._create_finger_array(
            length=self.length,
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
        width = self.pdk.snap_to_2xgrid(self.width_ref/self.fingers_ref)
        
        multiplier = component_snap_to_grid(rename_ports_by_orientation(multiplier))

        # Add routing
        if config.routing:
            self._add_source_drain_gate_routing(
                multiplier,
                config.sd_rmult, config.sd_route_topmet, config.sd_route_extension,
                config.gate_route_topmet, config.gate_rmult, config.gate_route_extension,
                config.interfinger_rmult
            )

        # Add tap ring if requested
        # sdlayer == n+s/d is NMOS, p+s/d is PMOS
        tie_well = "pwell" if config.sdlayer == "n+s/d" else "nwell"
        sdlayer_tiering = "p+s/d" if config.sdlayer == "n+s/d" else "n+s/d"
        if config.with_tie:
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
                sdlayer=sdlayer_tiering,
                horizontal_glayer=config.tie_layers[0],
                vertical_glayer=config.tie_layers[1],
            )
            multiplier.add_ports(tiering_ref.get_ports_list(), prefix="tie_")

        # make sure correct names by orientation, since routing adds some ports
        multiplier = rename_ports_by_orientation(multiplier)
        # route top_track_2 (common source) to the tapring
        multiplier << straight_route(self.pdk, multiplier.ports["tie_N_top_met_N"], multiplier.ports["common_source_N"])

        # Add pwell or nwell
        multiplier.add_padding(
            layers=(self.pdk.get_glayer(tie_well),),
            default=self.pdk.get_grule(tie_well, "active_tap")["min_enclosure"],
        )
        # add dnwell if dnwell and using nmos
        if config.with_dnwell and config.sdlayer == "n+s/d":
            multiplier.add_padding(
                    layers=(self.pdk.get_glayer("dnwell"),),
                    default=self.pdk.get_grule("pwell", "dnwell")["min_enclosure"],
                    )
        multiplier = add_ports_perimeter(multiplier, layer=self.pdk.get_glayer("pwell"), prefix="well_")

        # Route dummies if present
        if config.with_dummies:
            try:
                multiplier << straight_route(self.pdk, 
                        multiplier.ports["dummy_gate_L_W"], 
                        multiplier.ports["tie_W_bottom_lay_E"],
                        glayer1="poly",
                        glayer2="met1",
                        )

                multiplier << straight_route(self.pdk, 
                        multiplier.ports["dummy_gate_R_E"], 
                        multiplier.ports["tie_E_bottom_lay_W"],
                        glayer1="poly",
                        glayer2="met1",
                        )
            except KeyError:
                print("Warning: Could not route dummy gates to tie ring")

        # Finalize component
        cmirror_interdigitized = component_snap_to_grid(rename_ports_by_orientation(multiplier))
        cmirror_interdigitized.name = "cmirror_interdigitized"
        
        return cmirror_interdigitized


    def _create_decap_capacitor(self) -> Component:
        """
        Create a decoupling capacitor using MIM capacitor.
        
        Returns:
            Component: The decap capacitor component
        """
        # Use default size if not specified, or use provided decap_size
        if self.decap_size is not None:
            cap_size = self.decap_size
        else:
            # Default decap size - can be adjusted based on requirements
            cap_size = (1.0, 1.0)  # 1um x 1um
        
        # Create MIM capacitor
        decap = mimcap(self.pdk, size=cap_size)

        # align with the vias
        
        return decap

    def build(self) -> Component:
        """
        Build the complete current mirror with decoupling capacitor.
        
        This is the main method that orchestrates the creation of all components
        and their interconnections.
        
        Returns:
            Component: The complete current mirror component
        """
        # Create main component
        self.top_level = Component(name=self.component_name)
        
        # Create current mirror
        cmirror = self.create_cmirror_interdigitized()

        # Place component
        self.cmirror_ref = self.top_level << cmirror

        # Create vias outside tapring
        (via_vref_ref, via_vcopy_ref, via_vss_ref) = self._create_cmirror_vias_outside_tapring_and_route()
        
        # Add pins and labels
        self._add_pin_and_label_to_via(self.top_level, via_vref_ref, "I_BIAS")
        self._add_pin_and_label_to_via(self.top_level, via_vcopy_ref, "I_OUT")
        via_vss_label = "VSS" if self.cmirror_config.sdlayer == "n+s/d" else "VDD"
        self._add_pin_and_label_to_via(self.top_level, via_vss_ref, via_vss_label)
        
        # Create and add decap capacitor
        if self.cmirror_config.with_decap == True:
            decap = self._create_decap_capacitor()
            self.decap_ref = align_comp_to_port(decap, via_vss_ref.ports["top_met_W"], alignment=('l', 'c'))
            self.top_level.add(self.decap_ref) 
            
            # Route connections
            # Route decap to VSS via (straight route)
            vss_route = straight_route(self.pdk, self.decap_ref.ports["bottom_met_E"], via_vss_ref.ports["bottom_lay_W"])
            self.top_level << vss_route
        
            # Route decap to VREF via (L-route from S of mimcap to W of via_vref_ref)
            vref_route = L_route(self.pdk, self.decap_ref.ports["bottom_met_S"], via_vref_ref.ports["bottom_lay_W"])
            self.top_level << vref_route

        return self.top_level
    
    def write_gds(self, filename: str = 'Cmirror_with_decap.gds') -> None:
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
            precision=5e-9,
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
    
    # Configure current mirror FETs
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
        width_ref=7.5,
        width_mir=1.5,
        fingers_ref=5,
        fingers_mir=1,
        length=0.28,
        cmirror_config=cmirror_nmos_config
    )
    
    # Build the current mirror
    print("Building current mirror...")
    component = cmirror_nmos.build()
    
    # Write GDS
    print("✓ Writing GDS files...")
    cmirror_nmos.write_gds('lvs/gds/nmos_Cmirror_with_decap.gds')
    print("  - Hierarchical GDS: Cmirror_with_decap.gds")
    
    # Run DRC
    print("\n...Running DRC...")
    drc_result = cmirror_nmos.run_drc()
    if drc_result:
        print(f"✓ Magic DRC result: {drc_result}")
    
    print("\n" + "="*60)
    print("CURRENT MIRROR DESIGN COMPLETED!")
    print("="*60)
   
