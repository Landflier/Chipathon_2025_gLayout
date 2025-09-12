* Current Mirror with Decap - GF180 PDK
.subckt current_mirror VDD VSS IREF IOUT
* Reference transistor (diode-connected)
M1 IREF IREF VSS VSS nfet_03v3 W=2u L=0.28u M=4
* Mirror transistor
M2 IOUT IREF VSS VSS nfet_03v3 W=4u L=0.28u M=4
* Decoupling capacitor
C1 VDD VSS 1p
.ends
