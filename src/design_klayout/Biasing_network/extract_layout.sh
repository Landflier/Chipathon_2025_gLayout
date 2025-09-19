#!/bin/bash

# ext2spice cthresh 0.01

# NMOS cmirror
magic -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc -dnull -noconsole << 'EOF'
gds readonly false
gds rescale true
gds read Biasing_network.gds

# Check what cells are available and load the flattened one
cellname list allcells
load Biasing_Network
cellname rename Biasing_Network Biasing_network_layout

# Extract with more detailed options
# extract unique # disable port merging. Just for cmirror topology with decap (VSS/VDD and I_BIAS should remain separate)
extract all
ext2spice lvs
ext2spice cthresh inf
ext2spice rthresh inf
ext2spice format ngspice
ext2spice subcircuit top auto
ext2spice hierarchy on
ext2spice scale off
ext2spice blackbox on
# ext2spice merge conservative
ext2spice subcircuits descend off
ext2spice merge none
ext2spice global off
ext2spice -o lvs/netlists/Biasing_network_layout.spice
quit
EOF
# cleanup
rm *.ext
