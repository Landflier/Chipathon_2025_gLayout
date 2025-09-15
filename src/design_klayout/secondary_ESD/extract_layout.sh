#!/bin/bash

# ext2spice cthresh 0.01

magic -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc -dnull -noconsole << 'EOF'
gds readonly false
gds rescale true
gds read secondary_ESD.gds

# Check what cells are available and load the flattened one
cellname list allcells
load io_secondary_5p0
cellname rename io_secondary_5p0 io_secondary_5p0_layout

# Extract with more detailed options
extract all
ext2spice lvs
ext2spice cthresh inf
ext2spice rthresh inf
ext2spice format ngspice
ext2spice subcircuit top auto
ext2spice hierarchy on
ext2spice scale off
ext2spice blackbox on
ext2spice merge conservative
ext2spice global off
ext2spice -o lvs/secondary_ESD_layout.spice
quit
EOF
rm *.ext
