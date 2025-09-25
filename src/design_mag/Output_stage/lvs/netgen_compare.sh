#!/bin/bash

# Create a custom netgen setup file to handle pin mapping
cat > custom_netgen_setup.tcl << 'EOF'
# Load the base PDK setup
source /usr/local/share/pdk/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl
EOF

# Run netgen with the custom setup
netgen -batch lvs "netlists/Output_stage_layout.spice Output_stage_layout" "netlists/Output_stage_schematic.spice Output_stage-schematic" custom_netgen_setup.tcl comp.out


