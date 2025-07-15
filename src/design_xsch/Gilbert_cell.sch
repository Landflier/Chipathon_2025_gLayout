v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
L 4 192.5 0 1715 0 {}
L 4 0 0 32.5 0 {}
L 4 1715 -1215 1715 0 {}
L 4 0 -1215 1715 -1215 {}
L 4 0 -1215 0 0 {}
L 4 1055 -80 1055 0 {}
L 4 1055 -80 1715 -80 {Gilbert cell}
L 4 1055 -40 1715 -40 {}
L 4 1370 -40 1370 0 {}
L 4 1370 -80 1370 -40 {}
L 4 1225 -40 1225 0 {}
B 2 910 -970 1710 -570 {flags=graph
y1=0.5
y2=2.5
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1e-08
divx=5
subdivx=4
xlabmag=1.0
ylabmag=1.0


dataset=-1
unitx=1
logx=0
logy=0
color="4 5"
node="v_lo_b
v_lo"}
P 5 19 70 -7.5 67.5 -5 62.5 0 67.5 5 73.75 11.25 77.5 15 73.75 15 70 15 67.5 15 65 12.5 62.5 10 57.5 5 52.5 10 50 12.5 47.5 15 45 15 41.25 15 37.5 15 41.25 11.25 {fill=true
bezier=1}
T {@time_last_modified} 1375 -30 0 0 0.4 0.4 {}
T {Time Transcenders} 1060 -70 0 0 0.4 0.4 {}
T {Page @page of @pages} 1060 -30 0 0 0.4 0.4 {}
T {@title} 1375 -60 0 0 0.3 0.3 {vcenter=true}
T {Rev. @rev} 1230 -30 0 0 0.4 0.4 {}
T {SCHEM} 77.5 -12.5 0 0 0.5 0.5 {}
T {Desription

A double-balanced mixer, Gilbert cell topology
f_LO = 2.41 GHz
f_RF = 2.40 GHz
f_IF = f_LO - f_RF = 10 MHz} 1150 -1210 0 0 0.4 0.4 {}
N 240 -340 360 -340 {
lab=V_RF}
N 550 -160 550 -130 {
lab=VSS}
N 160 -1030 160 -1010 {
lab=VSS}
N 160 -1110 160 -1090 {lab=V_LO}
N 240 -1030 240 -1010 {
lab=VSS}
N 240 -1110 240 -1090 {
lab=V_LO_b}
N 310 -1030 310 -1010 {
lab=VSS}
N 310 -1110 310 -1090 {
lab=V_RF}
N 380 -1030 380 -1010 {
lab=VSS}
N 380 -1110 380 -1090 {
lab=V_RF_b}
N 500 -520 590 -520 {
lab=V_LO_b}
N 540 -660 650 -580 {
lab=V_RF}
N 440 -580 560 -660 {
lab=V_RF_b}
N 790 -520 860 -520 {
lab=V_LO}
N 230 -520 300 -520 {lab=V_LO}
N 360 -740 790 -740 {
lab=V_RF}
N 360 -660 540 -660 {
lab=V_RF}
N 730 -710 730 -660 {
lab=V_RF_b}
N 730 -710 790 -710 {
lab=V_RF_b}
N 560 -660 730 -660 {
lab=V_RF_b}
N 230 -430 550 -430 {lab=V_LO_b}
N 550 -520 550 -430 {
lab=V_LO_b}
N 360 -340 450 -340 {
lab=V_RF}
N 400 -400 510 -400 {
lab=#net1}
N 400 -450 400 -400 {
lab=#net1}
N 590 -400 690 -400 {
lab=#net2}
N 690 -450 690 -400 {
lab=#net2}
N 240 -250 690 -250 {
lab=V_RF_b}
N 690 -340 690 -250 {
lab=V_RF_b}
N 650 -340 690 -340 {
lab=V_RF_b}
N 550 -270 550 -220 {
lab=#net3}
N 230 -340 240 -340 {
lab=V_RF}
N 230 -250 240 -250 {
lab=V_RF_b}
N 360 -660 360 -650 {
lab=V_RF}
N 360 -740 360 -650 {
lab=V_RF}
N 730 -660 730 -650 {
lab=V_RF_b}
N 360 -590 360 -580 {
lab=#net4}
N 730 -590 730 -580 {
lab=#net5}
C {ipin.sym} 230 -520 0 0 {name=p1 lab=V_LO}
C {ipin.sym} 230 -430 0 0 {name=p2 lab=V_LO_b
}
C {ipin.sym} 230 -340 0 0 {name=p3 lab=V_RF}
C {ipin.sym} 230 -250 2 1 {name=p4 lab=V_RF_b
}
C {opin.sym} 790 -740 0 0 {name=p5 lab=V_RF}
C {opin.sym} 790 -710 0 0 {name=p7 lab=V_RF_b}
C {isource.sym} 550 -190 0 0 {name=I0 value=1m}
C {gnd.sym} 550 -130 0 0 {name=l1 lab=VSS}
C {code.sym} 30 -140 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"
}
C {code.sym} 975 -1185 0 0 {name=SPICE only_toplevel=false 
value="
.temp 27
.control
save all
tran 1p 10n
write Gilbert_sim.raw
.endc
"}
C {devices/launcher.sym} 1027.5 -517.5 0 0 {name=h2
descr="simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 1030 -480 0 0 {name=h1
descr="load waves" 
tclcommand="xschem raw_read $netlist_dir/Gilbert_sim.raw tran"
}
C {gnd.sym} 160 -1010 0 0 {name=l2 lab=VSS}
C {gnd.sym} 240 -1010 0 0 {name=l3 lab=VSS}
C {gnd.sym} 310 -1010 0 0 {name=l4 lab=VSS}
C {gnd.sym} 380 -1010 0 0 {name=l5 lab=VSS}
C {lab_wire.sym} 160 -1110 0 0 {name=p8 sig_type=std_logic lab=V_LO}
C {lab_wire.sym} 240 -1110 0 0 {name=p9 sig_type=std_logic lab=V_LO_b
}
C {lab_wire.sym} 310 -1110 0 0 {name=p10 sig_type=std_logic lab=V_RF}
C {lab_wire.sym} 380 -1110 0 0 {name=p11 sig_type=std_logic lab=V_RF_b}
C {vsource_arith.sym} 160 -1060 0 0 {name=E1
savecurrent=true
VOL="'1.5 + sin(time * 2.41 * 1e9)'"
hide_texts=true}
C {vsource_arith.sym} 240 -1060 0 0 {name=E2
savecurrent=true
VOL="'1.5 - sin(time * 2.41 * 1e9)'"
hide_texts=true}
C {vsource_arith.sym} 310 -1060 0 0 {name=E4
savecurrent=true
VOL="'1.5 + sin(time * 2.40 * 1e9)'"
hide_texts=true
}
C {vsource_arith.sym} 380 -1060 0 0 {name=E6 
savecurrent=true
VOL="'1.5 - sin(time * 2.40 * 1e9)'"
hide_texts=true
}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/diff_pair.sym} 550 -300 0 0 {name=Xdiff_pair_1
hide_texts=false

}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/diff_pair.sym} 400 -480 0 0 {name=Xdiff_pair_2
hide_texts=false}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/diff_pair.sym} 690 -480 0 0 {name=Xdiff_pair_3
hide_texts=false}
C {lab_wire.sym} 860 -520 0 1 {name=p6 sig_type=std_logic lab=V_LO}
C {res.sym} 730 -620 0 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1}
C {res.sym} 360 -620 0 0 {name=R2
value=1k
footprint=1206
device=resistor
m=1}
