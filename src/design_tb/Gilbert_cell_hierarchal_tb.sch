v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 1780 -1200 2580 -800 {flags=graph,unlocked
y1=-1.2
y2=3
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-5.2133076e-09
x2=1.995867e-07
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

sim_type=tran
autoload=1
rawfile=$netlist_dir/Gilbert_cell_hierarchal_sim.raw}
B 2 1780 -1650 2580 -1250 {flags=graph,unlocked
y1=8.3e-14
y2=0.8
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-7260061.4
x2=2.408058e+08
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
rawfile=$netlist_dir/Gilbert_cell_hierarchal_sim.raw
sim_type=sp
autoload=1}
P 4 5 860 -1230 1000 -1230 1000 -1120 860 -1120 860 -1230 {}
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
       = 10.7 MHz} 2580 -1200 0 0 0.4 0.4 {}
T {Degeneration} 880 -1220 0 0 0.3 0.3 {}
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
N 670 -1350 670 -1300 {
lab=GND}
N 910 -1320 910 -1280 {
lab=#net1}
N 910 -1280 910 -1260 {
lab=#net1}
N 950 -1320 950 -1260 {
lab=#net2}
N 830 -1790 830 -1690 {
lab=V_out_p}
N 1030 -1790 1030 -1690 {
lab=V_out_n}
N 660 -1940 660 -1910 {
lab=VDD}
N 660 -1910 750 -1910 {
lab=VDD}
N 640 -1490 730 -1490 {
lab=V_LO_b}
N 640 -1540 730 -1540 {
lab=V_LO}
N 640 -1440 730 -1440 {
lab=V_RF}
N 640 -1380 730 -1380 {
lab=V_RF_b}
N 670 -1350 730 -1350 {
lab=GND}
N 1030 -1720 1160 -1720 {
lab=V_out_n}
N 830 -1760 1160 -1760 {
lab=V_out_p}
N 910 -1260 910 -1230 {
lab=#net1}
N 950 -1260 950 -1230 {
lab=#net2}
N 930 -1160 930 -1140 {
lab=VDD}
N 900 -1180 900 -1120 {
lab=#net1}
N 960 -1180 960 -1130 {
lab=#net2}
N 900 -1230 900 -1180 {
lab=#net1}
N 900 -1230 910 -1230 {
lab=#net1}
N 960 -1230 960 -1180 {
lab=#net2}
N 950 -1230 960 -1230 {
lab=#net2}
N 960 -1130 960 -1120 {
lab=#net2}
N 1470 -1850 1540 -1850 {
lab=V_out_p}
N 1470 -1630 1530 -1630 {
lab=V_out_n}
N 1160 -1630 1270 -1630 {
lab=V_out_n}
N 1160 -1720 1160 -1630 {
lab=V_out_n}
N 1160 -1850 1270 -1850 {
lab=V_out_p}
N 1160 -1850 1160 -1760 {
lab=V_out_p}
N 1270 -1850 1470 -1850 {
lab=V_out_p}
N 820 -930 820 -870 {
lab=#net3}
N 820 -930 900 -930 {
lab=#net3}
N 1060 -930 1060 -870 {
lab=#net4}
N 960 -930 1060 -930 {
lab=#net4}
N 1300 -920 1300 -870 {
lab=GND}
N 1300 -920 1330 -920 {
lab=GND}
N 1270 -1630 1470 -1630 {
lab=V_out_n}
N 370 -830 400 -830 {
lab=VDD}
N 370 -860 370 -830 {
lab=VDD}
N 370 -570 400 -570 {
lab=GND}
N 370 -570 370 -540 {
lab=GND}
N 900 -1120 900 -1020 {
lab=#net1}
N 960 -1120 960 -1020 {
lab=#net2}
N 300 -670 300 -650 {
lab=#net5}
N 300 -670 400 -670 {
lab=#net5}
N 300 -570 370 -570 {
lab=GND}
N 300 -590 300 -570 {
lab=GND}
N 900 -960 900 -930 {
lab=#net3}
N 960 -960 960 -930 {
lab=#net4}
C {code.sym} 50 -190 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::PROJECT_ROOT/src/Chipathon2025_pads/xschem/gf180mcu_fd_io.spice
.include $::PROJECT_ROOT/src/Chipathon2025_pads/xschem/gf180mcu_fd_io__asig_5p0_extracted.spice
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/sm141064.ngspice mimcap_typical
.lib $::180MCU_MODELS/sm141064.ngspice cap_mim
.lib $::180MCU_MODELS/sm141064.ngspice res_typical
.lib $::180MCU_MODELS/sm141064.ngspice diode_typical
.lib $::180MCU_MODELS/sm141064.ngspice bjt_typical
.lib $::180MCU_MODELS/sm141064.ngspice moscap_typical
.lib $::180MCU_MODELS/sm141064.ngspice mimcap_typical
"
}
C {code.sym} 2710 -2400 0 0 {name=SPICE only_toplevel=true 
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
    alter @V_LO[sin] = [ $cm_lo $amp_lo $freq_lo 0 ]
    alter @V_LO_b[sin] = [ $cm_lo $amp_lo $freq_lo 0 0 180 ]
    alter @V_RF[sin] = [ $cm_rf $amp_rf $freq_rf 0 ]
    alter @V_RF_b[sin] = [ $cm_rf $amp_rf $freq_rf 0 0 180 ]

    save all
    
    * operating point
    op
    * show

    write Gilbert_cell_hierarchal_sim.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 3p 0.5u
    write Gilbert_cell_hierarchal_sim.raw

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
    let bandwidth = 15e6
    let bin_width = floor(bandwidth/freq_res + 0.5)
    print bin_width

   
    * Find center bins for RF and IF frequencies
    let rf_center_bin = floor( $freq_rf/freq_res + 0.5 )
    let if_center_bin = floor( freq_if/freq_res + 0.5 )
    print freq_if
    print freq_res
    print abs(v_out_diff[if_center_bin])
    print abs(v_out_diff[if_center_bin-1])
    print abs(v_out_diff[if_center_bin+1])



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
            print bin_freq
            print abs(v_out_diff[j])
            let if_power_total = if_power_total + abs(v_out_diff[j])^2
        end
        let j = j + 1
    end

    print if_power_total
    print rf_power_total

    let conversion_gain_db = 10*log10(if_power_total/rf_power_total)
    print conversion_gain_db

    write Gilbert_cell_hierarchal_sim.raw

.endc
"}
C {devices/launcher.sym} 1830 -720 2 1 {name=h2
descr="Run ngSpice simulation (ctrl+left-click)" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 1830 -680 0 0 {name=h1
descr="Load ngSpice waveforms (ctrl+left-click)" 
tclcommand="xschem raw_read $netlist_dir/Gilbert_cell_hierarchal_sim.raw tran"
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
C {ipin.sym} 640 -1540 2 1 {name=p1 lab=V_LO}
C {ipin.sym} 640 -1490 2 1 {name=p2 lab=V_LO_b
}
C {ipin.sym} 640 -1440 0 0 {name=p3 lab=V_RF}
C {ipin.sym} 640 -1380 2 1 {name=p4 lab=V_RF_b
}
C {opin.sym} 1540 -1850 0 0 {name=p5 lab=V_out_p}
C {opin.sym} 1530 -1630 0 0 {name=p7 lab=V_out_n}
C {isource.sym} 300 -620 0 0 {name=I0 value=10u}
C {gnd.sym} 670 -1300 0 0 {name=l11 lab=GND}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Gilbert_cell_hierarchal_mixing_stage.sym} 930 -1490 0 0 {name=x1}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Gilbert_cell_hierarchal_loading_stage.sym} 930 -1840 0 0 {name=x2}
C {vdd.sym} 660 -1940 0 0 {name=l5 lab=VDD}
C {lab_pin.sym} 930 -1140 3 0 {name=p15 sig_type=std_logic lab=VDD}
C {symbols/pplus_u.sym} 930 -1180 1 1 {name=R_load_3
W=0.5e-6
L=5e-6
model=pplus_u
spiceprefix=X
m=1
hide_texts=true}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Biasing_network_with_local_mirros.sym} 660 -660 0 0 {name=x3}
C {gnd.sym} 1330 -920 0 0 {name=l10 lab=GND}
C {vdd.sym} 370 -860 0 0 {name=l12 lab=VDD}
C {gnd.sym} 370 -540 0 0 {name=l13 lab=GND}
C {ammeter.sym} 900 -990 0 0 {name=Vmeas savecurrent=true spice_ignore=0}
C {ammeter.sym} 960 -990 0 0 {name=Vmeas1 savecurrent=true spice_ignore=0}
