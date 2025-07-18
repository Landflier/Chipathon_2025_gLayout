v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 1760 -1180 2560 -780 {flags=graph
y1=-0.0071
y2=1.4
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
color="4 6 8 21 21"
node="v_rf
v_rf_b
v_lo
v_lo_b
\\"diff_output; v_out_p v_out_n -\\""
rainbow=1}
B 2 1760 -1610 2560 -1210 {flags=graph
y1=0.4
y2=2.4
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node=""
color=""
dataset=-1
unitx=1
logx=0
logy=0
}
B 2 1760 -2030 2560 -1630 {flags=graph
y1=0
y2=2
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node=""
color=""
dataset=-1
unitx=1
logx=0
logy=0
}
B 2 2590 -1180 3390 -780 {flags=graph
y1=0
y2=2
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node=""
color=""
dataset=-1
unitx=1
logx=0
logy=0
}
B 2 2590 -1610 3390 -1210 {flags=graph
y1=0
y2=2
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node=""
color=""
dataset=-1
unitx=1
logx=0
logy=0
}
B 2 2590 -2030 3390 -1630 {flags=graph
y1=0
y2=2
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node=""
color=""
dataset=-1
unitx=1
logx=0
logy=0
}
T {Desription

A double-balanced mixer, Gilbert cell topology
f_LO = 2.50 GHz
f_RF = 2.40 GHz
f_IF = f_LO - f_RF = 100 MHz} 2870 -2390 0 0 0.4 0.4 {}
N 640 -910 760 -910 {
lab=V_RF}
N 950 -730 950 -700 {
lab=GND}
N 120 -2270 120 -2250 {
lab=GND}
N 120 -2350 120 -2330 {lab=V_LO}
N 200 -2270 200 -2250 {
lab=GND}
N 200 -2350 200 -2330 {
lab=V_LO_b}
N 270 -2270 270 -2250 {
lab=GND}
N 270 -2350 270 -2330 {
lab=V_RF}
N 340 -2270 340 -2250 {
lab=GND}
N 340 -2350 340 -2330 {
lab=V_RF_b}
N 900 -1090 990 -1090 {
lab=V_LO_b}
N 1190 -1090 1260 -1090 {
lab=V_LO}
N 630 -1090 700 -1090 {lab=V_LO}
N 630 -1000 950 -1000 {lab=V_LO_b}
N 950 -1090 950 -1000 {
lab=V_LO_b}
N 760 -910 850 -910 {
lab=V_RF}
N 800 -970 910 -970 {
lab=#net1}
N 800 -1020 800 -970 {
lab=#net1}
N 990 -970 1090 -970 {
lab=#net2}
N 1090 -1020 1090 -970 {
lab=#net2}
N 640 -820 1090 -820 {
lab=V_RF_b}
N 1090 -910 1090 -820 {
lab=V_RF_b}
N 1050 -910 1090 -910 {
lab=V_RF_b}
N 950 -840 950 -790 {
lab=#net3}
N 630 -910 640 -910 {
lab=V_RF}
N 630 -820 640 -820 {
lab=V_RF_b}
N 760 -1160 760 -1150 {
lab=V_out_p}
N 1130 -1160 1130 -1150 {
lab=V_out_n}
N 1130 -1230 1130 -1160 {
lab=V_out_n}
N 760 -1310 760 -1160 {
lab=V_out_p}
N 1130 -1310 1130 -1230 {
lab=V_out_n}
N 760 -1410 760 -1370 {
lab=VDD}
N 760 -1410 950 -1410 {
lab=VDD}
N 1130 -1410 1130 -1370 {
lab=VDD}
N 950 -1410 1130 -1410 {
lab=VDD}
N 760 -1290 1190 -1290 {
lab=V_out_p}
N 1130 -1260 1190 -1260 {
lab=V_out_n}
N 120 -2100 120 -2080 {
lab=GND}
N 120 -2170 120 -2160 {
lab=VDD}
N 880 -1230 1050 -1150 {
lab=V_out_p}
N 760 -1230 880 -1230 {
lab=V_out_p}
N 1010 -1230 1130 -1230 {
lab=V_out_n}
N 840 -1150 1010 -1230 {
lab=V_out_n}
C {ipin.sym} 630 -1090 0 0 {name=p1 lab=V_LO}
C {ipin.sym} 630 -1000 0 0 {name=p2 lab=V_LO_b
}
C {ipin.sym} 630 -910 0 0 {name=p3 lab=V_RF}
C {ipin.sym} 630 -820 2 1 {name=p4 lab=V_RF_b
}
C {opin.sym} 1190 -1290 0 0 {name=p5 lab=V_out_p}
C {opin.sym} 1190 -1260 0 0 {name=p7 lab=V_out_n}
C {isource.sym} 950 -760 0 0 {name=I0 value=100m}
C {code.sym} 70 -190 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"
}
C {code.sym} 2695 -2385 0 0 {name=SPICE only_toplevel=true 
value="
* let sets vectors to a plot, while set sets a variable, globally accessible in .control
.control

    * Set frequency and amplitude variables to proper values from within the control sequence
    set cm_lo = 1.0
    set freq_lo = 2.50G 
    set amp_lo = 0.4

    set cm_rf  = 1.0
    set freq_rf = 2.40G
    set amp_rf  = 0.4

    set freq_if = ( $freq_lo - $freq_rf )
    echo 'printing freq_if after calculation'
    print freq_if

    * set the parameters to the voltage sources
    alter @V_LO[sin] = [ $cm_lo $amp_lo $freq_lo 0 ]
    alter @V_LO_b[sin] = [ $cm_lo $amp_lo $freq_lo 0 0 180 ]
    alter @V_RF[sin] = [ $cm_rf $amp_rf $freq_rf 0 ]
    alter @V_RF_b[sin] = [ $cm_rf $amp_rf $freq_rf 0 0 180 ]

    save all
    
    * operating point
    op
    write Gilbert_sim.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 1p 10n
    write Gilbert_sim.raw

    * Calculate differential output for conversion gain measurement
    let v_out_diff = v(v_out_p)-v(v_out_n)
    let v_rf_diff = v(v_rf)-v(v_rf_b)
    
    * Extract IF component at 100MHz using FFT
    linearize v_out_diff v_rf_diff
    let time_step = 10e-12
    let sample_freq = 1/time_step
    let npts = length(v_out_diff)
    let freq_res = sample_freq/npts
    display ; print variables available in current plot
    

    fft v_out_diff v_rf_diff
    
    * Find frequency bins
    set     ; print all available global (?) variables (?)
    setplot ; print all plots
    display ; print variables available in current plot

    
    print $freq_if
    let if_bin = floor(freq_if/freq_res)
    let rf_bin = floor(freq_rf/freq_res)
    
    * Measure conversion gain (power gain from RF to IF)
    let rf_mag = abs(v_rf_diff[rf_bin])
    let if_mag = abs(v_out_diff[if_bin])
    let conversion_gain_db = 20*log10(if_mag/rf_mag)
    print conversion_gain_db

    * write Gilbert_cell.raw

.endc
"}
C {devices/launcher.sym} 1827.5 -717.5 0 0 {name=h2
descr="simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 1830 -680 0 0 {name=h1
descr="load waves" 
tclcommand="xschem raw_read $netlist_dir/Gilbert_sim.raw tran"
}
C {lab_wire.sym} 120 -2350 0 0 {name=p8 sig_type=std_logic lab=V_LO}
C {lab_wire.sym} 200 -2350 0 0 {name=p9 sig_type=std_logic lab=V_LO_b
}
C {lab_wire.sym} 270 -2350 0 0 {name=p10 sig_type=std_logic lab=V_RF}
C {lab_wire.sym} 340 -2350 0 0 {name=p11 sig_type=std_logic lab=V_RF_b}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/diff_pair.sym} 950 -870 0 0 {name=Xdiff_pair_1
hide_texts=false
W_pos=2u
lock=true}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/diff_pair.sym} 800 -1050 0 0 {name=Xdiff_pair_2
hide_texts=false
lock=true}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/diff_pair.sym} 1090 -1050 0 0 {name=Xdiff_pair_3
hide_texts=false
lock=true}
C {lab_wire.sym} 1260 -1090 0 1 {name=p6 sig_type=std_logic lab=V_LO}
C {res.sym} 760 -1340 0 0 {name=R1
value=1K
footprint=1206
device=resistor
m=1
lock=true}
C {res.sym} 1130 -1340 0 0 {name=R2
value=1K
footprint=1206
device=resistor
m=1
lock=true}
C {vdd.sym} 950 -1410 0 0 {name=l6 lab=VDD}
C {vdd.sym} 120 -2170 0 0 {name=l8 lab=VDD}
C {vsource.sym} 120 -2130 0 0 {name=V_PWR value=3.3 savecurrent=true}
C {title-2.sym} 0 0 0 0 {name=l9 author="Time Transcenders" rev=1.0 lock=true page=1}
C {vsource.sym} 120 -2300 0 0 {name=V_LO
value="sin( 1 1 1 0 )"
savecurrent=true
hide_texts=true}
C {vsource.sym} 200 -2300 0 0 {name=V_LO_b
value="sin( 1 1 1 0 0 180 )"
savecurrent=true
hide_texts=true}
C {vsource.sym} 270 -2300 0 0 {name=V_RF
value="sin( 1 1 1 0 )"
savecurrent=true
hide_texts=true}
C {vsource.sym} 340 -2300 0 0 {name=V_RF_b
value="sin( 1 1 1 0 0 180 )"
savecurrent=true
hide_texts=true}
C {gnd.sym} 120 -2080 0 0 {name=l7 lab=GND}
C {gnd.sym} 950 -700 0 0 {name=l11 lab=GND}
C {gnd.sym} 120 -2250 0 0 {name=l1 lab=GND}
C {gnd.sym} 200 -2250 0 0 {name=l2 lab=GND}
C {gnd.sym} 270 -2250 0 0 {name=l3 lab=GND}
C {gnd.sym} 340 -2250 0 0 {name=l4 lab=GND}
