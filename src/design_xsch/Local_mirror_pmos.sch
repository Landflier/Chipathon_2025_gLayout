v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {Desription

PMOS mirror used in the input of the 
I_bias. This component is used in
Biasing_network_with_local_mirrors } 2880 -2390 0 0 0.4 0.4 {}
N 370 -1200 370 -1100 {
lab=I_BIAS}
N 370 -1340 370 -1260 {
lab=VDD}
N 550 -1330 550 -1260 {
lab=VDD}
N 170 -1340 550 -1340 {
lab=VDD}
N 550 -1340 550 -1330 {
lab=VDD}
N 370 -1230 400 -1230 {
lab=VDD}
N 400 -1340 400 -1230 {
lab=VDD}
N 240 -1230 270 -1230 {
lab=I_BIAS}
N 240 -1260 240 -1230 {
lab=I_BIAS}
N 270 -1230 330 -1230 {
lab=I_BIAS}
N 240 -1340 240 -1320 {
lab=VDD}
N 480 -1230 510 -1230 {
lab=I_BIAS}
N 550 -1200 550 -1100 {
lab=I_out}
N 300 -1170 370 -1170 {
lab=I_BIAS}
N 300 -1230 300 -1170 {
lab=I_BIAS}
N 550 -1230 580 -1230 {
lab=VDD}
N 580 -1340 580 -1230 {
lab=VDD}
N 550 -1340 580 -1340 {
lab=VDD}
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
C {iopin.sym} 370 -1100 3 1 {name=p2 lab=I_BIAS}
C {symbols/pfet_03v3.sym} 350 -1230 0 0 {name=M1
L=1u
W=0.22u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_03v3
spiceprefix=X
}
C {iopin.sym} 170 -1340 0 1 {name=p3 lab=VDD}
C {symbols/pfet_03v3.sym} 530 -1230 0 0 {name=M5
L=1u
W=0.22u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_03v3
spiceprefix=X
}
C {lab_pin.sym} 480 -1230 3 0 {name=p11 sig_type=std_logic lab=I_BIAS}
C {iopin.sym} 550 -1100 3 1 {name=p1 lab=I_out}
C {symbols/cap_pmos_03v3.sym} 240 -1290 0 0 {name=C1
W=1e-6
L=1e-6
model=cap_pmos_03v3
spiceprefix=X
m=1}
