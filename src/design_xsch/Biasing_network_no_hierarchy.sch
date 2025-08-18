v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {Desription

The biasing circuit for the Gilbert cell,
providing constant 50uA current at both its
outputs} 2880 -2390 0 0 0.4 0.4 {}
N 860 -1550 860 -1420 {
lab=I_BIAS}
N 900 -1390 1020 -1390 {
lab=I_BIAS}
N 860 -1570 860 -1550 {
lab=I_BIAS}
N 860 -1360 860 -1320 {
lab=VSS}
N 1060 -1360 1060 -1320 {
lab=VSS}
N 1270 -1360 1270 -1320 {
lab=VSS}
N 1470 -1360 1470 -1320 {
lab=VSS}
N 860 -1320 1470 -1320 {
lab=VSS}
N 1060 -1390 1100 -1390 {
lab=VSS}
N 1100 -1390 1100 -1320 {
lab=VSS}
N 1270 -1390 1310 -1390 {
lab=VSS}
N 1310 -1390 1310 -1320 {
lab=VSS}
N 1470 -1320 1500 -1320 {
lab=VSS}
N 1470 -1390 1500 -1390 {
lab=VSS}
N 1500 -1390 1500 -1320 {
lab=VSS}
N 830 -1320 860 -1320 {
lab=VSS}
N 830 -1390 860 -1390 {
lab=VSS}
N 830 -1390 830 -1320 {
lab=VSS}
N 1060 -1550 1060 -1420 {
lab=I_out_1}
N 1270 -1550 1270 -1420 {
lab=I_out_2}
N 1470 -1550 1470 -1420 {
lab=I_out_3}
N 930 -1460 930 -1390 {
lab=I_BIAS}
N 860 -1460 930 -1460 {
lab=I_BIAS}
N 1200 -1390 1230 -1390 {
lab=I_BIAS}
N 1400 -1390 1430 -1390 {
lab=I_BIAS}
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
C {code.sym} 2705 -2395 0 0 {name=SPICE only_toplevel=true 
value="
* let sets vectors to a plot, while set sets a variable, globally accessible in .control
.control

    * Set frequency and amplitude variables to proper values from within the control sequence
    save all

    op
    show

    write Biasing_network_sim.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 1p 10n


    write Biasing_network_sim.raw

.endc
"}
C {symbols/nfet_03v3.sym} 880 -1390 0 1 {name=M1
L=0.28u
W=7u
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
C {symbols/nfet_03v3.sym} 1040 -1390 0 0 {name=M2
L=0.28u
W=3.5u
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
C {symbols/nfet_03v3.sym} 1250 -1390 0 0 {name=M3
L=0.28u
W=7u
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
C {symbols/nfet_03v3.sym} 1450 -1390 0 0 {name=M4
L=0.28u
W=14u
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
C {iopin.sym} 860 -1570 3 0 {name=p1 lab=I_BIAS}
C {opin.sym} 1060 -1550 3 0 {name=p2 lab=I_out_1}
C {opin.sym} 1270 -1550 3 0 {name=p3 lab=I_out_2}
C {opin.sym} 1470 -1550 3 0 {name=p4 lab=I_out_3}
C {lab_pin.sym} 1200 -1390 1 0 {name=p6 sig_type=std_logic lab=I_BIAS}
C {lab_pin.sym} 1400 -1390 1 0 {name=p7 sig_type=std_logic lab=I_BIAS}
C {ipin.sym} 830 -1320 0 0 {name=p8 lab=VSS}
