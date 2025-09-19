v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {Desription

The biasing circuit for the Gilbert cell,
providing constant 50uA current at both its
outputs} 2880 -2390 0 0 0.4 0.4 {}
N 180 -1370 240 -1370 {
lab=VDD}
N 840 -1190 840 -1020 {
lab=I_out_1}
N 610 -860 640 -860 {
lab=VSS}
N 610 -1140 1400 -1140 {
lab=#net1}
N 1180 -1190 1180 -1020 {
lab=I_out_2}
N 1600 -1190 1600 -1020 {
lab=I_out_3}
N 480 -1140 610 -1140 {
lab=#net1}
N 480 -1210 480 -1140 {
lab=#net1}
N 950 -860 980 -860 {
lab=VSS}
N 1370 -860 1400 -860 {
lab=VSS}
N 640 -1140 640 -1110 {
lab=#net1}
N 640 -1050 640 -980 {
lab=#net1}
N 980 -1050 980 -980 {
lab=#net1}
N 980 -1140 980 -1110 {
lab=#net1}
N 1400 -1050 1400 -980 {
lab=#net1}
N 1400 -1140 1400 -1110 {
lab=#net1}
N 640 -1110 640 -1050 {
lab=#net1}
N 980 -1110 980 -1050 {
lab=#net1}
N 1400 -1110 1400 -1050 {
lab=#net1}
N 360 -1210 360 -1160 {
lab=I_BIAS}
N 240 -1370 280 -1370 {
lab=VDD}
C {title-2.sym} 0 0 0 0 {name=l9 author="Time Transcenders" lock=true rev=1.0 page=1}
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
    save all

    op
    show

    write Biasing_network_sim.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 1p 10n


    write Biasing_network_sim.raw

.endc
"}
C {iopin.sym} 190 -860 0 1 {name=p1 lab=VSS}
C {iopin.sym} 360 -1160 3 1 {name=p2 lab=I_BIAS}
C {opin.sym} 840 -1190 3 0 {name=p7 lab=I_out_1}
C {opin.sym} 1180 -1190 3 0 {name=p8 lab=I_out_2}
C {opin.sym} 1600 -1190 3 0 {name=p9 lab=I_out_3}
C {iopin.sym} 180 -1370 0 1 {name=p3 lab=VDD}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Local_mirror_pmos.sym} 360 -1270 0 0 {name=x_PMOS_mirror
l_ref=0.4u
w_ref=2u
l_mir=0.4u
w_mir=6u}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Local_mirror_nmos.sym} 720 -900 0 0 {name=x_NMOS_mirror_1
l_ref=1u
w_ref=1.5u
nf_ref=1
l_mir=1u
w_mir=7.5u
nf_mir=5}
C {lab_pin.sym} 610 -860 0 0 {name=p4 sig_type=std_logic lab=VSS}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Local_mirror_nmos.sym} 1060 -900 0 0 {name=x_NMOS_mirror_2
l_ref=1u
w_ref=1.5u
nf_ref=1
l_mir=1u
w_mir=7.5u
nf_mir=5}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Local_mirror_nmos.sym} 1480 -900 0 0 {name=x_NMOS_mirror_3
l_ref=1u
w_ref=1.5u
nf_ref=1
l_mir=1u
w_mir=1.5u
nf_mir=1}
C {lab_pin.sym} 950 -860 0 0 {name=p5 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1370 -860 0 0 {name=p6 sig_type=std_logic lab=VSS}
