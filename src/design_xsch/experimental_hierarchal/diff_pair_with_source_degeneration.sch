v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 160 -240 160 -180 {
lab=I_out_p}
N 370 -240 370 -180 {
lab=I_out_n}
N 80 -150 120 -150 {
lab=V_in_p}
N 410 -150 470 -150 {
lab=V_in_n}
N 160 -120 160 -70 {
lab=I_bias1}
N 370 -120 370 -70 {
lab=I_bias2}
N 260 -180 260 -150 {
lab=GND}
N 160 -150 370 -150 {
lab=GND}
N 160 -90 230 -90 {
lab=I_bias1}
N 290 -90 370 -90 {
lab=I_bias2}
C {symbols/nfet_03v3.sym} 140 -150 0 0 {name=M1
L=L_pos
W=W_pos
nf=1
m=mult
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {symbols/nfet_03v3.sym} 390 -150 0 1 {name=M2
L=L_neg
W=W_neg
nf=1
m=mult
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {ipin.sym} 80 -150 0 0 {name=V_in_p dir=in lab=V_in_p}
C {ipin.sym} 470 -150 0 1 {name=V_in_n 
lab=V_in_n
}
C {iopin.sym} 160 -240 3 0 {name=I_out_p 
lab=I_out_p
dir=inout}
C {iopin.sym} 370 -240 3 0 {name=I_out_n 
lab=I_out_n
dir=inout
}
C {iopin.sym} 160 -70 3 1 {name=I_bias2
lab=I_bias1
dir=inout
}
C {res.sym} 260 -90 3 0 {name=R1
value=RS
footprint=1206
device=resistor
m=1}
C {iopin.sym} 370 -70 3 1 {name=I_bias1
lab=I_bias2
dir=inout
}
C {iopin.sym} 260 -180 3 0 {name=GND 
lab=GND
dir=inout}
