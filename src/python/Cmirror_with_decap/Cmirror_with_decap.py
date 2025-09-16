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
        
        def create_and_route_finger(config_key, port_name, port_suffix="", new_port_name="diffusion_port_to_align_sd"):
            config = routing_configs[config_key]
            
            # Get alignment port
            rel_align_port = multiplier.ports[port_name]
            
            # Create and route port
            port_to_route = multiplier.add_port(
                center=(rel_align_port.center[0], config['y_align_via'](width)),
                width=rel_align_port.width,
                orientation=90,
                layer=rel_align_port.layer,
                name=f"{new_port_name}_{port_suffix}"
            )
            
            # Calculate displacement and route
            displacement = config['sdvia_extension'](sdroute_minsep, sdmet_height) + config['sd_route_extension_sign'] * self.pdk.snap_to_2xgrid(sd_route_extension)
            sdvia_ref = align_comp_to_port(sdvia, port_to_route, alignment=config['alignment_port'])
            multiplier.add(sdvia_ref.movey(displacement))
            multiplier << straight_route(self.pdk, port_to_route, sdvia_ref.ports["bottom_met_N"])
            
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
                        port_suffix="s_0"
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
                            port_suffix="d_0"
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
            config_key = 'bottom_track_1'

            gate_port_name = f"row0_col{finger}_gate_S"    
            gate_aligning_port = multiplier.ports[gate_port_name]

            config = routing_configs[config_key]
            # Route gate to Rd drain connection 
            psuedo_gate_route = multiplier.add_port(
                    center=(gate_aligning_port.center[0], config['y_align_via'](width)),
                    width=gate_aligning_port.width,
                    orientation=90,
                    layer=gate_aligning_port.layer,
                    name=f"gate_port_vroute_{finger}"
                    )
            psuedo_gate_route.y = self.pdk.snap_to_2xgrid(psuedo_gate_route.y)

            multiplier << straight_route(self.pdk, gate_aligning_port, psuedo_gate_route)


            """
            # Route gate to Rd drain connection 
            sdvia_ports += create_and_route_finger(
                config_key=config_key,
                port_name=gate_port_name,
                port_suffix=f"{finger}",
                new_port_name=f"gate_vroute_via"
            )

        # Place horizontal gate routes
        gate_width = multiplier.ports[f"gate_vroute_via_{self.fingers_ref + self.fingers_mir-1}"].center[0] \
                - multiplier.ports["gate_vroute_via_0"].center[0] \
                + multiplier.ports["row0_col0_gate_S"].width
        gate_route = rename_ports_by_list(
            via_array(self.pdk, "poly", gate_route_topmet, size=(gate_width, None), num_vias=(None, gate_rmult), no_exception=True, fullbottom=True),
            [("top_met_", "gate_top_")]
        )
        
        # gate routes
        gate_ref = align_comp_to_port(gate_route.copy(), multiplier.ports[f"gate_vroute_via_{self.fingers_ref + self.fingers_mir - 1}"], alignment=('l', 'b'), layer=self.pdk.get_glayer("poly"))
        multiplier.add(gate_ref)
        
        multiplier.add_ports(gate_ref.get_ports_list(), prefix="common_gate__")
        
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
        
        sd_width = sdvia_ports[-1].center[0] - sdvia_ports[0].center[0]
        # sd_route = rectangle(size=(sd_width, sdmet_height), layer=self.pdk.get_glayer(sd_route_topmet), centered=True)
        
        # Update port widths
        sdvia_ports[port_1_sd_index].width = sdmet_height
        sdvia_ports[port_2_sd_index].width = sdmet_height
        
        # Add SD routes
        port_1_sd_route = align_comp_to_port(sd_route.copy(), sdvia_ports[port_1_sd_index], alignment=(None, 'c'))
        port_2_sd_route = align_comp_to_port(sd_route.copy(), sdvia_ports[port_2_sd_index], alignment=(None, 'c'))
        
        multiplier.add(port_1_sd_route)
        multiplier.add(port_2_sd_route)
        
        # Add ports
        multiplier.add_ports(port_1_sd_route.get_ports_list(), prefix="port_1_")
        multiplier.add_ports(port_2_sd_route.get_ports_list(), prefix="port_2_")
        """

    def _create_cmirror_vias_outside_tapring_and_route(self) -> Tuple:
        """
        Create vias for routing the current mirror I/O outside the tapring.
        
        Returns:
            tuple: References to the created vias (VREF, VCOPY, VSS, VB)
        """
        comp = self.top_level
        cmirror_ref = self.cmirror_ref
        
        # Get current mirror I/O ports
        try:
            vref_port = cmirror_ref.ports["CM_Mref_drain_N"]  # Reference drain (VREF/IREF input)
            vcopy_port = cmirror_ref.ports["CM_Mmirror_drain_N"]  # Mirror drain (ICOPY output)
            vss_port = cmirror_ref.ports["CM_Mref_source_S"]  # Common sources (VSS)
            vb_port = cmirror_ref.ports["CM_Mref_tie_S_top_met_S"]  # Body/substrate connection
        except KeyError as e:
            print(f"Warning: Could not find current mirror port: {e}")
            # Use fallback port names
            vref_port = list(cmirror_ref.ports.values())[0]
            vcopy_port = list(cmirror_ref.ports.values())[1]
            vss_port = list(cmirror_ref.ports.values())[2]
            vb_port = list(cmirror_ref.ports.values())[3]

        # Standard via size for current mirror connections
        via_width = max(vref_port.width, vcopy_port.width, vss_port.width)
        
        # Create vias for each signal
        via_vref = via_array(self.pdk, "met3", "met2", 
                            size=(via_width, via_width),
                            fullbottom=True)
        via_vcopy = via_array(self.pdk, "met3", "met2", 
                            size=(via_width, via_width),
                            fullbottom=True)
        via_vss = via_array(self.pdk, "met3", "met2", 
                            size=(via_width, via_width),
                            fullbottom=True)
        via_vb = via_array(self.pdk, "met3", "met2", 
                            size=(via_width, via_width),
                            fullbottom=True)

        # Add vias to component
        via_vref_ref = comp << via_vref
        via_vcopy_ref = comp << via_vcopy
        via_vss_ref = comp << via_vss
        via_vb_ref = comp << via_vb

        # Position vias aligned to their respective ports
        align_comp_to_port(via_vref_ref, vref_port, alignment=('c', 'c'))
        align_comp_to_port(via_vcopy_ref, vcopy_port, alignment=('c', 'c'))
        align_comp_to_port(via_vss_ref, vss_port, alignment=('c', 'c'))
        align_comp_to_port(via_vb_ref, vb_port, alignment=('c', 'c'))

        # Move vias outside the tapring with displacement
        try:
            # Calculate displacement to move vias outside tapring
            tie_w_port = cmirror_ref.ports["CM_Mref_tie_W_bottom_lay_W"]
            tie_e_port = cmirror_ref.ports["CM_Mmirror_tie_E_bottom_lay_E"]
            
            # Move VREF and VSS to the left
            via_vref_ref.movex(-abs(vref_port.center[0] - tie_w_port.center[0]) - via_width - self.extra_port_vias_x_displacement)
            via_vss_ref.movex(-abs(vss_port.center[0] - tie_w_port.center[0]) - via_width - self.extra_port_vias_x_displacement)
            
            # Move VCOPY and VB to the right  
            via_vcopy_ref.movex(abs(vcopy_port.center[0] - tie_e_port.center[0]) + via_width + self.extra_port_vias_x_displacement)
            via_vb_ref.movex(abs(vb_port.center[0] - tie_e_port.center[0]) + via_width + self.extra_port_vias_x_displacement)
            
        except KeyError:
            # Fallback positioning if tie ports not found
            via_vref_ref.movex(-self.extra_port_vias_x_displacement)
            via_vcopy_ref.movex(self.extra_port_vias_x_displacement)
            via_vss_ref.movex(-self.extra_port_vias_x_displacement)
            via_vb_ref.movex(self.extra_port_vias_x_displacement)

        # Route vias to their corresponding ports
        try:
            comp << straight_route(self.pdk, 
                    via_vref_ref.ports["bottom_lay_W"], 
                    vref_port)
            comp << straight_route(self.pdk, 
                    via_vcopy_ref.ports["bottom_lay_W"], 
                    vcopy_port)
            comp << straight_route(self.pdk, 
                    via_vss_ref.ports["bottom_lay_W"], 
                    vss_port)
            comp << straight_route(self.pdk, 
                    via_vb_ref.ports["bottom_lay_W"], 
                    vb_port)
        except Exception as e:
            print(f"Warning: Could not route via connections: {e}")

        return via_vref_ref, via_vcopy_ref, via_vss_ref, via_vb_ref

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

    def _add_cmirror_routing(self, 
            cm_component: Component
            ) -> Component:
        """
        Add proper current mirror routing connections:
        1. Connect sources together (VSS)
        2. Connect gates together (to form bias network)
        3. Connect gate of reference to its drain (for diode connection)
        
        Args:
            cm_component: Component containing the interdigitized current mirror
        
        Returns:
            Component: Component with routing added
        """
        cm_component.unlock()
        
        # Route sources together (VSS connection)
        try:
            source_route = straight_route(
                self.pdk, 
                cm_component.ports["CM_Mref_source_W"], 
                cm_component.ports["CM_Mmirror_source_W"]
            )
            cm_component << source_route
        except KeyError as e:
            print(f"Warning: Could not find source ports for VSS connection: {e}")
            # Try alternative port names from multiplier
            try:
                source_route = straight_route(
                    self.pdk, 
                    cm_component.ports["CM_Mref_source_E"], 
                    cm_component.ports["CM_Mmirror_source_E"]
                )
                cm_component << source_route
            except KeyError:
                print("Warning: Could not find any source ports for VSS connection")
        
        # Route gates together (bias network)
        try:
            gate_route = straight_route(
                self.pdk, 
                cm_component.ports["CM_Mref_gate_E"], 
                cm_component.ports["CM_Mmirror_gate_E"]
            )
            cm_component << gate_route
            
            # Connect reference transistor gate to its drain (diode connection)
            gate_drain_route = c_route(
                self.pdk, 
                cm_component.ports["CM_Mref_gate_W"], 
                cm_component.ports["CM_Mref_drain_W"],
                extension=self.pdk.util_max_metal_seperation()
            )
            cm_component << gate_drain_route
            
        except KeyError as e:
            print(f"Warning: Could not find gate/drain ports for bias connection: {e}")
            # Try alternative approach with different orientations
            try:
                gate_route = straight_route(
                    self.pdk, 
                    cm_component.ports["CM_Mref_gate_S"], 
                    cm_component.ports["CM_Mmirror_gate_S"]
                )
                cm_component << gate_route
                
                # Connect reference transistor gate to its drain (diode connection)
                gate_drain_route = c_route(
                    self.pdk, 
                    cm_component.ports["CM_Mref_gate_N"], 
                    cm_component.ports["CM_Mref_drain_N"],
                    extension=self.pdk.util_max_metal_seperation()
                )
                cm_component << gate_drain_route
            except KeyError:
                print("Warning: Could not find any gate/drain ports for bias connection")
        
        return cm_component

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
        
        """
        # Add routing
        self._add_cmirror_routing(cmirror)
        
        # Create vias outside tapring
        (via_vref_ref, via_vcopy_ref, 
         via_vss_ref, via_vb_ref) = self._create_cmirror_vias_outside_tapring_and_route()
        
        # Add pins and labels
        self._add_pin_and_label_to_via(self.top_level, via_vref_ref, "VREF")
        self._add_pin_and_label_to_via(self.top_level, via_vcopy_ref, "VCOPY")
        self._add_pin_and_label_to_via(self.top_level, via_vss_ref, "VSS")
        self._add_pin_and_label_to_via(self.top_level, via_vb_ref, "VB")
        
        # TODO: Add decoupling capacitor
        # This would typically be a MOM capacitor or MIM capacitor
        # Implementation depends on PDK capabilities
        """
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
    cmirror_config = CMirrorConfig(
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
        with_dnwell = False
    )
    
    # Create current mirror instance
    cmirror = CmirrorWithDecap(
        pdk=pdk_choice,
        width_ref=3,
        width_mir=1,
        fingers_ref=3,
        fingers_mir=1,
        length=0.28,
        cmirror_config=cmirror_config
    )
    
    # Build the current mirror
    print("Building current mirror...")
    component = cmirror.build()
    
    # Write GDS
    print("✓ Writing GDS files...")
    cmirror.write_gds('lvs/gds/Cmirror_with_decap.gds')
    print("  - Hierarchical GDS: Cmirror_with_decap.gds")
    
    # Run DRC
    print("\n...Running DRC...")
    drc_result = cmirror.run_drc()
    if drc_result:
        print(f"✓ Magic DRC result: {drc_result}")
    
    print("\n" + "="*60)
    print("CURRENT MIRROR DESIGN COMPLETED!")
    print("="*60)
   
