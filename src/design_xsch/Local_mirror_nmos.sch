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
N 600 -980 780 -980 {
lab=VSS}
N 840 -1010 840 -980 {
lab=VSS}
N 840 -1040 860 -1040 {
lab=VSS}
N 860 -1040 860 -980 {
lab=VSS}
N 780 -1040 800 -1040 {
lab=I_BIAS}
N 840 -1190 840 -1070 {
lab=I_out}
N 720 -1010 720 -980 {
lab=VSS}
N 720 -1040 750 -1040 {
lab=VSS}
N 750 -1040 750 -980 {
lab=VSS}
N 650 -1040 680 -1040 {
lab=I_BIAS}
N 650 -1110 650 -1040 {
lab=I_BIAS}
N 650 -1110 720 -1110 {
lab=I_BIAS}
N 720 -1110 720 -1070 {
lab=I_BIAS}
N 720 -1110 780 -1110 {
lab=I_BIAS}
N 780 -1110 780 -1040 {
lab=I_BIAS}
N 780 -980 860 -980 {
lab=VSS}
N 600 -1110 650 -1110 {
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
C {symbols/nfet_03v3.sym} 820 -1040 0 0 {name=M2
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
C {iopin.sym} 600 -980 0 1 {name=p1 lab=VSS}
C {opin.sym} 840 -1190 3 0 {name=p7 lab=I_out}
C {symbols/nfet_03v3.sym} 700 -1040 0 0 {name=M6
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
C {iopin.sym} 600 -1110 0 1 {name=p2 lab=I_BIAS}
C {symbols/cap_nmos_03v3.sym} 650 -1010 0 1 {name=C1
W=1e-6
L=1e-6
model=cap_nmos_03v3
spiceprefix=X
m=1}
