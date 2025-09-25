#!/usr/bin/env python3
"""Simple MIM capacitor generator using glayout."""

from glayout import gf180, mimcap

def create_mim_capacitor(size=(5.0, 5.0)):
    """Create a simple MIM capacitor.
    
    Args:
        size: Tuple of (width, height) in micrometers
    
    Returns:
        Component: MIM capacitor
    """
    # Create MIM capacitor
    cap = mimcap(pdk=gf180, size=size)
    cap.name = "MIM_CAPACITOR"
    return cap

def main():
    """Test MIM capacitor generation."""
    print("Creating MIM capacitor...")
    
    # Create capacitor
    cap = create_mim_capacitor(size=(5.0, 5.0))
    
    # Write GDS file
    cap.write_gds('mim_capacitor.gds')
    print(f"✓ Generated: mim_capacitor.gds")
    
    # Show layout if possible
    try:
        cap.show()
    except:
        print("Could not display layout")

if __name__ == "__main__":
    main()
