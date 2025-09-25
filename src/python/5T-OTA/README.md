# 5T-OTA (5-Transistor Operational Transconductance Amplifier)

## Overview

This module implements a 5-transistor Operational Transconductance Amplifier (OTA) design for the GF180MCU process. The design consists of:

- **PMOS Current Mirror** (2 transistors): Active load providing bias current
- **NMOS Differential Pair** (2 transistors): Input amplification stage
- **Proper routing and connectivity** between all stages

## Design Specifications

### PMOS Current Mirror
- **Width**: 0.3 µm (as specified)
- **Length**: 0.28 µm (minimum length)
- **Configuration**: Without decoupling capacitor
- **Function**: Provides active load and current mirroring

### NMOS Differential Pair  
- **Width**: 1.0 µm (as specified)
- **Length**: 0.28 µm (minimum length)  
- **Configuration**: Common source connection
- **Function**: Differential input amplification

## File Structure

```
5T-OTA/
├── __init__.py                 # Module initialization
├── five_t_ota.py              # Main 5T-OTA implementation
├── README.md                  # This documentation
└── lvs/                       # Layout vs Schematic verification
    ├── custom_netgen_setup.tcl       # Netgen configuration
    ├── extract_5t_ota_layout.sh      # Layout extraction script
    ├── netgen_compare.sh              # LVS comparison script
    ├── gds/                           # Generated GDS files
    └── netlists/                      # Extracted netlists
```

## Usage

### Basic Usage

```python
from glayout import gf180
from five_t_ota import FiveTOTA, OTAConfig

# Create configuration with default specifications
config = OTAConfig(
    pmos_width=0.3,      # 0.3µm PMOS width
    pmos_length=0.28,    # Minimum length
    nmos_width=1.0,      # 1.0µm NMOS width  
    nmos_length=0.28,    # Minimum length
    component_name="my_5T_OTA"
)

# Create and build the OTA
ota = FiveTOTA(pdk=gf180, ota_config=config)
ota_component = ota.build()

# Write GDS file
ota_component.write_gds('lvs/gds/5T_OTA.gds')
```

### Running the Example

```bash
cd src/python/5T-OTA
python five_t_ota.py
```

This will generate:
- `lvs/gds/5T_OTA.gds` - Layout file
- Console output with design summary
- DRC verification (if available)

## Configuration Options

The `OTAConfig` dataclass supports the following parameters:

```python
@dataclass
class OTAConfig:
    # PMOS Current Mirror
    pmos_width: float = 0.3        # Width in µm
    pmos_length: float = 0.28      # Length in µm  
    pmos_fingers: int = 1          # Number of fingers
    pmos_multipliers: int = 1      # Multiplier count
    
    # NMOS Differential Pair
    nmos_width: float = 1.0        # Width in µm
    nmos_length: float = 0.28      # Length in µm
    nmos_fingers: int = 1          # Number of fingers
    nmos_multipliers: int = 1      # Multiplier count
    
    # Layout
    placement: str = "vertical"     # "vertical" or "horizontal"
    component_spacing: float = 2.0  # Spacing in µm
    
    # Routing
    routing_metal: str = "met2"     # Primary routing metal
    via_metal: str = "met1"         # Via metal layer
    
    # Miscellaneous
    debug_mode: bool = True         # Enable debug visualization
    component_name: str = "5T_OTA"  # Component name
```

## Ports

The 5T-OTA provides the following external ports (each with E, N, W, S orientations):

### Input Ports
- `VIN_P_*` - Positive differential input
- `VIN_N_*` - Negative differential input  
- `IBIAS_*` - Bias current input

### Output Ports  
- `VOUT_P_*` - Positive differential output
- `VOUT_N_*` - Negative differential output

### Power Supply Ports
- `VDD_*` - Positive power supply
- `VSS_*` - Negative power supply (ground)

## Layout Verification

### Extract Layout
```bash
cd lvs
./extract_5t_ota_layout.sh
```

This generates:
- `netlists/5T_OTA_extracted_layout.spice` - For LVS comparison
- `netlists/5T_OTA_extracted_layout_PEX.spice` - With parasitic elements

### LVS Comparison
```bash  
cd lvs
./netgen_compare.sh
```

**Note**: Requires reference schematic netlist `5T_OTA_xschem.spice` in `netlists/` directory.

## Dependencies

The module depends on:
- `diff_pair` module (for NMOS differential pair)
- `Cmirror_with_decap` module (for PMOS current mirror)
- `glayout` framework
- `gdsfactory` for layout generation
- GF180MCU PDK

## Design Notes

1. **No Decoupling Capacitor**: The PMOS current mirror is configured without decoupling capacitors as specified.

2. **Minimum Length Transistors**: Both PMOS and NMOS use minimum channel length (0.28µm) for maximum speed.

3. **Differential Architecture**: Full differential design with separate positive and negative signal paths.

4. **Modular Design**: Uses existing verified `diff_pair` and `Cmirror_with_decap` components.

5. **Routing Flexibility**: Multiple port orientations provided for flexible higher-level routing.

## Process Technology

- **Process**: GF180MCU (GlobalFoundries 180nm)
- **Transistor Types**: 
  - PMOS: `sg13_hv_pmos` 
  - NMOS: `sg13_hv_nmos`
- **Metal Layers**: met1, met2 for routing
- **Design Rules**: Compliant with GF180MCU DRC

## Performance Characteristics

The 5T-OTA is designed for:
- **Low power consumption** (minimum length devices)
- **High speed operation** (minimum length devices)  
- **Differential operation** (balanced inputs/outputs)
- **Simple biasing** (single bias current input)

For detailed electrical characteristics, run circuit simulations with the extracted netlists.

## Authors

Time Transcenders Team - SSCS PICO 2025
