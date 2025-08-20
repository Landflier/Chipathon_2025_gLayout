v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {Desription

A simple 5T-OTA, to serve as a buffer 
for the IF signal to the output measurement
equipment.} 2880 -2390 0 0 0.4 0.4 {}
N 940 -810 940 -750 {
lab=VSS}
N 940 -750 980 -750 {
lab=VSS}
N 980 -780 980 -750 {
lab=VSS}
N 940 -870 940 -810 {
lab=VSS}
N 940 -870 980 -870 {
lab=VSS}
N 980 -870 980 -840 {
lab=VSS}
N 980 -810 1020 -810 {
lab=VSS}
N 1020 -810 1020 -750 {
lab=VSS}
N 980 -750 1020 -750 {
lab=VSS}
N 1090 -810 1090 -750 {
lab=VSS}
N 1090 -750 1130 -750 {
lab=VSS}
N 1130 -780 1130 -750 {
lab=VSS}
N 1090 -870 1090 -810 {
lab=VSS}
N 1090 -870 1130 -870 {
lab=VSS}
N 1130 -870 1130 -840 {
lab=VSS}
N 1130 -810 1170 -810 {
lab=VSS}
N 1170 -810 1170 -750 {
lab=VSS}
N 1130 -750 1170 -750 {
lab=VSS}
N 1230 -810 1230 -750 {
lab=VSS}
N 1230 -750 1270 -750 {
lab=VSS}
N 1270 -780 1270 -750 {
lab=VSS}
N 1230 -870 1230 -810 {
lab=VSS}
N 1230 -870 1270 -870 {
lab=VSS}
N 1270 -870 1270 -840 {
lab=VSS}
N 1270 -810 1310 -810 {
lab=VSS}
N 1310 -810 1310 -750 {
lab=VSS}
N 1270 -750 1310 -750 {
lab=VSS}
N 1360 -810 1360 -750 {
lab=VSS}
N 1360 -750 1400 -750 {
lab=VSS}
N 1400 -780 1400 -750 {
lab=VSS}
N 1360 -870 1360 -810 {
lab=VSS}
N 1360 -870 1400 -870 {
lab=VSS}
N 1400 -870 1400 -840 {
lab=VSS}
N 1400 -810 1440 -810 {
lab=VSS}
N 1440 -810 1440 -750 {
lab=VSS}
N 1400 -750 1440 -750 {
lab=VSS}
N 1500 -810 1500 -750 {
lab=VSS}
N 1500 -750 1540 -750 {
lab=VSS}
N 1540 -780 1540 -750 {
lab=VSS}
N 1500 -870 1500 -810 {
lab=VSS}
N 1500 -870 1540 -870 {
lab=VSS}
N 1540 -870 1540 -840 {
lab=VSS}
N 1540 -810 1580 -810 {
lab=VSS}
N 1580 -810 1580 -750 {
lab=VSS}
N 1540 -750 1580 -750 {
lab=VSS}
N 1020 -750 1090 -750 {
lab=VSS}
N 1170 -750 1230 -750 {
lab=VSS}
N 1310 -750 1360 -750 {
lab=VSS}
N 1440 -750 1500 -750 {
lab=VSS}
N 870 -750 940 -750 {
lab=VSS}
N 1660 -810 1660 -750 {
lab=VSS}
N 1660 -750 1700 -750 {
lab=VSS}
N 1700 -780 1700 -750 {
lab=VSS}
N 1660 -870 1660 -810 {
lab=VSS}
N 1660 -870 1700 -870 {
lab=VSS}
N 1700 -870 1700 -840 {
lab=VSS}
N 1700 -810 1740 -810 {
lab=VSS}
N 1740 -810 1740 -750 {
lab=VSS}
N 1700 -750 1740 -750 {
lab=VSS}
N 1810 -810 1810 -750 {
lab=VSS}
N 1810 -750 1850 -750 {
lab=VSS}
N 1850 -780 1850 -750 {
lab=VSS}
N 1810 -870 1810 -810 {
lab=VSS}
N 1810 -870 1850 -870 {
lab=VSS}
N 1850 -870 1850 -840 {
lab=VSS}
N 1850 -810 1890 -810 {
lab=VSS}
N 1890 -810 1890 -750 {
lab=VSS}
N 1850 -750 1890 -750 {
lab=VSS}
N 1580 -750 1660 -750 {
lab=VSS}
N 1740 -750 1810 -750 {
lab=VSS}
C {title-2.sym} 0 0 0 0 {name=l9 author="Time Transcenders" lock=true rev=1.0 page=1}
C {code.sym} 50 -190 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/sm141064.ngspice mimcap_typical
.lib $::180MCU_MODELS/sm141064.ngspice cap_mim
.lib $::180MCU_MODELS/sm141064.ngspice res_typical

"
}
C {symbols/nfet_03v3.sym} 960 -810 0 0 {name=M_dummy_1
L=0.28u
W=10u
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
C {symbols/nfet_03v3.sym} 1110 -810 0 0 {name=M_dummy_2
L=0.28u
W=10u
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
C {symbols/nfet_03v3.sym} 1250 -810 0 0 {name=M_dummy_3
L=0.28u
W=10u
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
C {symbols/nfet_03v3.sym} 1380 -810 0 0 {name=M_dummy_4
L=0.28u
W=10u
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
C {symbols/nfet_03v3.sym} 1520 -810 0 0 {name=M_dummy_5
L=0.28u
W=10u
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
C {ipin.sym} 870 -750 0 0 {name=p1 lab=VSS}
C {symbols/nfet_03v3.sym} 1680 -810 0 0 {name=M_dummy_6
L=0.28u
W=10u
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
C {symbols/nfet_03v3.sym} 1830 -810 0 0 {name=M_dummy_7
L=0.28u
W=10u
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
