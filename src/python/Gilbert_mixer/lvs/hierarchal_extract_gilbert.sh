#!/bin/bash

magic -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc -dnull -noconsole << 'EOF'
gds readonly false
gds rescale true
gds read Gilbert_cell.gds

# Check what cells are available and load the flattened one
cellname list allcells
load {Gilbert_cell$1}

# Rename the cell to something cleaner for extraction
cellname rename {Gilbert_cell$1} Gilbert_mixer

# Extract with more detailed options
extract all
ext2spice lvs
ext2spice cthresh 0.01
ext2spice rthresh 1000
ext2spice format ngspice
ext2spice subcircuits on
ext2spice hierarchy on
ext2spice scale off
ext2spice blackbox off
ext2spice merge conservative
ext2spice
quit
EOF
