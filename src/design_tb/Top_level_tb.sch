v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 2450 -1200 3250 -800 {flags=graph,unlocked
y1=-1.2
y2=3
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-1.5e-08
x2=2.85e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0


dataset=-1
unitx=1
logx=0
logy=0
rainbow=1
color="4 8 6 7"
node="v_rf
v_lo
\\"diff_output; v_out_p v_out_n -\\"
v_out_p"
rawfile=$netlist_dir/Gilbert_cell_tb_sim.raw
sim_type=tran
autoload=1}
B 2 2450 -1630 3250 -1230 {flags=graph,unlocked
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
rawfile=$netlist_dir/Gilbert_cell_tb_sim.raw
sim_type=sp
sweep=frequency
autoload=1}
T {Desription

Gilbert cell mixer for FM radio receiver, 
performing downconversion of a 89.0MHz signal
to an intermediate frequency of 10.7Mhz
f_LO = 100 MHz
f_RF = 89.3 MHz
f_IF = f_LO - f_RF = 10.7 MHz} 2880 -2390 0 0 0.4 0.4 {}
T {f_LO = 100 MHz
f_RF = 89.7 MHz

f_IF = f_LO - f_RF 
       = 10.7 MHz} 3250 -1200 0 0 0.4 0.4 {}
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
N 200 -1240 210 -1240 {
lab=V_RF_b}
N 200 -1270 260 -1270 {
lab=V_RF}
N 210 -1240 250 -1240 {
lab=V_RF_b}
N 460 -1500 460 -1440 {
lab=V_LO}
N 510 -1500 510 -1440 {
lab=V_LO_b}
N 730 -1280 780 -1280 {
lab=V_out_p}
N 730 -1230 780 -1230 {
lab=V_out_n}
N 460 -1520 460 -1500 {
lab=V_LO}
N 510 -1520 510 -1500 {
lab=V_LO_b}
N 670 -1230 730 -1230 {
lab=V_out_n}
N 670 -1280 730 -1280 {
lab=V_out_p}
N 250 -1240 300 -1240 {
lab=V_RF_b}
N 260 -1270 300 -1270 {
lab=V_RF}
N 440 -1050 440 -930 {
lab=VDD}
N 530 -1050 530 -930 {
lab=GND}
N 440 -930 440 -860 {
lab=VDD}
N 410 -860 440 -860 {
lab=VDD}
N 410 -880 410 -860 {
lab=VDD}
N 530 -930 530 -880 {
lab=GND}
N 470 -1070 470 -1030 {
lab=I_bias_pos}
N 440 -1080 440 -1050 {
lab=VDD}
N 530 -1080 530 -1050 {
lab=GND}
N 470 -1030 470 -1010 {
lab=I_bias_pos}
N 120 -1810 120 -1760 {
lab=GND}
N 120 -1760 140 -1760 {
lab=GND}
N 170 -1760 170 -1740 {
lab=GND}
N 120 -1910 120 -1870 {
lab=I_BIAS}
N 140 -1760 220 -1760 {
lab=GND}
N 220 -1810 220 -1760 {
lab=GND}
N 220 -1910 220 -1870 {
lab=I_BIAS}
N 350 -540 390 -550 {
lab=GND}
N 120 -1910 220 -1910 {
lab=I_BIAS}
N 170 -1980 170 -1910 {
lab=I_BIAS}
N 330 -720 400 -720 {
lab=I_BIAS}
N 460 -780 470 -1010 {
lab=I_bias_pos}
N 780 -1230 960 -1230 {
lab=V_out_n}
N 780 -1280 960 -1280 {
lab=V_out_p}
N 1020 -1390 1020 -1330 {
lab=VDD}
N 1050 -1190 1050 -1110 {
lab=GND}
N 1140 -1250 1260 -1250 {
lab=#net1}
N 1860 -1540 1860 -1470 {
lab=Oscilloscope_signal}
N 490 -1070 490 -780 {
lab=#net2}
N 460 -660 460 -640 {
lab=GND}
N 520 -780 1020 -1150 {
lab=#net3}
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
    set amp_lo = 0.4

    set cm_rf  = 1.2
    set freq_rf = 89.3Meg
    * set freq_rf = 10.7Meg
    set amp_rf  = 0.1

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

    write Top_level_sim.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 1p 0.1u
    write Top_level_sim.raw

    * Calculate differential output for conversion gain measurement
    let v_out_diff = v(v_out_p)-v(v_out_n)
    let v_rf_diff = v(v_rf)-v(v_rf_b)
    let v_lo_diff = v(v_lo)-v(v_lo_b)

    
    * Extract IF component at 100MHz using FFT
    linearize v_out_diff v_rf_diff v_lo_diff
    let time_step = 1e-12
    let sample_freq = 1/time_step
    let npts = length(v_out_diff)
    let freq_res = sample_freq/npts
    

    fft v_out_diff v_rf_diff v_lo_diff

    * print everything, sanity check
    * set     ; print all available global (?) variables (?)
    * setplot ; print all plots
    * display ; print variables available in current plot
    
    let freq_res = tran2.freq_res
    let freq_if = abs ( $freq_lo - $freq_rf )

    * Define bandwidth for power integration (10MHz around nominal frequencies).
    *  To improve resolution increase time of tran simulation, reduce time step, in order to reduce FFT resolution
    let bandwidth = 10e6
    let bin_width = floor(bandwidth/freq_res + 0.5)
   
    * Find center bins for RF and IF frequencies
    let rf_center_bin = floor( $freq_rf/freq_res + 0.5 )
    let if_center_bin = floor( freq_if/freq_res + 0.5 )

    * Calculate power by summing magnitude squared over the bandwidth
    * RF power integration (±10MHz around freq_rf)
    let rf_power_total = 0
    let i = rf_center_bin - bin_width
    while i <= rf_center_bin + bin_width
        if i>0 & i < length(v_rf_diff)
            let bin_freq = i * freq_res
            * print bin_freq
            * print abs(v_rf_diff[i])
            let rf_power_total = rf_power_total + abs(v_rf_diff[i])^2
        end
        let i = i + 1
    end
    
    * IF power integration (±10MHz around freq_if)  
    let if_power_total = 0
    let j = if_center_bin - bin_width
    while j <= if_center_bin + bin_width
        if j >= 0 & j < length(v_out_diff)
            let bin_freq = j * freq_res
            * print bin_freq
            * print abs(v_out_diff[j])
            let if_power_total = if_power_total + abs(v_out_diff[j])^2
        end
        let j = j + 1
    end

    print if_power_total
    print rf_power_total

    let conversion_gain_db = 10*log10(if_power_total/rf_power_total)
    print conversion_gain_db

    write Top_level_sim.raw

.endc
"}
C {devices/launcher.sym} 2497.5 -722.5 2 1 {name=h2
descr="Run ngSpice simulation (ctrl+left-click)" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 2500 -680 0 0 {name=h1
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
C {ipin.sym} 460 -1520 3 1 {name=p1 lab=V_LO}
C {ipin.sym} 510 -1520 3 1 {name=p2 lab=V_LO_b
}
C {ipin.sym} 200 -1270 0 0 {name=p3 lab=V_RF}
C {ipin.sym} 200 -1240 2 1 {name=p4 lab=V_RF_b
}
C {opin.sym} 780 -1280 0 0 {name=p5 lab=V_out_p}
C {opin.sym} 780 -1230 0 0 {name=p7 lab=V_out_n}
C {/foss/designs/Chipathon_2025_gLayout/src/design_xsch/Gilbert_cell_no_hierarchy.sym} 480 -1260 2 1 {name=xGilbert_mixer}
C {isource.sym} 120 -1840 0 0 {name=I0 value=50u}
C {isource.sym} 220 -1840 0 0 {name=I1 value=50u}
C {vdd.sym} 410 -880 0 0 {name=l10 lab=VDD}
C {gnd.sym} 530 -880 0 0 {name=l11 lab=GND}
C {gnd.sym} 170 -1740 0 0 {name=l6 lab=GND}
C {lab_pin.sym} 470 -1010 3 0 {name=p6 sig_type=std_logic lab=I_bias_pos}
C {/foss/designs/Chipathon_2025_gLayout/src/design_xsch/5T-OTA-buffer_no_hierarchy.sym} 1110 -1250 0 0 {name=x1}
C {/foss/designs/Chipathon_2025_gLayout/src/design_xsch/Dummy_devices_all.sym} 540 -550 0 0 {name=x3}
C {gnd.sym} 350 -540 0 0 {name=l5 lab=GND}
C {/foss/designs/Chipathon_2025_gLayout/src/design_xsch/Biasing_network_no_hierarchy.sym} 490 -720 0 0 {name=x4}
C {lab_pin.sym} 170 -1980 3 1 {name=p13 sig_type=std_logic lab=I_BIAS}
C {lab_pin.sym} 330 -720 0 0 {name=p14 sig_type=std_logic lab=I_BIAS}
C {vdd.sym} 1020 -1390 0 0 {name=l12 lab=VDD}
C {gnd.sym} 1050 -1110 0 0 {name=l13 lab=GND}
C {/foss/designs/Chipathon_2025_gLayout/src/design_xsch/Oscilloscope-probe.sym} 1410 -1250 0 0 {name=x_Probe_x10}
C {opin.sym} 1860 -1540 0 0 {name=p16 lab=Oscilloscope_signal}
C {gnd.sym} 460 -640 0 0 {name=l14 lab=GND}
