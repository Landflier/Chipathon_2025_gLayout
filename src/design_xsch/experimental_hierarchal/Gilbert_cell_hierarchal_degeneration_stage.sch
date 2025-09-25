v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 900 -1110 900 -1060 {
lab=iout_1}
N 900 -1230 900 -1170 {
lab=iout_1}
N 1000 -1230 1000 -1150 {
lab=VDD}
N 900 -1170 900 -1110 {
lab=iout_1}
N 1100 -1230 1100 -1060 {
lab=in_2}
N 900 -1130 970 -1130 {
lab=iout_1}
N 1030 -1130 1100 -1130 {
lab=in_2}
C {iopin.sym} 1100 -1230 3 0 {name=p2 lab=iout_2}
C {iopin.sym} 900 -1230 3 0 {name=p1 lab=iout_1
}
C {symbols/pplus_u.sym} 1000 -1130 3 1 {name=R_load_3
W=0.5e-6
L=5e-6
model=pplus_u
spiceprefix=X
m=1}
C {iopin.sym} 1000 -1230 2 0 {name=p5 lab=VDD
}
C {iopin.sym} 900 -1060 1 0 {name=p3 lab=iout_1
}
C {iopin.sym} 1100 -1060 1 0 {name=p4 lab=iout_2}
