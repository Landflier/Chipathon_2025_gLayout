#!/bin/bash

# Extract 5T-OTA layout for LVS verification
# This script extracts the GDS layout and generates SPICE netlist for comparison

echo "Starting 5T-OTA layout extraction..."

# LVS Extraction
magic -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc -dnull -noconsole << 'EOF'
gds readonly false
gds rescale true
gds read gds/5T_OTA.gds

# Check what cells are available and load the main one
cellname list allcells
load 5T_OTA
cellname rename 5T_OTA 5T_OTA_layout

# Extract with detailed options for LVS
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
ext2spice -o netlists/5T_OTA_extracted_layout.spice
quit
EOF

echo "Layout extraction completed."

# PEX Extraction (Parasitic Extraction)
echo "Starting PEX extraction..."

magic -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc -dnull -noconsole << 'EOF'
gds read gds/5T_OTA.gds

# Check what cells are available and load the main one
cellname list allcells
load 5T_OTA
cellname rename 5T_OTA 5T_OTA_layout_PEX

# Extract with parasitic elements
extract all
ext2spice hierarchy on
ext2spice cthresh 1
ext2spice rthresh 10 
ext2spice format ngspice
ext2spice scale off
ext2spice merge conservative
ext2spice -o netlists/5T_OTA_extracted_layout_PEX.spice
quit
EOF

# Clean up temporary files
rm -f *.ext

echo "PEX extraction completed."
echo "Generated files:"
echo "  - netlists/5T_OTA_extracted_layout.spice (for LVS)"
echo "  - netlists/5T_OTA_extracted_layout_PEX.spice (with parasitics)"
