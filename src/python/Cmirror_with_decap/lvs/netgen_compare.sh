#!/bin/bash

# Create a custom netgen setup file to handle pin mapping
cat > custom_netgen_setup.tcl << 'EOF'
# Load the base PDK setup
source /usr/local/share/pdk/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl
EOF

# Run netgen with the custom setup
netgen -batch lvs "netlists/nmos_Cmirror_with_decap_layout.spice nmos_Cmirror_with_decap_layout" "netlists/nmos_Cmirror_with_decap_xschem.spice nmos_Cmirror_with_decap_xschem" custom_netgen_setup.tcl comp.out


