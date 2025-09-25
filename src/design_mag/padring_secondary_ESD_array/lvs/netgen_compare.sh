#!/bin/bash

# Create a custom netgen setup file to handle pin mapping
cat > custom_netgen_setup.tcl << 'EOF'
# Load the base PDK setup
source /usr/local/share/pdk/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl
EOF

# Run netgen with the custom setup
netgen -batch lvs "netlists/ESD_array_layout.spice ESD_array_layout" "netlists/ESD_array_schematic.spice ESD_array_schematic" custom_netgen_setup.tcl comp.out


