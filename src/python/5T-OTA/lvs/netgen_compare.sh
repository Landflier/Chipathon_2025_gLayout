#!/bin/bash

# Netgen LVS comparison script for 5T-OTA
# Compares extracted layout netlist with reference schematic netlist

echo "Starting LVS comparison for 5T-OTA..."

# Check if required files exist
if [ ! -f "netlists/5T_OTA_extracted_layout.spice" ]; then
    echo "Error: Layout netlist not found. Run extract_5t_ota_layout.sh first."
    exit 1
fi

if [ ! -f "netlists/5T_OTA_xschem.spice" ]; then
    echo "Error: Schematic netlist not found."
    echo "Please provide 5T_OTA_xschem.spice in the netlists/ directory."
    exit 1
fi

# Run netgen LVS comparison
netgen -batch lvs "netlists/5T_OTA_extracted_layout.spice 5T_OTA_layout" \
                  "netlists/5T_OTA_xschem.spice 5T_OTA" \
                  custom_netgen_setup.tcl comp.out

# Check the result
if grep -q "Circuits match uniquely" comp.out; then
    echo "✅ LVS PASSED: Circuits match uniquely!"
    exit 0
else
    echo "❌ LVS FAILED: Circuits do not match."
    echo "Check comp.out for detailed comparison results."
    exit 1
fi
