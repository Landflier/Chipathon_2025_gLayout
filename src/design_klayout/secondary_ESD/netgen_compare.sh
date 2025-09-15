#!/bin/bash

# Create a custom netgen setup file to handle pin mapping
cat > custom_netgen_setup.tcl << 'EOF'
# Load the base PDK setup
source /usr/local/share/pdk/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl
EOF

# Run netgen with the custom setup
netgen -batch lvs "lvs/secondary_ESD_layout.spice io_secondary_5p0_layout" "lvs/secondary_ESD_xschem.spice io_secondary_5p0_schematic" custom_netgen_setup.tcl comp.out


