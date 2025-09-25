#!/bin/bash

# ext2spice cthresh 0.01

# LVS
magic -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc -dnull -noconsole << 'EOF'
gds readonly false
gds rescale true
gds read ../A5_Gilbert_mixer_only_routing.gds

# Check what cells are available and load the flattened one
cellname list allcells
load Gilbert_mixer_toplevel
cellname rename Gilbert_mixer_toplevel Gilbert_mixer_schematic 
# readspice /home/vasil/Downloads/SSCS_PICO_2025/src/design_padring/A5_Time_Transcenders_padring_integrated/schematic/simulation/Gilbert_mixer_schematic.spice

cellname rename Gilbert_mixer_schematic Gilbert_mixer_layout

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
ext2spice -o netlists/Gilbert_mixer_layout.spice
quit
EOF
rm *.ext
