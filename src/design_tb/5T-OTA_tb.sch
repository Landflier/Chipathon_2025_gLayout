v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 1780 -1200 2580 -800 {flags=graph,unlocked
y1=-1.4
y2=2.5
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=3e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0


dataset=-1
unitx=1
logx=0
logy=0
rainbow=1
color="4 8 7 6"
node="v_if
v_if_b
\\"diff_input; v_if v_if_b -\\"
\\" v_out; vout 2 -\\""
rawfile=$netlist_dir/5T-OTA.raw
sim_type=tran
autoload=1}
B 2 1780 -1630 2580 -1230 {flags=graph,unlocked
y1=6e-14
y2=0.8
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-25782827
x2=2.9112984e+08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="v_rf_diff
v_out_diff

v_lo_diff"
color="4 6 8"
dataset=-1
unitx=1
logx=0
logy=0
rainbow=1
rawfile=$netlist_dir/5T-OTA.raw
sim_type=ac
sweep=frequency
autoload=1}
T {Desription

5T-OTA intended to work at ~10 MHz. To be used
as a buffer between the IF output of the Gilbert cell
and the measuring probe outside the chip. Should
also serve as a filter for the higher 
harmonics at over 100MHz

f_LO = 100 MHz
f_RF = 89.3 MHz
f_IF = f_LO - f_RF = 10.7 MHz} 2880 -2390 0 0 0.4 0.4 {}
T {f_LO = 100 MHz
f_RF = 89.7 MHz

f_IF = f_LO - f_RF 
       = 10.7 MHz} 2580 -1200 0 0 0.4 0.4 {}
N 120 -2270 120 -2250 {
lab=GND}
N 120 -2350 120 -2330 {lab=V_IF}
N 200 -2270 200 -2250 {
lab=GND}
N 200 -2350 200 -2330 {
lab=V_IF_b}
N 120 -2100 120 -2080 {
lab=GND}
N 120 -2170 120 -2160 {
lab=VDD}
N 880 -1190 880 -1150 {
lab=I_bias_pos}
N 880 -1150 880 -1130 {
lab=I_bias_pos}
N 120 -1780 120 -1760 {
lab=GND}
N 120 -1920 120 -1880 {
lab=I_bias_pos}
N 880 -1430 880 -1380 {
lab=VDD}
N 710 -1250 820 -1250 {
lab=V_IF_b}
N 710 -1330 820 -1330 {
lab=V_IF}
N 1030 -1290 1140 -1290 {
lab=Vout}
N 120 -1820 120 -1780 {
lab=GND}
N 910 -1210 910 -1170 {
lab=GND}
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
.control

    * Set frequency and amplitude variables to proper values from within the control sequence
    * sine-wave L

    set freq_if = 10.7Meg
    set cm_if = 2
    set amp_if = 0.5

    * set the parameters to the voltage sources
    alter @V_IF[sin] = [ $cm_if $amp_if $freq_if 0 ]
    alter @V_IF_b[sin] = [ $cm_if $amp_if $freq_if 0 0 180 ]

    save all
    
    * operating point
    op
    show
    write 5T-OTA.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 3p 300n
    write 5T-OTA.raw


.endc
"}
C {devices/launcher.sym} 1827.5 -722.5 2 1 {name=h2
descr="Run ngSpice simulation (ctrl+left-click)" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 1830 -680 0 0 {name=h1
descr="Load ngSpice waveforms (ctrl+left-click)" 
tclcommand="xschem raw_read $netlist_dir/5T-OTA.raw tran"
}
C {lab_wire.sym} 120 -2350 0 0 {name=p8 sig_type=std_logic lab=V_IF}
C {lab_wire.sym} 200 -2350 0 0 {name=p9 sig_type=std_logic lab=V_IF_b
}
C {vdd.sym} 120 -2170 0 0 {name=l8 lab=VDD}
C {vsource.sym} 120 -2130 0 0 {name=V_PWR value=3.3 savecurrent=true}
C {title-2.sym} 0 0 0 0 {name=l9 author="Time Transcenders" lock=true rev=1.0 page=1}
C {vsource.sym} 120 -2300 0 0 {name=V_IF
value="sin( 1 1 1 0 )"
savecurrent=true
hide_texts=true}
C {vsource.sym} 200 -2300 0 0 {name=V_IF_b
value="sin( 1 1 1 0 )"
savecurrent=true
hide_texts=true}
C {gnd.sym} 120 -2080 0 0 {name=l7 lab=GND}
C {gnd.sym} 120 -2250 0 0 {name=l1 lab=GND}
C {gnd.sym} 200 -2250 0 0 {name=l2 lab=GND}
C {isource.sym} 120 -1850 0 0 {name=I0 value=10u}
C {vdd.sym} 880 -1430 0 0 {name=l10 lab=VDD}
C {gnd.sym} 120 -1760 0 0 {name=l6 lab=GND}
C {lab_pin.sym} 880 -1130 3 0 {name=p6 sig_type=std_logic lab=I_bias_pos}
C {lab_pin.sym} 120 -1920 3 1 {name=p13 sig_type=std_logic lab=I_bias_pos}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/5T-OTA-buffer_no_hierarchy.sym} 970 -1290 0 0 {name=X5T-OTA}
C {lab_pin.sym} 710 -1330 0 0 {name=p1 sig_type=std_logic lab=V_IF}
C {lab_pin.sym} 710 -1250 0 0 {name=p2 sig_type=std_logic lab=V_IF_b
}
C {opin.sym} 1140 -1290 0 0 {name=p3 lab=Vout}
C {gnd.sym} 910 -1170 0 0 {name=l3 lab=GND}
