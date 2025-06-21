from glayout import sky130, gf180, nmos ,pmos, via_stack

# Generate a via stack
#met2 is the bottom layer. met3 is the top layer.
via = via_stack(sky130, "met2", "met3", centered=True) 

# Generate a transistor
transistor = nmos(sky130, width=1.0, length=0.15, fingers=2)

# Write to GDS
via.write_gds("via.gds")
transistor.write_gds("transistor.gds")
