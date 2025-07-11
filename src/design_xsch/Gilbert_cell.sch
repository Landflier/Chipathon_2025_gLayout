v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 120 -30 300 -30 {
lab=#net1}
N 200 -30 200 40 {
lab=#net1}
N 420 -30 590 -30 {
lab=#net2}
N 520 -30 520 30 {
lab=#net2}
N 520 30 520 40 {
lab=#net2}
N 420 -130 420 -90 {
lab=#net3}
N 120 -130 120 -90 {
lab=#net3}
N 120 -190 120 -130 {
lab=#net3}
N 590 -180 590 -90 {
lab=#net4}
N 300 -130 300 -90 {
lab=#net4}
N 300 -130 380 -160 {
lab=#net4}
N 120 -160 340 -160 {
lab=#net3}
N 340 -160 420 -130 {
lab=#net3}
N 380 -160 590 -160 {
lab=#net4}
N 340 -60 380 -60 {
lab=V_LO_b}
N 590 -190 590 -180 {
lab=#net4}
N 200 100 520 100 {
lab=#net5}
N 360 100 360 160 {
lab=#net5}
N 40 -60 80 -60 {
lab=V_LO}
N 360 -60 360 10 {
lab=V_LO_b}
N 40 10 360 10 {
lab=V_LO_b}
N 40 70 160 70 {
lab=V_RF}
N 560 70 560 140 {
lab=xxx}
N 40 140 560 140 {
lab=xxx}
N 630 -60 670 -60 {
lab=V_LO}
N 670 -60 700 -60 {
lab=V_LO}
C {symbols/nfet_03v3.sym} 180 70 0 0 {name=M1
L=0.28u
W=0.22u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
hide_annotation=true}
C {symbols/nfet_03v3.sym} 540 70 0 1 {name=M2
L=0.28u
W=0.22u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {symbols/nfet_03v3.sym} 100 -60 0 0 {name=M3
L=0.28u
W=0.22u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {symbols/nfet_03v3.sym} 320 -60 0 1 {name=M4
L=0.28u
W=0.22u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {symbols/nfet_03v3.sym} 400 -60 0 0 {name=M5
L=0.28u
W=0.22u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {symbols/nfet_03v3.sym} 610 -60 0 1 {name=M6
L=0.28u
W=0.22u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {ipin.sym} 40 -60 0 0 {name=p1 lab=V_LO}
C {ipin.sym} 40 10 0 0 {name=p2 lab=V_LO_b
}
C {ipin.sym} 40 70 0 0 {name=p3 lab=V_RF}
C {ipin.sym} 40 140 2 1 {name=p4 lab=V_RF_b
}
C {ipin.sym} 700 -60 0 0 {name=p6 lab=V_LO}
