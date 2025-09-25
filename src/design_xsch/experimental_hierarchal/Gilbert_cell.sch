v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 1760 -1180 2560 -780 {flags=graph,unlocked
y1=-0.00012
y2=2.5
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=3e-08
divx=5
subdivx=4
xlabmag=1.0
ylabmag=1.0


dataset=-1
unitx=1
logx=0
logy=0
color="4 6 7"
node="v_rf
v_lo
\\"diff_output; v_out_p v_out_n -\\""
rainbow=1
rawfile=$netlist_dir/Gilbert_sim.raw
sim_type=tran
autoload=1}
B 2 1760 -1610 2560 -1210 {flags=graph,unlocked
y1=-0.144
y2=0.216
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=5e+11
divx=5
subdivx=4
xlabmag=1.0
ylabmag=1.0


dataset=-1
unitx=1
logx=0
logy=0

sim_type=sp
rawfile=$netlist_dir/Gilbert_sim.raw
autoload=1
sweep=frequency


rainbow=1

color="4 5"
node="v_rf_diff
v_out_diff"}
B 2 1760 -2030 2560 -1630 {flags=graph,unlocked
y1=0
y2=2
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-5e-09
x2=9.5e-08
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
B 2 2590 -1180 3390 -780 {flags=graph,unlocked
y1=4.6000001e-08
y2=2.76e-07
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=2.1601686
x2=2.4489349
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0


dataset=-1
unitx=1
logx=0
logy=0
rawfile=$netlist_dir/Gilbert_sim.raw
sweep=v(net1)
sim_type=tran}
B 2 2590 -1610 3390 -1210 {flags=graph,unlocked
y1=0.8
y2=2.8
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=4.6336307e+09
x2=7.5851097e+09
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
x2=3e-08
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

Gilbert cell mixer for FM radio receiver, 
performing downconversion of a 89.0MHz signal
to an intermediate frequency of 10.7Mhz
f_LO = 100 MHz
f_RF = 89.0 MHz
f_IF = f_LO - f_RF = 11 MHz} 2870 -2390 0 0 0.4 0.4 {}
N 640 -910 760 -910 {
lab=V_RF}
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
N 910 -840 910 -780 {
lab=#net3}
N 990 -840 990 -780 {
lab=#net3}
N 950 -640 950 -610 {
lab=GND}
N 910 -780 910 -760 {
lab=#net3}
N 990 -780 990 -760 {
lab=#net3}
N 910 -700 910 -640 {
lab=GND}
N 910 -640 990 -640 {
lab=GND}
N 990 -700 990 -640 {
lab=GND}
N 950 -970 950 -950 {
lab=GND}
N 800 -1150 800 -1130 {
lab=GND}
N 1090 -1150 1090 -1130 {
lab=GND}
C {ipin.sym} 630 -1090 0 0 {name=p1 lab=V_LO}
C {ipin.sym} 630 -1000 0 0 {name=p2 lab=V_LO_b
}
C {ipin.sym} 630 -910 0 0 {name=p3 lab=V_RF}
C {ipin.sym} 630 -820 2 1 {name=p4 lab=V_RF_b
}
C {opin.sym} 1190 -1290 0 0 {name=p5 lab=V_out_p}
C {opin.sym} 1190 -1260 0 0 {name=p7 lab=V_out_n}
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
    * sine-wave LO
    * set cm_lo = 0.5
    * set freq_lo = 2.50G 
    * set amp_lo = 0.5
    * alter @V_LO[sin] = [ $cm_lo $amp_lo $freq_lo 0 ]
    * alter @V_LO_b[sin] = [ $cm_lo $amp_lo $freq_lo 0 0 180 ]

    set freq_lo = 100Meg
    set cm_lo = 1.8
    set amp_lo = 0.25

    set cm_rf  = 1.6
    set freq_rf = 89Meg
    set amp_rf  = 0.2

    * set the parameters to the voltage sources
    * alter @V_LO[pulse] = [ 2 2.5 0 0.5p 0.5p 5n 10n ]
    * alter @V_LO_b[pulse] = [ 2 2.5 5n 0.5p 0.5p 5n 10n]
    alter @V_LO[sin] = [ $cm_lo $amp_lo $freq_lo 0 ]
    alter @V_LO_b[sin] = [ $cm_lo $amp_lo $freq_lo 0 0 180 ]
    alter @V_RF[sin] = [ $cm_rf $amp_rf $freq_rf 0 ]
    alter @V_RF_b[sin] = [ $cm_rf $amp_rf $freq_rf 0 0 180 ]

    save all
    
    * operating point
    op
    show

    * save transistor op parameters
    * diff_pair_1 transistors
    save @m.xdiff_pair_rf.xm1.m0[vgs]
    save @m.xdiff_pair_rf.xm1.m0[vds]
    save @m.xdiff_pair_rf.xm1.m0[id]
    save @m.xdiff_pair_rf.xm1.m0[gm]
    save @m.xdiff_pair_rf.xm1.m0[vth]
    save @m.xdiff_pair_rf.xm1.m0[cgg]
    save @m.xdiff_pair_rf.xm2.m0[vgs]
    save @m.xdiff_pair_rf.xm2.m0[vds]
    save @m.xdiff_pair_rf.xm2.m0[id]
    save @m.xdiff_pair_rf.xm2.m0[gm]
    save @m.xdiff_pair_rf.xm2.m0[vth]
    save @m.xdiff_pair_rf.xm2.m0[cgg]
    
    * diff_pair_2 transistors  
    save @m.xdiff_pair_2.xm1.m0[vgs]
    save @m.xdiff_pair_2.xm1.m0[vds]
    save @m.xdiff_pair_2.xm1.m0[id]
    save @m.xdiff_pair_2.xm1.m0[gm]
    save @m.xdiff_pair_2.xm1.m0[vth]
    save @m.xdiff_pair_2.xm1.m0[cgg]
    save @m.xdiff_pair_2.xm2.m0[vgs]
    save @m.xdiff_pair_2.xm2.m0[vds]
    save @m.xdiff_pair_2.xm2.m0[id]
    save @m.xdiff_pair_2.xm2.m0[gm]
    save @m.xdiff_pair_2.xm2.m0[vth]
    save @m.xdiff_pair_2.xm2.m0[cgg]
    
    * diff_pair_3 transistors
    save @m.xdiff_pair_3.xm1.m0[vgs]
    save @m.xdiff_pair_3.xm1.m0[vds]
    save @m.xdiff_pair_3.xm1.m0[id]
    save @m.xdiff_pair_3.xm1.m0[gm]
    save @m.xdiff_pair_3.xm1.m0[vth]
    save @m.xdiff_pair_3.xm1.m0[cgg]
    save @m.xdiff_pair_3.xm2.m0[vgs]
    save @m.xdiff_pair_3.xm2.m0[vds]
    save @m.xdiff_pair_3.xm2.m0[id]
    save @m.xdiff_pair_3.xm2.m0[gm]
    save @m.xdiff_pair_3.xm2.m0[vth]
    save @m.xdiff_pair_3.xm2.m0[cgg]


    write Gilbert_sim.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 1p 30n
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
    

    fft v_out_diff v_rf_diff
    * Find frequency bins

    * print everything, sanity check
    * set     ; print all available global (?) variables (?)
    * setplot ; print all plots
    * display ; print variables available in current plot

    let freq_res = tran2.freq_res
    let freq_if = abs( $freq_lo - $freq_rf )

    let if_bin = floor( freq_if/freq_res )
    let rf_bin = floor( $freq_rf/freq_res )
    
    * Measure conversion gain (power gain from RF to IF)
    let rf_mag = abs(v_rf_diff[rf_bin])
    let if_mag = abs(v_out_diff[if_bin])
    let conversion_gain_db = 20*log10(if_mag/rf_mag)
    print conversion_gain_db

    write Gilbert_sim.raw

.endc
"}
C {devices/launcher.sym} 1827.5 -722.5 2 1 {name=h2
descr="Run ngSpice simulation (ctrl+left-click)" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 1830 -680 0 0 {name=h1
descr="Load ngSpice waveforms (ctrl+left-click)" 
tclcommand="xschem raw_read $netlist_dir/Gilbert_sim.raw tran"
}
C {lab_wire.sym} 120 -2350 0 0 {name=p8 sig_type=std_logic lab=V_LO}
C {lab_wire.sym} 200 -2350 0 0 {name=p9 sig_type=std_logic lab=V_LO_b
}
C {lab_wire.sym} 270 -2350 0 0 {name=p10 sig_type=std_logic lab=V_RF}
C {lab_wire.sym} 340 -2350 0 0 {name=p11 sig_type=std_logic lab=V_RF_b}
C {lab_wire.sym} 1260 -1090 0 1 {name=p6 sig_type=std_logic lab=V_LO}
C {res.sym} 760 -1340 0 0 {name=R1
value=6K
footprint=1206
device=resistor
m=1
lock=true}
C {res.sym} 1130 -1340 0 0 {name=R2
value=6K
footprint=1206
device=resistor
m=1
lock=true}
C {vdd.sym} 950 -1410 0 0 {name=l6 lab=VDD}
C {vdd.sym} 120 -2170 0 0 {name=l8 lab=VDD}
C {vsource.sym} 120 -2130 0 0 {name=V_PWR value=3.3 savecurrent=true}
C {title-2.sym} 0 0 0 0 {name=l9 author="Time Transcenders" rev=1.0 lock=true page=1}
C {vsource.sym} 120 -2300 0 0 {name=V_LO
* value="pulse(0 1.5 0 1p 1p 0.25n 0.5n)"
value="sin( 1 1 1 0 )"
savecurrent=true
lock=true
hide_texts=true}
C {vsource.sym} 200 -2300 0 0 {name=V_LO_b
* value="pulse(0 1.5 0 1p 1p 0.25n 0.5n)"
value="sin( 1 1 1 0 )"
savecurrent=true
lock=true
hide_texts=true}
C {vsource.sym} 270 -2300 0 0 {name=V_RF
value="sin( 1 1 1 0 )"
savecurrent=true
lock=true
hide_texts=true}
C {vsource.sym} 340 -2300 0 0 {name=V_RF_b
value="sin( 1 1 1 0 0 180 )"
savecurrent=true
lock=true
hide_texts=true}
C {gnd.sym} 120 -2080 0 0 {name=l7 lab=GND}
C {gnd.sym} 120 -2250 0 0 {name=l1 lab=GND}
C {gnd.sym} 200 -2250 0 0 {name=l2 lab=GND}
C {gnd.sym} 270 -2250 0 0 {name=l3 lab=GND}
C {gnd.sym} 340 -2250 0 0 {name=l4 lab=GND}
C {ngspice_probe.sym} 1090 -980 0 0 {name=r3}
C {ngspice_probe.sym} 800 -980 0 0 {name=r4}
C {ngspice_probe.sym} 990 -790 0 0 {name=r5}
C {ngspice_probe.sym} 910 -790 0 0 {name=r6}
C {gnd.sym} 950 -610 0 0 {name=l5 
lab=GND}
C {isource.sym} 910 -730 0 0 {name=I0 value=100u}
C {isource.sym} 990 -730 0 0 {name=I1 value=100u}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/experimental/diff_pair.sym} 800 -1050 0 0 {name=xdiff_pair_2 mult=1
+ W_neg=24u W_pos=24u}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/experimental/diff_pair.sym} 1090 -1050 0 0 {name=xdiff_pair_3 mult=1
+ W_neg=24u W_pos=24u}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/experimental/diff_pair_with_source_degeneration.sym} 950 -770 0 0 {name=xdiff_pair_rf mult=1
+ W_neg=12u W_pos=12u RS=2K}
C {gnd.sym} 950 -970 2 1 {name=l10 
lab=GND}
C {gnd.sym} 800 -1150 2 1 {name=l11 
lab=GND}
C {gnd.sym} 1090 -1150 2 1 {name=l12 
lab=GND}
