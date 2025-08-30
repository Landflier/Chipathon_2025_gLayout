v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 1000 -1010 1800 -610 {flags=graph
y1=-0.095
y2=-0.091
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=2e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
dataset=-1
unitx=1
logx=0
logy=0
rawfile=$netlist_dir/buffer_tb.raw
color=4
node=signal_out}
B 2 1000 -540 1800 -140 {flags=graph
y1=0.49
y2=0.51
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=2e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
dataset=-1
unitx=1
logx=0
logy=0
rawfile=$netlist_dir/buffer_tb.raw
color=4
node=vin_plus}
N -670 -320 -670 -300 {
lab=GND}
N -670 -390 -670 -380 {
lab=VDD}
N -20 -10 -20 30 {lab=VOUT}
N -20 -130 -20 -70 {lab=VDD}
N -20 -140 -20 -130 {lab=VDD}
N -570 -320 -570 -300 {
lab=GND}
N -570 -400 -570 -380 {
lab=Vin_plus}
N -20 10 30 10 {
lab=VOUT}
N -550 -70 -550 -10 {
lab=#net1}
N -330 -70 -330 -10 {
lab=Vota}
N -670 20 -590 20 {
lab=Vin_plus}
N -290 20 -210 20 {
lab=Vin_minus}
N -550 -190 -550 -130 {
lab=VDD}
N -330 -190 -330 -130 {
lab=VDD}
N -550 -190 -330 -190 {
lab=VDD}
N -680 -190 -550 -190 {
lab=VDD}
N -550 50 -550 120 {
lab=I_bias}
N -330 50 -330 120 {
lab=I_bias}
N -550 120 -330 120 {
lab=I_bias}
N -440 120 -440 170 {
lab=I_bias}
N -330 -40 -210 -40 {
lab=Vota}
N -660 80 -210 80 {
lab=Vin_minus}
N -210 20 -210 80 {
lab=Vin_minus}
N -670 80 -660 80 {
lab=Vin_minus}
N -440 170 -440 200 {
lab=I_bias}
N -510 -100 -370 -100 {
lab=#net1}
N -550 -40 -470 -40 {
lab=#net1}
N -470 -100 -470 -40 {
lab=#net1}
N -330 -100 -300 -100 {
lab=VDD}
N -360 20 -330 20 {
lab=GND}
N -550 20 -520 20 {
lab=GND}
N -580 -100 -550 -100 {
lab=VDD}
N -330 -300 -330 -280 {
lab=GND}
N -330 -340 -330 -300 {
lab=GND}
N -20 30 -20 70 {
lab=VOUT}
N -20 130 -20 160 {lab=GND}
N -20 -40 60 -40 {lab=GND}
N -490 -320 -490 -300 {
lab=GND}
N -490 -400 -490 -380 {
lab=Vin_minus}
N -210 -40 -110 -40 {lab=Vota}
N 690 -210 760 -210 {lab=signal_out}
N -110 -40 -60 -40 {lab=Vota}
N 30 10 90 10 {lab=VOUT}
C {vdd.sym} -670 -390 0 0 {name=l8 lab=VDD}
C {vsource.sym} -670 -350 0 0 {name=V_PWR value=3.3 savecurrent=true}
C {gnd.sym} -670 -300 0 0 {name=l7 lab=GND}
C {symbols/nfet_03v3.sym} -40 -40 0 0 {name=nfet_SF
L=0.28u
W=7u
nf=10
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
C {vdd.sym} -20 -140 0 0 {name=l4 lab=VDD}
C {lab_wire.sym} -570 -400 0 0 {name=p10 sig_type=std_logic lab=Vin_plus}
C {vsource.sym} -570 -350 0 0 {name=vrf_plus
value="sin( 0.5 0.01 10e6 0 )"
savecurrent=true
hide_texts=true}
C {gnd.sym} -570 -300 0 0 {name=l5 lab=GND}
C {code.sym} -100 -360 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/sm141064.ngspice mimcap_typical
.lib $::180MCU_MODELS/sm141064.ngspice cap_mim
.lib $::180MCU_MODELS/sm141064.ngspice res_typical

"
}
C {code.sym} -100 -540 0 0 {name=spice only_toplevel=false value=
"
* let sets vectors to a plot, while set sets a variable, globally accessible in .control
.tran 100p 200n
.op
.save all

*.control
*  set appendwrite
*  op
*  show
*  let sig = v(signal_out)
*  save all
*  write buffer_tb.raw
*.endc
"
}
C {symbols/nfet_03v3.sym} -570 20 0 0 {name=M_nmos_pos
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
C {symbols/nfet_03v3.sym} -310 20 0 1 {name=M_nmos_neg
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
C {ipin.sym} -680 -190 0 0 {name=p1 lab=VDD}
C {ipin.sym} -670 20 0 0 {name=p2 lab=Vin_plus
}
C {ipin.sym} -670 80 0 0 {name=p4 lab=Vin_minus
}
C {iopin.sym} -440 200 1 0 {name=p7 lab=I_bias}
C {symbols/pfet_03v3.sym} -530 -100 0 1 {name=M_pmos_diode
L=0.28u
W=17u
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
C {symbols/pfet_03v3.sym} -350 -100 0 0 {name=M_pmos_mirror
L=0.28u
W=17u
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
C {lab_pin.sym} -580 -100 0 0 {name=p8 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -300 -100 0 1 {name=p13 sig_type=std_logic lab=VDD}
C {isource.sym} -330 -370 0 0 {name=I0 value=28u}
C {gnd.sym} -330 -280 0 0 {name=l9 lab=GND}
C {lab_pin.sym} -330 -400 0 1 {name=p14 sig_type=std_logic lab=I_bias}
C {isource.sym} -20 100 0 0 {name=Ibias_SF value=8000u}
C {gnd.sym} -20 160 0 0 {name=l1 lab=GND}
C {lab_wire.sym} -110 -40 0 0 {name=p3 sig_type=std_logic lab=Vota}
C {lab_wire.sym} -490 -400 0 0 {name=p16 sig_type=std_logic lab=Vin_minus
}
C {vsource.sym} -490 -350 0 0 {name=vrf_minus
value="sin( 0.5 0.01 10e6 0 0 180 )"
savecurrent=true
hide_texts=true}
C {gnd.sym} -490 -300 0 0 {name=l2 lab=GND}
C {lab_wire.sym} 30 10 1 1 {name=p5 sig_type=std_logic lab=VOUT}
C {launcher.sym} 200 -670 0 0 {name=h5
descr="load waves ctrl+left click" 
tclcommand="xschem raw_read $netlist_dir/buffer_tb.raw tran"
}
C {launcher.sym} 190 -720 0 0 {name=h2
descr="Run ngSpice simulation (ctrl+left-click)" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {gnd.sym} -520 20 0 0 {name=l6 lab=GND}
C {gnd.sym} -360 20 0 0 {name=l10 lab=GND}
C {gnd.sym} 60 -40 0 0 {name=l11 lab=GND}
C {src/design_xsch/Oscilloscope-probe.sym} 240 10 0 0 {name=x1}
C {lab_wire.sym} 760 -210 1 0 {name=p6 sig_type=std_logic lab=signal_out}
