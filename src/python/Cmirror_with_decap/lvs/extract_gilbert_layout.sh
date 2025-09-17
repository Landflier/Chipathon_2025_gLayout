#!/bin/bash

# ext2spice cthresh 0.01

magic -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc -dnull -noconsole << 'EOF'
gds readonly false
gds rescale true
gds read gds/Gilbert_cell_interdigitized.gds

# Check what cells are available and load the flattened one
cellname list allcells
load Gilbert_mixer_interdigitized
cellname rename Gilbert_mixer_interdigitized Gilbert_cell_layout

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
ext2spice -o spice/Gilbert_mixer_extracted_layout.spice
quit
EOF
rm *.ext
