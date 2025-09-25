v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 60 -290 100 -290 {
lab=Vin}
N 160 -290 190 -290 {
lab=Vout}
N 190 -290 190 -250 {
lab=Vout}
N 190 -190 190 -150 {
lab=GND}
N 190 -290 250 -290 {
lab=Vout}
C {symbols/cap_mim_2f0fF.sym} 130 -290 1 1 {name=C1
W=10e-6
L=10e-6
model=cap_mim_2f0fF
spiceprefix=X
m=5}
C {symbols/ppolyf_u_1k.sym} 190 -220 0 0 {name=R1
W=1e-6
L=100e-6
model=ppolyf_u_1k
spiceprefix=X
m=1}
C {gnd.sym} 190 -150 0 0 {name=l1 lab=GND}
C {iopin.sym} 60 -290 0 1 {name=p1 lab=Vin}
C {iopin.sym} 250 -290 0 0 {name=p2 lab=Vout}
