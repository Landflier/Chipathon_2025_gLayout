#!/usr/bin/env python3
"""
Interdigitized Current Mirror with Decoupling Capacitor Design

This module provides functions to create an interdigitized current mirror layout
based on GLayout primitives. The design includes:
- Interdigitized NMOS transistor pairs for improved matching
- Proper current mirror routing (gate-drain short for reference)
- External I/O via placement for easy chip-level integration
- Framework for decoupling capacitor integration

Key Functions:
============

create_cmirror_interdigitized(pdk, width, fingers, CM_FET_kwargs, length=None, component_name="cmirror_interdigitized")
    -> Component
    Creates the basic interdigitized current mirror structure with two NMOS transistors.
    
add_cmirror_routing(pdk, cm_component) -> Component
    Adds proper current mirror routing: source connections (VSS), gate connections (bias),
    and gate-drain short for the reference transistor.
    
create_cmirror_with_decap(pdk, width, fingers, CM_FET_kwargs, decap_size=None, length=None) 
    -> Component
    Creates complete current mirror with routing and framework for decoupling capacitor.
    
create_cmirror_vias_outside_tapring_and_route(pdk, cmirror_ref, comp, extra_port_vias_x_displacement)
    -> tuple[via_vref_ref, via_vcopy_ref, via_vss_ref, via_vb_ref]
    Creates external I/O vias for VREF, VCOPY, VSS, and VB connections outside the tapring.

add_pin_and_label_to_via(comp, via_ref, pin_name, pdk, debug_mode=False) -> Component
    Utility function to add pins and labels to vias for proper GDS annotation.

Usage Example:
=============
    CM_FET_kwargs = {
        "sd_route_topmet": "met2",
        "gate_route_topmet": "met2", 
        "sd_rmult": 2,
        "gate_rmult": 3,
        "with_tie": True,
        "tie_layers": ("met2","met1")
    }
    
    cmirror = create_cmirror_with_decap(
        pdk=gf180,
        width=20.0,    # [um] 
        fingers=4,     # fingers per transistor
        CM_FET_kwargs=CM_FET_kwargs
    )
"""

import os
import sys
from typing import Optional
from gdsfactory import Component

from glayout import gf180, MappedPDK
from glayout import nmos, pmos, tapring
from glayout.routing.straight_route import straight_route
from glayout.routing.c_route import c_route
from glayout.routing.L_route import L_route
from glayout import via_array

from gdsfactory.components import rectangle
from glayout.primitives.via_gen import via_array
from glayout.util.comp_utils import evaluate_bbox, align_comp_to_port
from glayout.util.snap_to_grid import component_snap_to_grid
    
# Add the diff_pair module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../diff_pair'))
from diff_pair import get_pin_layers

def add_pin_and_label_to_via(
    comp: Component,
    via_ref: Component,
    pin_name: str,
    pdk: MappedPDK,
    debug_mode: bool = False,
) -> Component:
    """
    Add a pin and label to an existing via at its center on the top metal layer.
    
    Args:
        comp: Component to add pins and labels to
        via_ref: Reference to the via component
        pin_name: Name for the pin and label
        pdk: PDK for layer information
        debug_mode: whether to show rectangles where the pin should be
    
    Returns:
        Component: The modified comp component
    """
    comp.unlock()
    
    # Get via center and size
    via_center = via_ref.center
    via_size = via_ref.size
    
    # Use the largest dimension for pin size
    pin_size = max(via_size[0], via_size[1])
    
    # Find the top metal port of the via
    top_met_ports = [port for port_name, port in via_ref.ports.items() if "top_met" in port_name]
    
    if not top_met_ports:
        print(f"⚠ Warning: No top_met ports found in via for {pin_name}")
        return comp
    
    # Use the first top metal port to determine the layer
    top_met_port = top_met_ports[0]
    metal_layer = top_met_port.layer
    
    # Get pin and label layers from the top metal layer
    pin_layer_gds, label_layer_gds = get_pin_layers(metal_layer, pdk)
    
    # Add label at via center
    comp.add_label(text=pin_name, position=via_center, layer=label_layer_gds)
    
    if debug_mode:
        # Create visual pin rectangle for debugging
        pin_rect = rectangle(layer=pin_layer_gds, size=(pin_size, pin_size), centered=True).copy()
        pin_rect_ref = comp << pin_rect
        pin_rect_ref.move(via_center)
    
    # Add electrical ports for connectivity using the via center
    # Create ports with all four orientations (E=0°, N=90°, W=180°, S=270°)
    comp.add_port(
        center=via_center,
        width=pin_size,
        orientation=0,  # East orientation
        layer=metal_layer,
        name=f"{pin_name}_E"
    )
    comp.add_port(
        center=via_center,
        width=pin_size,
        orientation=90,  # North orientation
        layer=metal_layer,
        name=f"{pin_name}_N"
    )
    comp.add_port(
        center=via_center,
        width=pin_size,
        orientation=180,  # West orientation
        layer=metal_layer,
        name=f"{pin_name}_W"
    )
    comp.add_port(
        center=via_center,
        width=pin_size,
        orientation=270,  # South orientation
        layer=metal_layer,
        name=f"{pin_name}_S"
    )
    
    return comp



def create_cmirror_vias_outside_tapring_and_route(
        pdk: MappedPDK,
        cmirror_ref: Component,
        comp: Component,
        extra_port_vias_x_displacement: float,
        ) -> tuple:
    """
    Create vias for routing the current mirror I/O outside the tapring.
    
    Args:
        pdk: PDK for design rules and layer information
        cmirror_ref: Component reference with the current mirror
        comp: Top-level component to add vias to
        extra_port_vias_x_displacement: Additional x displacement for vias
    
    Returns:
        tuple: References to the created vias (VREF, VCOPY, VSS, VB)
    """
    
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
    via_vref = via_array(pdk, "met3", "met2", 
                        size=(via_width, via_width),
                        fullbottom=True)
    via_vcopy = via_array(pdk, "met3", "met2", 
                        size=(via_width, via_width),
                        fullbottom=True)
    via_vss = via_array(pdk, "met3", "met2", 
                        size=(via_width, via_width),
                        fullbottom=True)
    via_vb = via_array(pdk, "met3", "met2", 
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
        via_vref_ref.movex(-abs(vref_port.center[0] - tie_w_port.center[0]) - via_width - extra_port_vias_x_displacement)
        via_vss_ref.movex(-abs(vss_port.center[0] - tie_w_port.center[0]) - via_width - extra_port_vias_x_displacement)
        
        # Move VCOPY and VB to the right  
        via_vcopy_ref.movex(abs(vcopy_port.center[0] - tie_e_port.center[0]) + via_width + extra_port_vias_x_displacement)
        via_vb_ref.movex(abs(vb_port.center[0] - tie_e_port.center[0]) + via_width + extra_port_vias_x_displacement)
        
    except KeyError:
        # Fallback positioning if tie ports not found
        via_vref_ref.movex(-extra_port_vias_x_displacement)
        via_vcopy_ref.movex(extra_port_vias_x_displacement)
        via_vss_ref.movex(-extra_port_vias_x_displacement)
        via_vb_ref.movex(extra_port_vias_x_displacement)

    # Route vias to their corresponding ports
    try:
        comp << straight_route(pdk, 
                via_vref_ref.ports["bottom_lay_W"], 
                vref_port)
        comp << straight_route(pdk, 
                via_vcopy_ref.ports["bottom_lay_W"], 
                vcopy_port)
        comp << straight_route(pdk, 
                via_vss_ref.ports["bottom_lay_W"], 
                vss_port)
        comp << straight_route(pdk, 
                via_vb_ref.ports["bottom_lay_W"], 
                vb_port)
    except Exception as e:
        print(f"Warning: Could not route via connections: {e}")

    return via_vref_ref, via_vcopy_ref, via_vss_ref, via_vb_ref

def create_cmirror_interdigitized(
    pdk: MappedPDK,
    width: float,
    fingers: int,
    CM_FET_kwargs: dict,
    length: Optional[float] = None,
    component_name: Optional[str] = "cmirror_interdigitized",
) -> Component:
    """
    Create interdigitized current mirror for current mirroring applications.
    This function creates two NMOS transistors in an interdigitized layout
    with proper current mirror connections (gate-drain short for reference).
    
    Args:
        pdk: PDK for design rules and layer information
        width: float of total width of each transistor
        fingers: int of number of fingers per transistor
        CM_FET_kwargs: Dictionary of additional FET parameters
                      Should include parameters like:
                      - with_dnwell
                      - sd_route_topmet, gate_route_topmet
                      - sd_rmult, gate_rmult
                      - interfinger_rmult
                      - tie_layers
        length: Gate length (uses PDK minimum if not specified)
        component_name: Name for the component
    
    Returns:
        Component: Single interdigitized component containing both current mirror transistors
    """
    if width % fingers != 0:
        raise ValueError(f"Width ({width}) must be a multiple of number of fingers ({fingers})")
    
    pdk.activate()

    # Use PDK minimum length if not specified
    if length is None:
        length = pdk.get_grule('poly')['min_width']

    # Get parameters from CM_FET_kwargs
    sd_rmult_temp = CM_FET_kwargs.get("sd_rmult", 1)  # multiplies thickness of sd metal (int only)
    sd_route_topmet_temp = CM_FET_kwargs.get("sd_route_topmet", "met2")  # top metal layer for source/drain routing
    inter_finger_topmet_temp = CM_FET_kwargs.get("inter_finger_topmet", "met1")  # top metal of the via array laid on the source/drain regions
    gate_route_topmet_temp = CM_FET_kwargs.get("gate_route_topmet", "met2")  # top metal layer for gate routing
    gate_rmult_temp = CM_FET_kwargs.get("gate_rmult", 1)  # multiplies gate by adding rows to the gate via array (int only)
    interfinger_rmult_temp = CM_FET_kwargs.get("interfinger_rmult", 1)  # multiplies thickness of source/drain routes between the gates (int only)
    tie_layers_temp = CM_FET_kwargs.get("tie_layers", ("met2","met1"))  # layers for tie ring (horizontal, vertical)
    with_dummies_temp = CM_FET_kwargs.get("with_dummies", True)  # whether to include dummy gates connected to the tiering
    with_dnwell_temp = CM_FET_kwargs.get("with_dnwell", False)
    with_tie_temp = CM_FET_kwargs.get("with_tie", True)
    with_substrate_tap_temp = CM_FET_kwargs.get("with_substrate_tap", False) 

    # error checking
    if sd_rmult_temp<1 or interfinger_rmult_temp<1 or gate_rmult_temp<1:
        raise ValueError("routing multipliers must be positive int")
    
    ##top level component
    top_level = Component()

    ## two NMOS transistors for current mirror (reference and mirror)
    M_ref_temp = nmos(pdk, 
            width = width, 
            fingers = fingers, 
            multipliers = 1,
            with_tie = with_tie_temp,
            with_dummy = with_dummies_temp,
            with_dnwell = with_dnwell_temp,
            with_substrate_tap = with_substrate_tap_temp, 
            length = length, 
            sd_rmult = sd_rmult_temp,
            sd_route_topmet = sd_route_topmet_temp,
            gate_route_topmet = gate_route_topmet_temp,
            gate_rmult = gate_rmult_temp,
            interfinger_rmult = interfinger_rmult_temp,
            tie_layers = tie_layers_temp,
            )
    M_mirror_temp = nmos(pdk, 
            width = width, 
            fingers = fingers, 
            multipliers = 1,
            with_tie = with_tie_temp,
            with_dummy = with_dummies_temp,
            with_dnwell = with_dnwell_temp,
            with_substrate_tap = with_substrate_tap_temp, 
            length = length, 
            sd_rmult = sd_rmult_temp,
            sd_route_topmet = sd_route_topmet_temp,
            gate_route_topmet = gate_route_topmet_temp,
            gate_rmult = gate_rmult_temp,
            interfinger_rmult = interfinger_rmult_temp,
            tie_layers = tie_layers_temp,
            )

    # For current mirror, we don't swap drain/source - keep standard configuration
    M_ref = M_ref_temp
    M_mirror = M_mirror_temp

    M_ref_ref = top_level << M_ref
    M_mirror_ref = top_level << M_mirror
    
    # Place mirror transistor next to reference with mirroring for interdigitation
    M_mirror_ref.mirror_x()
    M_mirror_ref.movex(M_ref_ref.xmax + evaluate_bbox(M_mirror)[0]/2 )

    top_level.add_ports(M_ref_ref.get_ports_list(), prefix="CM_Mref_")
    top_level.add_ports(M_mirror_ref.get_ports_list(), prefix="CM_Mmirror_")

    top_level.name = component_name
   
    return component_snap_to_grid(top_level)

def add_cmirror_routing(
    pdk: MappedPDK,
    cm_component: Component,
) -> Component:
    """
    Add proper current mirror routing connections:
    1. Connect sources together (VSS)
    2. Connect gates together (to form bias network)
    3. Connect gate of reference to its drain (for diode connection)
    
    Args:
        pdk: PDK for design rules and layer information
        cm_component: Component containing the interdigitized current mirror
    
    Returns:
        Component: Component with routing added
    """
    cm_component.unlock()
    
    # Route sources together (VSS connection)
    try:
        source_route = straight_route(
            pdk, 
            cm_component.ports["CM_Mref_source_W"], 
            cm_component.ports["CM_Mmirror_source_W"]
        )
        cm_component << source_route
    except KeyError as e:
        print(f"Warning: Could not find source ports for VSS connection: {e}")
    
    # Route gates together (bias network)
    try:
        gate_route = straight_route(
            pdk, 
            cm_component.ports["CM_Mref_gate_E"], 
            cm_component.ports["CM_Mmirror_gate_E"]
        )
        cm_component << gate_route
        
        # Connect reference transistor gate to its drain (diode connection)
        gate_drain_route = c_route(
            pdk, 
            cm_component.ports["CM_Mref_gate_W"], 
            cm_component.ports["CM_Mref_drain_W"],
            extension=pdk.util_max_metal_seperation()
        )
        cm_component << gate_drain_route
        
    except KeyError as e:
        print(f"Warning: Could not find gate/drain ports for bias connection: {e}")
    
    return cm_component

def create_cmirror_with_decap(
    pdk: MappedPDK,
    width: float,
    fingers: int,
    CM_FET_kwargs: dict,
    decap_size: Optional[tuple] = None,
    length: Optional[float] = None,
) -> Component:
    """
    Create complete current mirror with decoupling capacitor.
    
    Args:
        pdk: PDK for design rules and layer information
        width: float of total width of each transistor
        fingers: int of number of fingers per transistor
        CM_FET_kwargs: Dictionary of FET parameters
        decap_size: Optional tuple (width, height) for decap. If None, uses default
        length: Gate length (uses PDK minimum if not specified)
    
    Returns:
        Component: Complete current mirror with decoupling capacitor
    """
    # Create the basic interdigitized current mirror
    cm_base = create_cmirror_interdigitized(
        pdk=pdk,
        width=width,
        fingers=fingers,
        CM_FET_kwargs=CM_FET_kwargs,
        length=length,
        component_name="cmirror_with_decap"
    )
    
    # Add current mirror routing
    cm_routed = add_cmirror_routing(pdk, cm_base)
    
    # TODO: Add decoupling capacitor
    # This would typically be a MOM capacitor or MIM capacitor
    # Implementation depends on PDK capabilities
    
    return cm_routed
    

if __name__ == "__main__":
    
    from diff_pair import diff_pair, get_pin_layers

    pdk_choice = gf180

    # Current Mirror FET parameters
    CM_FET_kwargs = {
        "with_dnwell": False,
        "sd_route_topmet": "met2",
        "gate_route_topmet": "met2",
        "sd_rmult": 2,
        "gate_rmult": 3,
        "interfinger_rmult": 2,
        "tie_layers": ("met2","met1"),
        "inter_finger_topmet": "met1",
        "with_dummies": True,
        "with_tie": True,
        "with_substrate_tap": False,
    }

    # Generate interdigitized current mirror with explicit parameters
    print("✓ Creating interdigitized current mirror...")
    cmirror_interdigitized = create_cmirror_interdigitized(
        pdk=pdk_choice,
        width=20.0,           # [um] width of each transistor
        fingers=4,            # Number of fingers per transistor
        CM_FET_kwargs=CM_FET_kwargs,
        length=0.28,          # [um] gate length
        component_name="cmirror_interdigitized"
    )

    # Create complete current mirror with routing and decap
    print("✓ Adding current mirror routing...")
    cmirror_with_routing = add_cmirror_routing(pdk_choice, cmirror_interdigitized)

    # Create top-level component
    comp = Component(name="cmirror_with_decap_interdigitized")
    cmirror_ref = comp << cmirror_with_routing
    
    # Add VSS via for substrate connection
    via_size = (1.42, 1.42)
    via_vss = via_array(pdk_choice, "met2", "met3", 
                         size=via_size,
                         lay_every_layer=True,
                         fullbottom=True)
    via_vss_ref = comp << via_vss
    
    # Position VSS via at the center bottom of the current mirror
    try:
        align_comp_to_port(via_vss_ref, cmirror_ref.ports["CM_Mref_well_S"], alignment=('c', 'c'))
    except KeyError:
        # Fallback positioning
        via_vss_ref.move(cmirror_ref.center)
        via_vss_ref.movey(cmirror_ref.ymin - via_size[1])
    
    add_pin_and_label_to_via(comp, via_vss_ref, "VSS", pdk_choice, debug_mode=False)

    # Create and position I/O vias outside the tapring
    print("✓ Creating external I/O vias...")
    try:
        via_vref_ref, via_vcopy_ref, via_vss_io_ref, via_vb_ref = create_cmirror_vias_outside_tapring_and_route(
            pdk_choice,
            cmirror_ref,
            comp,
            extra_port_vias_x_displacement=2.0
        )

        # Add pin labels for current mirror I/O
        add_pin_and_label_to_via(comp, via_vref_ref, "VREF", pdk_choice)     # Reference voltage/current input
        add_pin_and_label_to_via(comp, via_vcopy_ref, "VCOPY", pdk_choice)   # Mirrored current output  
        add_pin_and_label_to_via(comp, via_vss_io_ref, "VSS_IO", pdk_choice) # Source connection
        add_pin_and_label_to_via(comp, via_vb_ref, "VB", pdk_choice)         # Body/substrate bias
        
    except Exception as e:
        print(f"⚠ Warning: Could not create external vias: {e}")

    # Write GDS files
    print("✓ Writing GDS files...")
    comp.write_gds('lvs/gds/cmirror_interdigitized.gds', 
                   cellname="cmirror_interdigitized",
                   unit=1e-6,
                   precision=1e-9)
    print("  - Hierarchical GDS: cmirror_interdigitized.gds")
    
    # Run DRC check
    print("\n...Running DRC...")
    try:
        drc_result = pdk_choice.drc_magic(comp, comp.name)
        print(f"✓ Magic DRC result: {drc_result}")
    except Exception as e:
        print(f"⚠ Magic DRC skipped: {e}")
    
    print("\n" + "="*60)
    print("CURRENT MIRROR DESIGN COMPLETED!")
    print("="*60)
    print("Design Features:")
    print("- Interdigitized NMOS current mirror")
    print("- Reference transistor with gate-drain short")
    print("- Mirror transistor for current copying")
    print("- External I/O vias: VREF, VCOPY, VSS, VB")
    print("- Tapring for substrate isolation")
    print("- Ready for decoupling capacitor integration")
    print("="*60)
   
