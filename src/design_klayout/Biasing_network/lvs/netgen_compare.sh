#!/bin/bash

# Create a custom netgen setup file to handle pin mapping
cat > custom_netgen_setup.tcl << 'EOF'
# Load the base PDK setup
source /usr/local/share/pdk/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl
EOF

# Run netgen with the custom setup
netgen -batch lvs "netlists/Biasing_network_layout Biasing_network_layout" "netlists/Biasing_network_with_local_mirros_xschem.spice Biasing_network_schematic" custom_netgen_setup.tcl comp.out

