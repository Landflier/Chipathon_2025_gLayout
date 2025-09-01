#!/bin/bash

# Create a custom netgen setup file to handle pin mapping
cat > custom_netgen_setup.tcl << 'EOF'
# Load the base PDK setup
source /usr/local/share/pdk/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl
EOF

# Run netgen with the custom setup
netgen -batch lvs "spice/Gilbert_mixer_extracted_layout.spice Gilbert_cell_layout" "spice/Gilbert_mixer_extracted_xschem.spice Gilbert_cell_xschem" custom_netgen_setup.tcl comp.out


