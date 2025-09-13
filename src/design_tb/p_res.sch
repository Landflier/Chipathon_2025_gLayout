v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N -0 -60 0 -30 {lab=#net1}
N 0 -30 40 -30 {lab=#net1}
N 40 -30 40 10 {
lab=#net1}
N 40 70 40 100 {lab=GND}
N -170 0 -170 20 {
lab=GND}
N -170 -70 -170 -60 {
lab=VDD}
N 40 -110 40 -90 {lab=VDD}
N 40 -60 110 -60 {lab=VDD}
C {symbols/pfet_03v3.sym} 20 -60 0 0 {name=M1
L=0.28u
W=0.47u
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
C {isource.sym} 40 40 0 0 {name=I0 value=50u}
C {gnd.sym} 40 100 0 0 {name=l6 lab=GND}
C {vdd.sym} -170 -70 0 0 {name=l8 lab=VDD}
C {vsource.sym} -170 -30 0 0 {name=V_PWR value=3.3 savecurrent=true}
C {gnd.sym} -170 20 0 0 {name=l7 lab=GND}
C {vdd.sym} 40 -110 0 0 {name=l10 lab=VDD}
C {code.sym} -130 60 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/sm141064.ngspice mimcap_typical
.lib $::180MCU_MODELS/sm141064.ngspice cap_mim
.lib $::180MCU_MODELS/sm141064.ngspice res_typical

"
}
C {code.sym} 150 -30 0 0 {name=spice only_toplevel=false value=
"
*.op
*.save all

.control
save all
op
print @m.xm1.m0[gm]
set appendwrite
write pres_tb.raw
.endc
"
}
C {lab_pin.sym} 110 -60 1 0 {name=p1 sig_type=std_logic lab=VDD}
