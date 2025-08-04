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
rawfile=$netlist_dir/Gilbert_cell_tb_sim.raw
sim_type=tran}
B 2 1780 -1640 2580 -1240 {flags=graph,unlocked
y1=3.2e-14
y2=0.5
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
v_out_diff

v_lo_diff"
color="4 6 8"
dataset=-1
unitx=1
logx=0
logy=0
rainbow=1
rawfile=$netlist_dir/Gilbert_cell_tb_sim.raw
sim_type=sp
sweep=frequency
autoload=1}
B 2 1780 -2080 2580 -1680 {flags=graph
y1=0
y2=2
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=10e-6
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
f_RF = 89.3 MHz
f_IF = f_LO - f_RF = 10.7 MHz} 2870 -2390 0 0 0.4 0.4 {}
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
N 120 -2100 120 -2080 {
lab=GND}
N 120 -2170 120 -2160 {
lab=VDD}
N 640 -1270 650 -1270 {
lab=V_RF_b}
N 640 -1300 700 -1300 {
lab=V_RF}
N 650 -1270 690 -1270 {
lab=V_RF_b}
N 900 -1530 900 -1470 {
lab=V_LO}
N 950 -1530 950 -1470 {
lab=V_LO_b}
N 1170 -1310 1220 -1310 {
lab=V_out_p}
N 1170 -1260 1220 -1260 {
lab=V_out_n}
N 900 -1550 900 -1530 {
lab=V_LO}
N 950 -1550 950 -1530 {
lab=V_LO_b}
N 1110 -1260 1170 -1260 {
lab=V_out_n}
N 1110 -1310 1170 -1310 {
lab=V_out_p}
N 690 -1270 740 -1270 {
lab=V_RF_b}
N 700 -1300 740 -1300 {
lab=V_RF}
N 880 -1080 880 -960 {
lab=VDD}
N 970 -1080 970 -960 {
lab=GND}
N 880 -960 880 -890 {
lab=VDD}
N 850 -890 880 -890 {
lab=VDD}
N 850 -910 850 -890 {
lab=VDD}
N 970 -960 970 -910 {
lab=GND}
N 910 -1100 910 -1060 {
lab=I_bias_pos}
N 930 -1100 930 -1060 {
lab=I_bias_neg}
N 880 -1110 880 -1080 {
lab=VDD}
N 970 -1110 970 -1080 {
lab=GND}
N 930 -1060 930 -960 {
lab=I_bias_neg}
N 910 -1060 910 -1040 {
lab=I_bias_pos}
N 120 -1810 120 -1760 {
lab=GND}
N 120 -1760 140 -1760 {
lab=GND}
N 170 -1760 170 -1740 {
lab=GND}
N 120 -1910 120 -1870 {
lab=I_bias_pos}
N 140 -1760 220 -1760 {
lab=GND}
N 220 -1810 220 -1760 {
lab=GND}
N 220 -1910 220 -1870 {
lab=I_bias_neg}
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
    * set freq_rf = 89.3Meg
    set freq_rf = 10Meg
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
    save @m.xgilbert_mixer.xm_rf_pos.m0[vgs]
    save @m.xgilbert_mixer.xm_rf_pos.m0[vds]
    save @m.xgilbert_mixer.xm_rf_pos.m0[id]
    save @m.xgilbert_mixer.xm_rf_pos.m0[gm]
    save @m.xgilbert_mixer.xm_rf_pos.m0[vth]
    save @m.xgilbert_mixer.xm_rf_pos.m0[cgg]
    save @m.xgilbert_mixer.xm_rf_neg.m0[vgs]
    save @m.xgilbert_mixer.xm_rf_neg.m0[vds]
    save @m.xgilbert_mixer.xm_rf_neg.m0[id]
    save @m.xgilbert_mixer.xm_rf_neg.m0[gm]
    save @m.xgilbert_mixer.xm_rf_neg.m0[vth]
    save @m.xgilbert_mixer.xm_rf_neg.m0[cgg]
    
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

    write Gilbert_cell_tb_sim.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 1p 300n
    write Gilbert_cell_tb_sim.raw

    * Calculate differential output for conversion gain measurement
    let v_out_diff = v(v_out_p)-v(v_out_n)
    let v_rf_diff = v(v_rf)-v(v_rf_b)
    let v_lo_diff = v(v_lo)-v(v_lo_b)

    
    * Extract IF component at 100MHz using FFT
    linearize v_out_diff v_rf_diff v_lo_diff
    let time_step = 10e-12
    let sample_freq = 1/time_step
    let npts = length(v_out_diff)
    let freq_res = sample_freq/npts
    

    fft v_out_diff v_rf_diff v_lo_diff
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

    write Gilbert_cell_tb_sim.raw

.endc
"}
C {devices/launcher.sym} 1827.5 -722.5 2 1 {name=h2
descr="Run ngSpice simulation (ctrl+left-click)" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 1830 -680 0 0 {name=h1
descr="Load ngSpice waveforms (ctrl+left-click)" 
tclcommand="xschem raw_read $netlist_dir/Gilbert_cell_tb_sim.raw tran"
}
C {lab_wire.sym} 120 -2350 0 0 {name=p8 sig_type=std_logic lab=V_LO}
C {lab_wire.sym} 200 -2350 0 0 {name=p9 sig_type=std_logic lab=V_LO_b
}
C {lab_wire.sym} 270 -2350 0 0 {name=p10 sig_type=std_logic lab=V_RF}
C {lab_wire.sym} 340 -2350 0 0 {name=p11 sig_type=std_logic lab=V_RF_b}
C {vdd.sym} 120 -2170 0 0 {name=l8 lab=VDD}
C {vsource.sym} 120 -2130 0 0 {name=V_PWR value=3.3 savecurrent=true}
C {title-2.sym} 0 0 0 0 {name=l9 author="Time Transcenders" lock=true rev=1.0 page=1}
C {vsource.sym} 120 -2300 0 0 {name=V_LO
* value="pulse(0 1.5 0 1p 1p 0.25n 0.5n)"
value="sin( 1 1 1 0 )"
savecurrent=true
hide_texts=true}
C {vsource.sym} 200 -2300 0 0 {name=V_LO_b
* value="pulse(0 1.5 0 1p 1p 0.25n 0.5n)"
value="sin( 1 1 1 0 )"
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
C {gnd.sym} 120 -2250 0 0 {name=l1 lab=GND}
C {gnd.sym} 200 -2250 0 0 {name=l2 lab=GND}
C {gnd.sym} 270 -2250 0 0 {name=l3 lab=GND}
C {gnd.sym} 340 -2250 0 0 {name=l4 lab=GND}
C {ipin.sym} 900 -1550 3 1 {name=p1 lab=V_LO}
C {ipin.sym} 950 -1550 3 1 {name=p2 lab=V_LO_b
}
C {ipin.sym} 640 -1300 0 0 {name=p3 lab=V_RF}
C {ipin.sym} 640 -1270 2 1 {name=p4 lab=V_RF_b
}
C {opin.sym} 1220 -1310 0 0 {name=p5 lab=V_out_p}
C {opin.sym} 1220 -1260 0 0 {name=p7 lab=V_out_n}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Gilbert_cell_no_hierarchy.sym} 920 -1290 2 1 {name=xGilbert_mixer}
C {isource.sym} 120 -1840 0 0 {name=I0 value=50u}
C {isource.sym} 220 -1840 0 0 {name=I1 value=50u}
C {vdd.sym} 850 -910 0 0 {name=l10 lab=VDD}
C {gnd.sym} 970 -910 0 0 {name=l11 lab=GND}
C {gnd.sym} 170 -1740 0 0 {name=l6 lab=GND}
C {lab_pin.sym} 910 -1040 3 0 {name=p6 sig_type=std_logic lab=I_bias_pos}
C {lab_pin.sym} 930 -980 3 0 {name=p12 sig_type=std_logic lab=I_bias_neg}
C {lab_pin.sym} 120 -1910 3 1 {name=p13 sig_type=std_logic lab=I_bias_pos}
C {lab_pin.sym} 220 -1910 3 1 {name=p14 sig_type=std_logic lab=I_bias_neg}
