v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
L 16 700 -1070 730 -1070 {}
L 16 730 -1150 730 -1070 {}
L 16 730 -1150 760 -1150 {}
L 16 760 -1150 760 -1070 {}
L 16 760 -1070 790 -1070 {}
L 16 760 -1070 790 -1070 {}
L 16 790 -1150 790 -1070 {}
L 16 790 -1150 820 -1150 {}
L 16 820 -1150 820 -1070 {}
L 16 820 -1070 850 -1070 {}
L 16 820 -1070 850 -1070 {}
L 16 850 -1150 850 -1070 {}
L 16 850 -1150 880 -1150 {}
L 16 880 -1150 880 -1070 {}
L 16 880 -1070 910 -1070 {}
L 16 1800 -1080 1830 -1080 {}
L 16 1830 -1110 1860 -1110 {}
L 16 1860 -1080 1890 -1080 {}
L 16 1860 -1080 1890 -1080 {}
L 16 1830 -1110 1830 -1080 {}
L 16 1860 -1110 1860 -1080 {}
L 16 1860 -1080 1890 -1080 {}
L 16 1890 -1110 1920 -1110 {}
L 16 1920 -1080 1950 -1080 {}
L 16 1920 -1080 1950 -1080 {}
L 16 1890 -1110 1890 -1080 {}
L 16 1920 -1110 1920 -1080 {}
L 16 1920 -1080 1950 -1080 {}
L 16 1950 -1110 1980 -1110 {}
L 16 1980 -1080 2010 -1080 {}
L 16 1980 -1080 2010 -1080 {}
L 16 1950 -1110 1950 -1080 {}
L 16 1980 -1110 1980 -1080 {}
L 19 1210 -1150 1360 -1150 {}
L 19 1210 -1080 1360 -1080 {}
A 19 1255 -1115 57.0087712549569 142.1250163489018 75.74996730219635 {}
A 19 1165 -1115 57.0087712549569 322.1250163489018 75.74996730219635 {}
A 19 1405 -1115 57.0087712549569 142.1250163489018 75.74996730219635 {}
A 19 1315 -1115 57.0087712549569 322.1250163489018 75.74996730219635 {}
P 6 6 1450 -1190 1450 -980 1640 -980 1640 -1050 1640 -1190 1450 -1190 {}
T {Desription

A simple 5T-OTA, to serve as a buffer 
for the IF signal to the output measurement
equipment.} 2880 -2390 0 0 0.4 0.4 {}
T {Scope} 1510 -1220 0 0 0.4 0.4 { layer=6}
T {Probe Cable} 1220 -1190 0 0 0.4 0.4 { layer=19}
N 1010 -1120 1060 -1120 {
lab=Signal_IN}
N 1040 -1180 1040 -1120 {
lab=Signal_IN}
N 1040 -1180 1060 -1180 {
lab=Signal_IN}
N 1120 -1120 1140 -1120 {
lab=Signal_OUT}
N 1120 -1180 1140 -1180 {
lab=Signal_OUT}
N 1140 -1180 1140 -1120 {
lab=Signal_OUT}
N 1140 -1120 1250 -1120 {
lab=Signal_OUT}
N 1250 -1120 1450 -1120 {
lab=Signal_OUT}
N 1450 -1120 1510 -1120 {
lab=Signal_OUT}
N 1540 -1000 1630 -1000 {
lab=GND}
N 1460 -1000 1540 -1000 {
lab=GND}
N 1510 -1030 1510 -1000 {
lab=GND}
N 1590 -1030 1590 -1000 {
lab=GND}
N 1510 -1120 1510 -1090 {
lab=Signal_OUT}
N 1590 -1120 1590 -1090 {
lab=Signal_OUT}
N 1510 -1120 1590 -1120 {
lab=Signal_OUT}
N 1590 -1120 1690 -1120 {
lab=Signal_OUT}
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
C {ipin.sym} 1010 -1120 0 0 {name=p1 lab=Signal_IN}
C {res.sym} 1090 -1120 3 0 {name=R1
value=9Meg
footprint=1206
device=resistor
m=1}
C {capa.sym} 1090 -1180 3 0 {name=C1
m=1
value=10p
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 1550 -1000 0 0 {name=l1 lab=GND}
C {res.sym} 1510 -1060 0 0 {name=R2
value=1Meg
footprint=1206
device=resistor
m=1}
C {capa.sym} 1590 -1060 0 0 {name=C2
m=1
value=20p
footprint=1206
device="ceramic capacitor"}
C {opin.sym} 1690 -1120 0 0 {name=p2 lab=Signal_OUT}
