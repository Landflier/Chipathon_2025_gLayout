#!/bin/bash

# Create a custom netgen setup file to handle pin mapping
cat > custom_netgen_setup.tcl << 'EOF'
# Load the base PDK setup
source /usr/local/share/pdk/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl
EOF

# Run netgen with the custom setup
netgen -batch lvs "netlists/Gilbert_mixer_loading_stage.spice Gilbert_mixer_loading_stage " "netlists/Gilbert_cell_hierarchal_loading_stage.spice Gilbert_cell_hierarchal_loading_stage" custom_netgen_setup.tcl comp.out


