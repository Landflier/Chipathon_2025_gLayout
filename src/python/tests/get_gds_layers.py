from glayout import gf180

# Try to access the PDK's internal layer mapping
try:
    # This might work depending on the PDK implementation
    if hasattr(gf180, 'layers'):
        for name, gds_info in gf180.layers.items():
            print(f"{name}: {gds_info}")
    elif hasattr(gf180, '_layers'):
        for name, gds_info in gf180._layers.items():
            print(f"{name}: {gds_info}")
    else:
        print("Layer mapping not directly accessible")
except Exception as e:
    print(f"Could not access layer mapping: {e}")
