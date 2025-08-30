
from glayout import MappedPDK, sky130 , gf180
from gdsfactory.cell import cell
from gdsfactory import Component
from gdsfactory.components import text_freetype, rectangle

from glayout import nmos, pmos, multiplier
from glayout import via_stack, via_array
from glayout import rename_ports_by_orientation
from glayout import tapring

from glayout.util.comp_utils import evaluate_bbox, prec_center, prec_ref_center, align_comp_to_port
from glayout.util.comp_utils import move, movex, movey
from glayout.util.port_utils import PortTree, rename_ports_by_orientation
from glayout.util.port_utils import add_ports_perimeter,print_ports
from glayout.util.snap_to_grid import component_snap_to_grid
from glayout.spice.netlist import Netlist


from glayout.routing.straight_route import straight_route
from glayout.routing.c_route import c_route
from glayout.routing.L_route import L_route

import numpy as np
import os
import subprocess

# Run a shell, source .bashrc, then printenv
cmd = 'bash -c "source ~/.bashrc && printenv"'
result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
env_vars = {}
for line in result.stdout.splitlines():
    if '=' in line:
        key, value = line.split('=', 1)
        env_vars[key] = value

# Now, update os.environ with these
os.environ.update(env_vars)

# Swap drain-source ports, to ease connections

def swap_drain_source_ports(mosfet_component):
    """
    Swap all drain and source port names in a MOSFET component.
    This effectively makes the drain become the source and vice versa.
    
    Args:
        mosfet_component: The MOSFET component to modify
        
    Returns:
        Modified component with swapped drain/source port names
    """
    
    # Make sure component is unlocked for modification
    mosfet_component.unlock()
    
    # Get all ports
    all_ports = list(mosfet_component.ports.items())
    
    # Create mapping of old names to new names
    port_name_mapping = {}
    
    for port_name, port in all_ports:
        new_name = port_name
        
        # Swap drain -> source
        if "drain" in port_name.lower():
            new_name = port_name.replace("drain", "source").replace("DRAIN", "SOURCE")
        # Swap source -> drain  
        elif "source" in port_name.lower():
            new_name = port_name.replace("source", "drain").replace("SOURCE", "DRAIN")
        
        port_name_mapping[port_name] = new_name
    
    # Remove all old ports and add them back with new names
    # Store port information first
    port_info = {}
    for old_name, port in all_ports:
        port_info[old_name] = {
            'center': port.center,
            'width': port.width,
            'orientation': port.orientation,
            'layer': port.layer,
            'port_type': getattr(port, 'port_type', None)
        }
    
    # Clear existing ports
    mosfet_component.ports.clear()
    
    # Add ports back with new names
    for old_name, new_name in port_name_mapping.items():
        info = port_info[old_name]
        try:
            mosfet_component.add_port(
                name=new_name,
                center=info['center'],
                width=info['width'], 
                orientation=info['orientation'],
                layer=info['layer']
            )
        except Exception as e:
            print(f"Warning: Could not rename port {old_name} to {new_name}: {e}")
    
    return mosfet_component

# Get dynamic layers from the actual port layers
def create_and_connect_tapring(top_level, M1_ref, M2_ref, pdk, placement, diff_pair_center, debug_mode=True, comp_name="diff_pair"):
    """
    Create tapring around the differential pair and connect dummy devices to it.
    Also adds a GND pin connected to the tapring.
    
    Args:
        top_level: Main component to add tapring to
        M1_ref: Reference to M1 transistor
        M2_ref: Reference to M2 transistor  
        pdk: Process design kit
        placement: "vertical" or "horizontal" placement
        diff_pair_center: Center coordinates of the differential pair
        comp_name: Component name to use as prefix for port names (default: "diff_pair")
        debug_mode: whether to place phsyical rectangles where pin names are
        
    Returns:
        None (modifies top_level in place)
    """
    ## Create the tapring with appropriate parameters
    ## Using substrate tap for NMOS devices in bulk
    tapring_comp = tapring(
        pdk=pdk,
        enclosed_rectangle=evaluate_bbox(top_level, padding=pdk.get_grule("nwell", "active_diff")["min_enclosure"])
    )
    
    ## Center the tapring around the differential pair
    tapring_ref = top_level << tapring_comp
    tapring_ref.name = "bulk_tapring_diff_pair"
    tapring_ref.move(diff_pair_center)

    ## connect up the dummy transistors to the tapring
    ## Get connection points for all devices
    if placement == "vertical":
        device_gdscons = {
            'M1_L': M1_ref.ports["multiplier_0_dummy_L_gsdcon_bottom_met_E"].center,
            'M1_R': M1_ref.ports["multiplier_0_dummy_R_gsdcon_bottom_met_W"].center,
            'M2_L': M2_ref.ports["multiplier_0_dummy_L_gsdcon_bottom_met_E"].center,
            'M2_R': M2_ref.ports["multiplier_0_dummy_R_gsdcon_bottom_met_W"].center
        }
    if placement == "horizontal":
        device_gdscons = {
            'M1_L': M1_ref.ports["multiplier_0_dummy_L_gsdcon_bottom_met_N"].center,
            'M1_R': M1_ref.ports["multiplier_0_dummy_R_gsdcon_bottom_met_S"].center,
            'M2_L': M2_ref.ports["multiplier_0_dummy_L_gsdcon_bottom_met_N"].center,
            'M2_R': M2_ref.ports["multiplier_0_dummy_R_gsdcon_bottom_met_S"].center
        }
        
    ## Get all tapring ports with "bottom_met" in name
    ## this gets the closest ports along the west and east wall of the tapring (works for vertical placement only)
    if placement == "vertical":
        tapring_ports = [port for port in tapring_ref.get_ports_list() if "bottom_met" in port.name.lower() and ("E_array" in port.name or "W_array" in port.name)]
    if placement == "horizontal":
        tapring_ports = [port for port in tapring_ref.get_ports_list() if "bottom_met" in port.name.lower() and ("S_array" in port.name or "N_array" in port.name)]
    
    def find_closest_port(target_pos, ports):
        #Find the closest port to a target position.
        distances = [(np.linalg.norm(np.array(target_pos) - np.array(port.center)), port) 
                     for port in ports]
        return min(distances, key=lambda x: x[0])[1]
    
    ## Create routes for all connections
    for device_name, gdscon_pos in device_gdscons.items():
        device_port_name = f"multiplier_0_dummy_{'L' if 'L' in device_name else 'R'}_gsdcon_bottom_met_{'E' if 'L' in device_name else 'W'}"
        device_ref = M1_ref if 'M1' in device_name else M2_ref

        closest_tapring_port = find_closest_port(gdscon_pos, tapring_ports)
        try:
            top_level << straight_route(pdk, device_ref.ports[device_port_name], tapring_ref.ports[closest_tapring_port.name])
        except:
            top_level << c_route(pdk, device_ref.ports[device_port_name], tapring_ref.ports[closest_tapring_port.name])
    
    ## Add GND pin connected to the tapring

    # Find a suitable tapring port for VSS connection (use the first available port)
    all_tapring_ports = [port for port in tapring_ref.get_ports_list() if "bottom_met" in port.name.lower()]
    if all_tapring_ports:
        vss_tapring_port = all_tapring_ports[0]  # Use first available port
        
        # Get the port properties for creating the VSS pin
        vss_port_center = vss_tapring_port.center
        vss_port_width = vss_tapring_port.width
        vss_port_layer = vss_tapring_port.layer
        
        # Get pin and label layers for the VSS pin
        vss_pin_layer, vss_label_layer = get_pin_layers(vss_port_layer, pdk)
        
        # Create visual VSS pin rectangle (if debug mode would be enabled)
        if debug_mode:
            vss_label = rectangle(layer=vss_pin_layer, size=(vss_port_width, vss_port_width), centered=True).copy()
            vss_label.add_label(text="VSS", layer=vss_label_layer)
            # Add the visual pin to the component
            vss_label_ref = top_level << vss_label
            vss_label_ref.move(vss_port_center)
        else: 
            top_level.add_label(text="VSS", position=vss_tapring_port.center, layer=vss_label_layer)
        # Add electrical ports for VSS connectivity (all four orientations)
        top_level.add_port(center=vss_port_center, width=vss_port_width, orientation=0, layer=vss_port_layer, name=f"{comp_name}_VSS_E")
        top_level.add_port(center=vss_port_center, width=vss_port_width, orientation=90, layer=vss_port_layer, name=f"{comp_name}_VSS_N")
        top_level.add_port(center=vss_port_center, width=vss_port_width, orientation=180, layer=vss_port_layer, name=f"{comp_name}_VSS_W")
        top_level.add_port(center=vss_port_center, width=vss_port_width, orientation=270, layer=vss_port_layer, name=f"{comp_name}_VSS_S")


def get_pin_layers(port_layer, pdk=None):
    # Convert port layer to corresponding pin and label layers
    # Get all available metal layers from PDK to find which one matches
    if pdk is not None:
        metal_layers = {
            pdk.get_glayer("met1"): ("met1_pin", "met1_label"),
            pdk.get_glayer("met2"): ("met2_pin", "met2_label"), 
            pdk.get_glayer("met3"): ("met3_pin", "met3_label"),
            pdk.get_glayer("met4"): ("met4_pin", "met4_label"),
            pdk.get_glayer("met5"): ("met5_pin", "met5_label"),
        }
        
        # Find matching metal layer
        for metal_layer, (pin_name, label_name) in metal_layers.items():
            if port_layer == metal_layer:
                try:
                    return pdk.get_glayer(pin_name), pdk.get_glayer(label_name)
                except:
                    # If pin/label layers don't exist, use the metal layer itself
                    return port_layer, port_layer
    
    # Default fallback - use the port layer itself
    return port_layer, port_layer

# Calculate the center of a FET terminal, from any number of ports
def calculate_terminal_center(ports):
    """
    Calculate the center point of a terminal by averaging the center coordinates 
    of any number of ports.

    Args:
        ports: Tuple or list of Port objects to average over

    Returns:
        tuple: (x, y) coordinates of the terminal center
    """
    # Get center coordinates of all ports
    centers = [port.center for port in ports]

    # Average the coordinates
    center_array = np.array(centers)
    average_center = np.mean(center_array, axis=0)

    return tuple(average_center)

def diff_pair_pins(
    top_level: Component,
    M1_ref: Component,
    M2_ref: Component,
    pdk: MappedPDK,
    connected_sources: bool,
    component_name: str = "diff_pair",
    gate_pin_offset_x: float = 0,
    debug_mode: bool = True,
) -> Component:

    top_level.unlock()
    
    # List that will contain all port/component info
    move_info = list()
        
    # TODO: these gate width calculation is a bit sketchy, although it works perfectly. Find another way
    m1_gate_full_width = abs(M1_ref.ports['gate_E'].center[1] - M1_ref.ports['gate_W'].center[1]) 
    m2_gate_full_width = abs(M2_ref.ports['gate_E'].center[1] - M2_ref.ports['gate_W'].center[1]) 


    # If in debug mode, add visual rectangles and pin labels where the electrical ports are
    if debug_mode:
        # M1 Gate pin - dynamic layer from port
        m1_gate_port = M1_ref.ports["multiplier_0_gate_E"]
        m1_gate_pin_layer, m1_gate_label_layer = get_pin_layers(m1_gate_port.layer, pdk)
        m1_gate_label = rectangle(layer=m1_gate_pin_layer, size=(m1_gate_full_width, m1_gate_full_width), centered=True).copy()
        #m1_gate_label = rectangle(layer=m1_gate_pin_layer, size=(2*m1_gate_port.width, 2*m1_gate_port.width), centered=True).copy()
        m1_gate_label.add_label(text="M1_GATE", layer=m1_gate_label_layer)
      
        # M1 Drain pin - dynamic layer from port (drains are always separate)
        m1_drain_port = M1_ref.ports["multiplier_0_drain_W"]
        m1_drain_pin_layer, m1_drain_label_layer = get_pin_layers(m1_drain_port.layer, pdk)
        m1_drain_label = rectangle(layer=m1_drain_pin_layer, size=(m1_drain_port.width, m1_drain_port.width), centered=True).copy()
        m1_drain_label.add_label(text="M1_DRAIN", layer=m1_drain_label_layer)

        # Check if sources should be connected and named accordingly
        if connected_sources:
            # If sources are connected, give them the same name
            source_name = "SOURCE_COMMON"

        else:
            # If sources are separate, give them different names
            source_name = "M2_SOURCE"  # Will be set individually below

            # And place the source pin for M1
            m1_source_port = M1_ref.ports["multiplier_0_source_W"]
            m1_source_pin_layer, m1_source_label_layer = get_pin_layers(m1_source_port.layer, pdk)
            m1_source_label = rectangle(layer=m1_source_pin_layer, size=(m1_source_port.width, m1_source_port.width), centered=True).copy()
            m1_source_label.add_label(text="M1_SOURCE", layer=m1_source_label_layer)
        
        # M2 Source pin - dynamic layer from port, this is the same as M!
        m2_source_port = M1_ref.ports["multiplier_0_source_E"]
        m2_source_pin_layer, m2_source_label_layer = get_pin_layers(m2_source_port.layer, pdk)
        m2_source_label = rectangle(layer=m2_source_pin_layer, size=(m2_source_port.width, m2_source_port.width), centered=True).copy()
        m2_source_label.add_label(text=f"{source_name}", layer=m2_source_label_layer)
        
        # M2 Gate pin - dynamic layer from port
        m2_gate_port = M2_ref.ports["multiplier_0_gate_E"]
        m2_gate_pin_layer, m2_gate_label_layer = get_pin_layers(m2_gate_port.layer, pdk)
        m2_gate_label = rectangle(layer=m2_gate_pin_layer, size=(m2_gate_full_width, m2_gate_full_width), centered=True).copy()
        #m2_gate_label = rectangle(layer=m2_gate_pin_layer, size=(2*m2_gate_port.width, 2*m2_gate_port.width), centered=True).copy()
        m2_gate_label.add_label(text="M2_GATE", layer=m2_gate_label_layer)
        
        
        # M2 Drain pin - dynamic layer from port (drains are always separate)
        m2_drain_port = M2_ref.ports["multiplier_0_drain_W"]
        m2_drain_pin_layer, m2_drain_label_layer = get_pin_layers(m2_drain_port.layer, pdk)
        m2_drain_label = rectangle(layer=m2_drain_pin_layer, size=(m2_drain_port.width, m2_drain_port.width), centered=True).copy()
        m2_drain_label.add_label(text="M2_DRAIN", layer=m2_drain_label_layer)
    
    # Calculate M1 terminal centers
    ## Gate centers are more finicky for some reason. TODO: simpler logic
    m1_gate_center_x = calculate_terminal_center((
        M1_ref.ports["multiplier_0_gate_N"], M1_ref.ports["multiplier_0_gate_S"]
    ))
    m1_gate_center_y = calculate_terminal_center((
        M1_ref.ports["multiplier_0_gate_W"], M1_ref.ports["multiplier_0_gate_E"]
    ))
    m1_gate_center = (m1_gate_center_x[0] + gate_pin_offset_x, m1_gate_center_y[1])

    m1_drain_center = calculate_terminal_center((
        M1_ref.ports["multiplier_0_drain_W"], M1_ref.ports["multiplier_0_drain_E"]
    ))
    m1_source_center = calculate_terminal_center((
        M1_ref.ports["multiplier_0_source_W"], M1_ref.ports["multiplier_0_source_E"]
    ))
    
    # M2 terminal centers
    ## Gate centers are more finicky for some reason. TODO: simpler logic
    m2_gate_center_x = calculate_terminal_center((
        M2_ref.ports["multiplier_0_gate_N"], M2_ref.ports["multiplier_0_gate_S"]
    ))
    m2_gate_center_y = calculate_terminal_center((
        M2_ref.ports["multiplier_0_gate_W"], M2_ref.ports["multiplier_0_gate_E"]
    ))
    m2_gate_center = (m2_gate_center_x[0] + gate_pin_offset_x, m2_gate_center_y[1])

    m2_drain_center = calculate_terminal_center((
        M2_ref.ports["multiplier_0_drain_W"], M2_ref.ports["multiplier_0_drain_E"]
    ))
    m2_source_center = calculate_terminal_center((
        M2_ref.ports["multiplier_0_source_W"], M2_ref.ports["multiplier_0_source_E"]
    ))
    
    if debug_mode:
        # Position visual pins at the same calculated centers as electrical ports
        m1_gate_ref = top_level << m1_gate_label
        m1_gate_ref.move(m1_gate_center)
        
        m1_drain_ref = top_level << m1_drain_label
        m1_drain_ref.move(m1_drain_center)
        
        if not connected_sources:
            m1_source_ref = top_level << m1_source_label
            m1_source_ref.move(m1_source_center)
        
        m2_source_ref = top_level << m2_source_label
        m2_source_ref.move(m2_source_center)
        
        m2_gate_ref = top_level << m2_gate_label
        m2_gate_ref.move(m2_gate_center)
        
        m2_drain_ref = top_level << m2_drain_label
        m2_drain_ref.move(m2_drain_center)
    
    # Add electrical ports for connectivity using the calculated centers
    # Create ports with all four orientations (E=0°, N=90°, W=180°, S=270°)
    
    # M1 Gate ports (all orientations)
    top_level.add_port(center=m1_gate_center, width=m1_gate_full_width, orientation=0, layer=M1_ref.ports["multiplier_0_gate_E"].layer, name=f"{component_name}_M1_GATE_E")
    top_level.add_port(center=m1_gate_center, width=m1_gate_full_width, orientation=90, layer=M1_ref.ports["multiplier_0_gate_E"].layer, name=f"{component_name}_M1_GATE_N")
    top_level.add_port(center=m1_gate_center, width=m1_gate_full_width, orientation=180, layer=M1_ref.ports["multiplier_0_gate_E"].layer, name=f"{component_name}_M1_GATE_W")
    top_level.add_port(center=m1_gate_center, width=m1_gate_full_width, orientation=270, layer=M1_ref.ports["multiplier_0_gate_E"].layer, name=f"{component_name}_M1_GATE_S")
    
    # M2 Gate ports (all orientations)
    top_level.add_port(center=m2_gate_center, width=m2_gate_full_width, orientation=0, layer=M2_ref.ports["multiplier_0_gate_E"].layer, name=f"{component_name}_M2_GATE_E")
    top_level.add_port(center=m2_gate_center, width=m2_gate_full_width, orientation=90, layer=M2_ref.ports["multiplier_0_gate_E"].layer, name=f"{component_name}_M2_GATE_N")
    top_level.add_port(center=m2_gate_center, width=m2_gate_full_width, orientation=180, layer=M2_ref.ports["multiplier_0_gate_E"].layer, name=f"{component_name}_M2_GATE_W")
    top_level.add_port(center=m2_gate_center, width=m2_gate_full_width, orientation=270, layer=M2_ref.ports["multiplier_0_gate_E"].layer, name=f"{component_name}_M2_GATE_S")
    
    # Add drain ports (always separate) - all orientations
    top_level.add_port(center=m1_drain_center, width=M1_ref.ports["drain_W"].width, orientation=0, layer=M1_ref.ports["multiplier_0_source_E"].layer, name=f"{component_name}_M1_DRAIN_E")
    top_level.add_port(center=m1_drain_center, width=M1_ref.ports["drain_W"].width, orientation=90, layer=M1_ref.ports["multiplier_0_source_E"].layer, name=f"{component_name}_M1_DRAIN_N")
    top_level.add_port(center=m1_drain_center, width=M1_ref.ports["drain_W"].width, orientation=180, layer=M1_ref.ports["multiplier_0_source_E"].layer, name=f"{component_name}_M1_DRAIN_W")
    top_level.add_port(center=m1_drain_center, width=M1_ref.ports["drain_W"].width, orientation=270, layer=M1_ref.ports["multiplier_0_source_E"].layer, name=f"{component_name}_M1_DRAIN_S")
    
    top_level.add_port(center=m2_drain_center, width=M2_ref.ports["drain_W"].width, orientation=0, layer=M2_ref.ports["multiplier_0_source_E"].layer, name=f"{component_name}_M2_DRAIN_E")
    top_level.add_port(center=m2_drain_center, width=M2_ref.ports["drain_W"].width, orientation=90, layer=M2_ref.ports["multiplier_0_source_E"].layer, name=f"{component_name}_M2_DRAIN_N")
    top_level.add_port(center=m2_drain_center, width=M2_ref.ports["drain_W"].width, orientation=180, layer=M2_ref.ports["multiplier_0_source_E"].layer, name=f"{component_name}_M2_DRAIN_W")
    top_level.add_port(center=m2_drain_center, width=M2_ref.ports["drain_W"].width, orientation=270, layer=M2_ref.ports["multiplier_0_source_E"].layer, name=f"{component_name}_M2_DRAIN_S")
    
    # Always add ports to both sources, so routing is robust, regardless if sources are connected or not
    # M1 Source ports
    top_level.add_port(center=m1_source_center, width=M1_ref.ports["source_W"].width, orientation=0, layer=M1_ref.ports["multiplier_0_drain_E"].layer, name=f"{component_name}_M1_SOURCE_E")
    top_level.add_port(center=m1_source_center, width=M1_ref.ports["source_W"].width, orientation=90, layer=M1_ref.ports["multiplier_0_drain_E"].layer, name=f"{component_name}_M1_SOURCE_N")
    top_level.add_port(center=m1_source_center, width=M1_ref.ports["source_W"].width, orientation=180, layer=M1_ref.ports["multiplier_0_drain_E"].layer, name=f"{component_name}_M1_SOURCE_W")
    top_level.add_port(center=m1_source_center, width=M1_ref.ports["source_W"].width, orientation=270, layer=M1_ref.ports["multiplier_0_drain_E"].layer, name=f"{component_name}_M1_SOURCE_S")
        
    # M2 Source ports
    top_level.add_port(center=m2_source_center, width=M2_ref.ports["source_W"].width, orientation=0, layer=M2_ref.ports["multiplier_0_drain_E"].layer, name=f"{component_name}_M2_SOURCE_E")
    top_level.add_port(center=m2_source_center, width=M2_ref.ports["source_W"].width, orientation=90, layer=M2_ref.ports["multiplier_0_drain_E"].layer, name=f"{component_name}_M2_SOURCE_N")
    top_level.add_port(center=m2_source_center, width=M2_ref.ports["source_W"].width, orientation=180, layer=M2_ref.ports["multiplier_0_drain_E"].layer, name=f"{component_name}_M2_SOURCE_W")
    top_level.add_port(center=m2_source_center, width=M2_ref.ports["source_W"].width, orientation=270, layer=M2_ref.ports["multiplier_0_drain_E"].layer, name=f"{component_name}_M2_SOURCE_S")
    
    return top_level

    
@cell
def diff_pair(
        pdk: MappedPDK,
        placement: str = "vertical",
        width: tuple[float,float] = (3,3),
        length: tuple[float,float] | None = None,
        fingers: tuple[int,int] = (1,1),
        multipliers: tuple[int,int] = (1,1),
        dummy_1: tuple[bool,bool] = (True,True),
        dummy_2: tuple[bool,bool] = (True,True),
        tie_layers1: tuple[str,str] = ("met2","met1"),
        tie_layers2: tuple[str,str] = ("met2","met1"),
        sd_rmult: int=1,
        connected_sources: bool = True,
        gate_pin_offset_x: float = 0,
        debug_mode: bool = True,
        M1_kwargs: dict = None,
        M2_kwargs: dict = None,
        component_name: str = "diff_pair",
        **kwargs        
        ) -> Component:

    pdk.activate()
    
    ##top level component
    top_level = Component(name=component_name)

    ## two fets
    ## temp mosfets, so we can switch the drain/source ports
    if M1_kwargs is None:
        M1_kwargs = {}
    if M2_kwargs is None:
        M2_kwargs = {}
    
    # Handle length parameter - use None for PDK minimum length
    length1 = length[0] if length is not None else None
    length2 = length[1] if length is not None else None
   
    M1_temp = nmos(pdk, width=width[0], fingers=fingers[0], multipliers=multipliers[0], with_dummy=dummy_1, with_substrate_tap=False, length=length1, tie_layers=tie_layers1,  **M1_kwargs)
    M2_temp = nmos(pdk, width=width[1], fingers=fingers[1], multipliers=multipliers[1], with_dummy=dummy_2, with_substrate_tap=False, length=length2, tie_layers=tie_layers2,  **M2_kwargs)
    
    M1_temp.name=f"{component_name}_M1_temp"
    M2_temp.name=f"{component_name}_M2_temp"

    M1 = swap_drain_source_ports(M1_temp)
    M2 = swap_drain_source_ports(M2_temp)
    
    M1_ref = top_level << M1
    M2_ref = top_level << M2
    
    M1_ref.name=f"{component_name}_M1"
    M2_ref.name=f"{component_name}_M2"
    
    if placement == "horizontal":
        M1_ref.mirror_x()
        M2_ref.movex(M1_ref.xmax + evaluate_bbox(M2)[0]/2 )
        M2_ref.movex(pdk.util_max_metal_seperation()+0.5)
    elif placement == "vertical":
        M1_ref.mirror_y()
        M2_bbox = evaluate_bbox(M2)
        M2_ref.movey(M1_ref.ymin - M2_bbox[1]/2 - pdk.util_max_metal_seperation()-1)
    else:
            raise ValueError("Placement must be either 'horizontal' or 'vertical'.")

    ## connect up the drains/sources of the MOSFETS if connect_sources is set to True
    if connected_sources == True:
        if placement == "vertical" :
            top_level << straight_route(pdk, M1_ref.ports["source_N"], M2_ref.ports["source_N"])
            # top_level << straight_route(pdk, M1_ref.ports["source_N"], M2_ref.ports["source_N"], glayer1="met4")
        if placement == "horizontal" :
            top_level << straight_route(pdk, M1_ref.ports["source_N"], M2_ref.ports["source_E"])

    
    # Tapring surrounding the two transistors
    diff_pair_center = top_level.center
    
    # Create and connect tapring
    create_and_connect_tapring(top_level, M1_ref, M2_ref, pdk, placement, diff_pair_center, debug_mode, component_name)

    #Routing
    top_level_with_pins = diff_pair_pins(top_level, M1_ref, M2_ref, gf180, connected_sources, component_name, gate_pin_offset_x, debug_mode)
    
    return component_snap_to_grid(top_level_with_pins)


if __name__ == "__main__":
    comp = diff_pair(gf180)

    # comp.pprint_ports()
    comp.name = "DIFF_PAIR"
    comp.write_gds('out_diff_pair.gds')
    comp.show()
    print("...Running DRC...")
    drc_result = gf180.drc_magic(comp, "DIFF_PAIR")
    drc_result = gf180.drc(comp)
