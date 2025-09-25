#!/bin/bash

# ext2spice cthresh 0.01

# LVS
magic -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc -dnull -noconsole << 'EOF'
gds readonly false
gds rescale true
gds read gds/Gilbert_cell_interdigited.gds

# Check what cells are available and load the flattened one
cellname list allcells
load Gilbert_mixer_interdigited
cellname rename Gilbert_mixer_interdigited Gilbert_cell_layout

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
ext2spice -o netlists/Gilbert_mixer_extracted_layout.spice
quit
EOF

# PEX


magic -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc -dnull -noconsole << 'EOF'
gds read gds/Gilbert_cell_interdigited.gds

# Check what cells are available and load the flattened one
cellname list allcells
load Gilbert_mixer_interdigited
cellname rename Gilbert_mixer_interdigited Gilbert_cell_hierarchal_mixing_stage
readspice /home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/simulation/Gilbert_cell_hierarchal_mixing_stage.spice

# Extract with more detailed options
extract all
ext2spice hierarchy on
ext2spice cthresh 1
ext2spice rthresh 10 
ext2spice format ngspice
ext2spice scale off
ext2spice merge conservative
ext2spice -o netlists/Gilbert_mixer_extracted_layout_PEX.spice
quit
EOF
rm *.ext
