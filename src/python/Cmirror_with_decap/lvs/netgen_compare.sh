#!/bin/bash

# Create a custom netgen setup file to handle pin mapping
cat > custom_netgen_setup.tcl << 'EOF'
# Load the base PDK setup
source /usr/local/share/pdk/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl
EOF

# Run netgen with the custom setup
# NMOS_cmirror
netgen -batch lvs "netlists/nmos_Cmirror_with_decap_layout.spice nmos_Cmirror_with_decap_layout" "netlists/nmos_Cmirror_with_decap_xschem.spice nmos_Cmirror_with_decap_xschem" custom_netgen_setup.tcl nmos_cmirror_comp.out


netgen -batch lvs "netlists/pmos_Cmirror_with_decap_layout.spice pmos_Cmirror_with_decap_layout" "netlists/pmos_Cmirror_with_decap_xschem.spice pmos_Cmirror_with_decap_xschem" custom_netgen_setup.tcl pmos_cmirror_comp.out
