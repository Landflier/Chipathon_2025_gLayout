v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 1780 -1200 2580 -800 {flags=graph,unlocked
y1=-0.58
y2=2.1
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
color="4 8 6"
node="v_rf
v_lo
\\"diff_output; v_out_p v_out_n -\\""
rawfile=$netlist_dir/Gilbert_no_hierarchy_sim.raw
sim_type=tran}
B 2 1780 -1640 2580 -1240 {flags=graph,unlocked
y1=-0.015232865
y2=0.46476713
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-23992288
x2=3.3808633e+08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="v_rf_diff
v_out_diff"
color="15 4"
dataset=-1
unitx=1
logx=0
logy=0
rainbow=1
rawfile=$netlist_dir/Gilbert_no_hierarchy_sim.raw
sim_type=sp
sweep=frequency
autoload=1}
T {Desription

Gilbert cell mixer for FM radio receiver, 
performing downconversion of a 89.0MHz signal
to an intermediate frequency of 10.7Mhz
f_LO = 100 MHz
f_RF = 89.3 MHz
f_IF = f_LO - f_RF = 10.7 MHz} 2870 -2390 0 0 0.4 0.4 {}
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
lab=#net4}
N 950 -640 950 -610 {
lab=GND}
N 910 -780 910 -760 {
lab=#net3}
N 990 -780 990 -760 {
lab=#net4}
N 910 -700 910 -640 {
lab=GND}
N 910 -640 990 -640 {
lab=GND}
N 990 -700 990 -640 {
lab=GND}
N 990 -970 990 -940 {
lab=#net2}
N 1050 -1060 1130 -1060 {
lab=#net2}
N 1050 -1150 1050 -1120 {
lab=V_out_p}
N 1130 -1150 1130 -1120 {
lab=V_out_n}
N 840 -1150 840 -1120 {
lab=V_out_n}
N 760 -1150 760 -1120 {
lab=V_out_p}
N 700 -1090 720 -1090 {
lab=V_LO}
N 880 -1090 900 -1090 {
lab=V_LO_b}
N 990 -1090 1010 -1090 {
lab=V_LO_b}
N 1170 -1090 1190 -1090 {
lab=V_LO}
N 1090 -1060 1090 -1020 {
lab=#net2}
N 760 -1060 840 -1060 {
lab=#net1}
N 800 -1060 800 -1020 {
lab=#net1}
N 910 -970 910 -940 {
lab=#net1}
N 850 -910 870 -910 {
lab=V_RF}
N 1030 -910 1050 -910 {
lab=V_RF_b}
N 910 -880 910 -840 {
lab=#net3}
N 990 -880 990 -840 {
lab=#net4}
N 910 -850 920 -850 {
lab=#net3}
N 980 -850 990 -850 {
lab=#net4}
N 910 -910 990 -910 {
lab=GND}
N 760 -1090 840 -1090 {
lab=GND}
N 1050 -1090 1130 -1090 {
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

    set cm_rf  = 1,6
    set freq_rf = 89.3Meg
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
    save @m.xm_rf_pos.m0[vgs]
    save @m.xm_rf_pos.m0[vds]
    save @m.xm_rf_pos.m0[id]
    save @m.xm_rf_pos.m0[gm]
    save @m.xm_rf_pos.m0[vth]
    save @m.xm_rf_pos.m0[cgg]
    save @m.xm_rf_neg.m0[vgs]
    save @m.xm_rf_neg.m0[vds]
    save @m.xm_rf_neg.m0[id]
    save @m.xm_rf_neg.m0[gm]
    save @m.xm_rf_neg.m0[vth]
    save @m.xm_rf_neg.m0[cgg]
    
    * diff_pair_2 transistors  
    * save @m.xdiff_pair_2.xm1.m0[vgs]
    * save @m.xdiff_pair_2.xm1.m0[vds]
    * save @m.xdiff_pair_2.xm1.m0[id]
    * save @m.xdiff_pair_2.xm1.m0[gm]
    * save @m.xdiff_pair_2.xm1.m0[vth]
    * save @m.xdiff_pair_2.xm1.m0[cgg]
    * save @m.xdiff_pair_2.xm2.m0[vgs]
    * save @m.xdiff_pair_2.xm2.m0[vds]
    * save @m.xdiff_pair_2.xm2.m0[id]
    * save @m.xdiff_pair_2.xm2.m0[gm]
    * save @m.xdiff_pair_2.xm2.m0[vth]
    * save @m.xdiff_pair_2.xm2.m0[cgg]
    
    * diff_pair_3 transistors
    * save @m.xdiff_pair_3.xm1.m0[vgs]
    * save @m.xdiff_pair_3.xm1.m0[vds]
    * save @m.xdiff_pair_3.xm1.m0[id]
    * save @m.xdiff_pair_3.xm1.m0[gm]
    * save @m.xdiff_pair_3.xm1.m0[vth]
    * save @m.xdiff_pair_3.xm1.m0[cgg]
    * save @m.xdiff_pair_3.xm2.m0[vgs]
    * save @m.xdiff_pair_3.xm2.m0[vds]
    * save @m.xdiff_pair_3.xm2.m0[id]
    * save @m.xdiff_pair_3.xm2.m0[gm]
    * save @m.xdiff_pair_3.xm2.m0[vth]
    * save @m.xdiff_pair_3.xm2.m0[cgg]

    write Gilbert_no_hierarchy_sim.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 1p 300n
    write Gilbert_no_hierarchy_sim.raw

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

    write Gilbert_no_hierarchy_sim.raw

.endc
"}
C {devices/launcher.sym} 1827.5 -722.5 2 1 {name=h2
descr="Run ngSpice simulation (ctrl+left-click)" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 1830 -680 0 0 {name=h1
descr="Load ngSpice waveforms (ctrl+left-click)" 
tclcommand="xschem raw_read $netlist_dir/Gilbert_no_hierarchy_sim.raw tran"
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
C {gnd.sym} 950 -610 0 0 {name=l5 lab=GND}
C {isource.sym} 910 -730 0 0 {name=I0 value=50u}
C {isource.sym} 990 -730 0 0 {name=I1 value=50u}
C {symbols/nfet_03v3.sym} 740 -1090 0 0 {name=M_dp_lo_pos
L=0.28u
W=24u
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
C {symbols/nfet_03v3.sym} 860 -1090 0 1 {name=M_dp_lo_neg
L=0.28u
W=24u
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
C {symbols/nfet_03v3.sym} 1030 -1090 0 0 {name=M_dp_lo_b_pos
L=0.28u
W=24u
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
C {symbols/nfet_03v3.sym} 1150 -1090 0 1 {name=M_dp_lo_b_neg
L=0.28u
W=24u
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
C {symbols/nfet_03v3.sym} 890 -910 0 0 {name=M_rf_pos
L=0.28u
W=12u
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
C {symbols/nfet_03v3.sym} 1010 -910 0 1 {name=M_rf_neg
L=0.28u
W=12u
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
C {res.sym} 950 -850 3 0 {name=R7
value=2K
footprint=1206
device=resistor
m=1
lock=true}
C {lab_wire.sym} 950 -910 0 0 {name=p12 sig_type=std_logic lab=GND}
C {lab_wire.sym} 810 -1090 0 0 {name=p13 sig_type=std_logic lab=GND}
C {lab_wire.sym} 1090 -1090 0 0 {name=p14 sig_type=std_logic lab=GND}
