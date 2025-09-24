v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 2470 -760 3270 -360 {flags=graph,unlocked
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
color="4 8 16"
node="v_out
\\"diff_output; v_out_p v_out_n -\\"
v_out_p"

sim_type=tran
autoload=1
rawfile=$netlist_dir/Gilbert_cell_hierarchal_sim.raw}
B 2 2470 -1210 3270 -810 {flags=graph,unlocked
y1=7.4e-15
y2=0.8
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-19663354
x2=2.2840251e+08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="v_rf_diff
v_out
v_lo_diff"
color="4 6 8"
dataset=-1
unitx=1
logx=0
logy=0
rawfile=$netlist_dir/Gilbert_cell_hierarchal_sim.raw
sim_type=sp
autoload=1}
P 4 5 1340 -1230 1480 -1230 1480 -1120 1340 -1120 1340 -1230 {}
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
       = 10.7 MHz} 3060 -1200 0 0 0.4 0.4 {}
T {Degeneration} 1360 -1220 0 0 0.3 0.3 {}
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
N 1150 -1350 1150 -1300 {
lab=GND}
N 1390 -1320 1390 -1280 {
lab=#net1}
N 1390 -1280 1390 -1260 {
lab=#net1}
N 1430 -1320 1430 -1260 {
lab=#net2}
N 1310 -1790 1310 -1690 {
lab=V_out_p}
N 1510 -1790 1510 -1690 {
lab=V_out_n}
N 1140 -1940 1140 -1910 {
lab=VDD}
N 1140 -1910 1230 -1910 {
lab=VDD}
N 1120 -1490 1210 -1490 {
lab=#net3}
N 1120 -1540 1210 -1540 {
lab=#net4}
N 1120 -1440 1210 -1440 {
lab=#net5}
N 1120 -1380 1210 -1380 {
lab=#net6}
N 1150 -1350 1210 -1350 {
lab=GND}
N 1390 -1260 1390 -1230 {
lab=#net1}
N 1430 -1260 1430 -1230 {
lab=#net2}
N 1410 -1160 1410 -1140 {
lab=VDD}
N 1380 -1180 1380 -1120 {
lab=#net1}
N 1440 -1180 1440 -1130 {
lab=#net2}
N 1380 -1230 1380 -1180 {
lab=#net1}
N 1380 -1230 1390 -1230 {
lab=#net1}
N 1440 -1230 1440 -1180 {
lab=#net2}
N 1430 -1230 1440 -1230 {
lab=#net2}
N 1440 -1130 1440 -1120 {
lab=#net2}
N 1300 -930 1300 -870 {
lab=#net7}
N 1300 -930 1380 -930 {
lab=#net7}
N 1540 -930 1540 -870 {
lab=#net8}
N 1440 -930 1540 -930 {
lab=#net8}
N 1780 -920 1780 -870 {
lab=#net9}
N 1780 -920 1810 -920 {
lab=#net9}
N 850 -830 880 -830 {
lab=VDD}
N 850 -860 850 -830 {
lab=VDD}
N 850 -570 880 -570 {
lab=GND}
N 850 -570 850 -540 {
lab=GND}
N 1380 -1120 1380 -1020 {
lab=#net1}
N 1440 -1120 1440 -1020 {
lab=#net2}
N 780 -670 880 -670 {
lab=#net10}
N 780 -570 850 -570 {
lab=GND}
N 1380 -960 1380 -930 {
lab=#net7}
N 1440 -960 1440 -930 {
lab=#net8}
N 580 -560 580 -530 {
lab=GND}
N 580 -670 580 -620 {
lab=#net11}
N 700 -600 700 -570 {
lab=GND}
N 700 -570 780 -570 {
lab=GND}
N 700 -610 700 -600 {
lab=GND}
N 610 -1680 640 -1680 {
lab=V_LO}
N 610 -1510 640 -1510 {
lab=V_LO_b}
N 610 -1320 640 -1320 {
lab=V_RF}
N 610 -1140 640 -1140 {
lab=V_RF_b}
N 1120 -1680 1120 -1540 {
lab=#net4}
N 840 -1680 1120 -1680 {
lab=#net4}
N 840 -1510 1120 -1510 {
lab=#net3}
N 1120 -1510 1120 -1490 {
lab=#net3}
N 840 -1320 1080 -1320 {
lab=#net5}
N 1080 -1440 1080 -1320 {
lab=#net5}
N 1080 -1440 1120 -1440 {
lab=#net5}
N 840 -1140 1110 -1140 {
lab=#net6}
N 1110 -1380 1110 -1140 {
lab=#net6}
N 1110 -1380 1120 -1380 {
lab=#net6}
N 700 -740 700 -730 {
lab=VDD}
N 760 -1210 760 -1200 {
lab=VDD}
N 760 -1390 760 -1380 {
lab=VDD}
N 760 -1580 760 -1570 {
lab=VDD}
N 760 -1750 760 -1740 {
lab=VDD}
N 760 -1080 760 -1070 {
lab=GND}
N 760 -1260 760 -1250 {
lab=GND}
N 760 -1450 760 -1440 {
lab=GND}
N 760 -1620 760 -1610 {
lab=GND}
N 2480 -1620 2520 -1620 {
lab=V_out}
N 1920 -1660 1920 -1580 {
lab=#net12}
N 1520 -1720 1640 -1720 {
lab=V_out_n}
N 1520 -1760 1640 -1760 {
lab=V_out_p}
N 1850 -1870 1850 -1850 {
lab=VDD}
N 1850 -1620 1850 -1600 {
lab=GND}
N 1640 -1720 1800 -1720 {
lab=V_out_n}
N 1640 -1760 1780 -1760 {
lab=V_out_p}
N 1920 -1580 1920 -1360 {
lab=#net12}
N 1920 -1300 1920 -920 {
lab=#net9}
N 1510 -1720 1520 -1720 {
lab=V_out_n}
N 1310 -1760 1520 -1760 {
lab=V_out_p}
N 1780 -1760 1800 -1760 {
lab=V_out_p}
N 1810 -920 1920 -920 {
lab=#net9}
N 2160 -1740 2200 -1740 {
lab=#net13}
N 2020 -1740 2160 -1740 {
lab=#net13}
N 2170 -1800 2170 -1780 {
lab=VDD}
N 2170 -1780 2200 -1780 {
lab=VDD}
N 2390 -1660 2390 -1250 {
lab=V_out}
N 2290 -1660 2290 -1250 {
lab=V_out}
N 2390 -1620 2480 -1620 {
lab=V_out}
N 2020 -1200 2020 -870 {
lab=V_out}
N 2390 -1250 2390 -1200 {
lab=V_out}
N 2020 -1200 2390 -1200 {
lab=V_out}
N 2290 -1250 2290 -1200 {
lab=V_out}
N 2160 -1690 2200 -1690 {
lab=GND}
N 2160 -1690 2160 -1670 {
lab=GND}
C {code.sym} 50 -190 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::PROJECT_ROOT/src/design_padring/Chipathon2025_pads/xschem/gf180mcu_fd_io.spice
.include $::PROJECT_ROOT/src/design_padring/Chipathon2025_pads/xschem/gf180mcu_fd_io__asig_5p0_extracted.spice
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

    write Gilbert_cell_hierarchal_with_pads_sim.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 3p 0.5u
    write Gilbert_cell_hierarchal_with_pads_sim.raw

    * Calculate differential output for conversion gain measurement
    let v_out_diff = v(v_out_p)-v(v_out_n)
    let v_rf_diff = v(v_rf)-v(v_rf_b)
    let v_lo_diff = v(v_lo)-v(v_lo_b)

    
    * Extract IF component at 100MHz using FFT
    linearize v_out_diff v_rf_diff v_lo_diff v_out
    let time_step = 1e-12
    let sample_freq = 1/time_step
    let npts = length(v_out_diff)
    let freq_res = sample_freq/npts
    

    fft v_out_diff v_rf_diff v_lo_diff v_out

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

    write Gilbert_cell_hierarchal_with_pads_sim.raw

.endc
"}
C {devices/launcher.sym} 2520 -280 2 1 {name=h2
descr="Run ngSpice simulation (ctrl+left-click)" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 2520 -240 0 0 {name=h1
descr="Load ngSpice waveforms (ctrl+left-click)" 
tclcommand="xschem raw_read $netlist_dir/Gilbert_cell_hierarchal_with_pads_sim.raw tran"
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
C {ipin.sym} 610 -1680 2 1 {name=p1 lab=V_LO}
C {ipin.sym} 610 -1510 2 1 {name=p2 lab=V_LO_b
}
C {ipin.sym} 610 -1320 0 0 {name=p3 lab=V_RF}
C {ipin.sym} 610 -1140 2 1 {name=p4 lab=V_RF_b
}
C {isource.sym} 580 -590 0 0 {name=I0 value=10u}
C {gnd.sym} 1150 -1300 0 0 {name=l11 lab=GND}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Gilbert_cell_hierarchal_mixing_stage.sym} 1410 -1490 0 0 {name=x1}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Gilbert_cell_hierarchal_loading_stage.sym} 1410 -1840 0 0 {name=x2}
C {vdd.sym} 1140 -1940 0 0 {name=l5 lab=VDD}
C {lab_pin.sym} 1410 -1140 3 0 {name=p15 sig_type=std_logic lab=VDD}
C {symbols/pplus_u.sym} 1410 -1180 1 1 {name=R_load_3
W=0.5e-6
L=5e-6
model=pplus_u
spiceprefix=X
m=1
hide_texts=true}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Biasing_network_with_local_mirros.sym} 1140 -660 0 0 {name=x3}
C {vdd.sym} 850 -860 0 0 {name=l12 lab=VDD}
C {gnd.sym} 580 -530 0 0 {name=l13 lab=GND}
C {ammeter.sym} 1380 -990 0 0 {name=Vmeas savecurrent=true spice_ignore=0}
C {ammeter.sym} 1440 -990 0 0 {name=Vmeas1 savecurrent=true spice_ignore=0}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_padring/Chipathon2025_pads/xschem/symbols/io_secondary_5p0/io_secondary_5p0.sym} 840 -1600 0 1 {name=IO1
spiceprefix=X
}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_padring/Chipathon2025_pads/xschem/symbols/io_secondary_5p0/io_secondary_5p0.sym} 780 -590 0 1 {name=IO2
spiceprefix=X
}
C {gnd.sym} 850 -540 0 0 {name=l6 lab=GND}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_padring/Chipathon2025_pads/xschem/symbols/io_secondary_5p0/io_secondary_5p0.sym} 840 -1430 0 1 {name=IO3
spiceprefix=X
}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_padring/Chipathon2025_pads/xschem/symbols/io_secondary_5p0/io_secondary_5p0.sym} 840 -1240 0 1 {name=IO4
spiceprefix=X
}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_padring/Chipathon2025_pads/xschem/symbols/io_secondary_5p0/io_secondary_5p0.sym} 840 -1060 0 1 {name=IO5
spiceprefix=X
}
C {lab_pin.sym} 700 -740 0 0 {name=p6 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 760 -1210 0 0 {name=p12 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 760 -1390 0 0 {name=p13 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 760 -1580 0 0 {name=p14 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 760 -1750 0 0 {name=p16 sig_type=std_logic lab=VDD}
C {gnd.sym} 760 -1070 0 0 {name=l14 lab=GND}
C {gnd.sym} 760 -1250 0 0 {name=l15 lab=GND}
C {gnd.sym} 760 -1440 0 0 {name=l16 lab=GND}
C {gnd.sym} 760 -1610 0 0 {name=l17 lab=GND}
C {opin.sym} 2520 -1620 0 0 {name=p5 lab=V_out}
C {lab_pin.sym} 1570 -1760 1 0 {name=p7 sig_type=std_logic lab=V_out_p}
C {lab_pin.sym} 1570 -1720 3 0 {name=p17 sig_type=std_logic lab=V_out_n}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/5T-OTA-buffer_no_hierarchy.sym} 1920 -1740 0 0 {name=x_Amplifier}
C {vdd.sym} 1850 -1870 0 0 {name=l18 lab=VDD}
C {gnd.sym} 1850 -1600 0 0 {name=l19 lab=GND}
C {ammeter.sym} 1920 -1330 0 0 {name=Vmeas2 savecurrent=true spice_ignore=0}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Output_stage.sym} 2330 -1720 0 0 {name=x4}
C {vdd.sym} 2170 -1800 0 0 {name=l10 lab=VDD}
C {gnd.sym} 2160 -1680 0 0 {name=l20 lab=GND}
