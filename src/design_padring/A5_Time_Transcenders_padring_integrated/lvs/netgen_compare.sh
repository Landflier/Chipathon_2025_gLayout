#!/bin/bash

# Create a custom netgen setup file to handle pin mapping
cat > custom_netgen_setup.tcl << 'EOF'
# Load the base PDK setup
source /usr/local/share/pdk/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl
equiv cell io_secondary_5p0 io_secondary_5p0
EOF

# Run netgen with the custom setup
netgen -batch lvs "netlists/Gilbert_mixer_layout.spice Gilbert_mixer_layout" "../schematic/simulation/Gilbert_mixer_schematic.spice Gilbert_mixer_schematic" custom_netgen_setup.tcl comp.out 


