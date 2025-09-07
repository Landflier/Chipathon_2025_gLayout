v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 1950 -1450 2750 -1050 {flags=graph,unlocked
y1=1.1e-05
y2=6.1e-05
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


dataset=-1
unitx=1
logx=0
logy=0
rainbow=1
color="4 4 4"
node="i(vmeas3)
i(vmeas2)
i(vmeas1)"
rawfile=$netlist_dir/Local_mirror_biasing_tb.raw
sim_type=tran
autoload=1}
T {Desription

Simple 3 current mirrors, biased from the same
tranistor. The circuit should get a current
biasing from outside the chip ~ 100 uA, and
provide biasing of 50uA at I_out_1 and I_out_2,
and a bias of some current at I_out_3. 

I_out_1, I_out_2 -> biasing the diff pair in 
the Gilbert mixer

I_out_3 -> biasing the 5T-OTA
} 2880 -2390 0 0 0.4 0.4 {}
N 370 -910 430 -910 {
lab=GND}
N 370 -910 370 -900 {
lab=GND}
N 160 -2080 160 -2040 {
lab=GND}
N 160 -2170 160 -2140 {
lab=VDD}
N 850 -1420 850 -1390 {
lab=VDD}
N 1090 -1420 1090 -1390 {
lab=VDD}
N 1330 -1420 1330 -1390 {
lab=VDD}
N 850 -1240 850 -1210 {
lab=#net1}
N 850 -1330 850 -1300 {
lab=#net2}
N 1090 -1240 1090 -1210 {
lab=#net3}
N 1090 -1330 1090 -1300 {
lab=#net4}
N 1330 -1240 1330 -1210 {
lab=#net5}
N 1330 -1330 1330 -1300 {
lab=#net6}
N 370 -1010 430 -1010 {
lab=#net7}
N 370 -1170 430 -1170 {
lab=VDD}
N 370 -1180 370 -1170 {
lab=VDD}
N 370 -1010 370 -1000 {
lab=#net7}
N 370 -940 370 -910 {
lab=GND}
C {code.sym} 50 -190 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
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
C {code.sym} 2705 -2395 0 0 {name=SPICE only_toplevel=true 
value="
* Add convergence aids
.option method=gear

.control
    
    * operating point
    op
    show

    write Local_mirror_biasing_tb.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 1n 0.01u
    write Local_mirror_biasing_tb.raw

.endc
"}
C {devices/launcher.sym} 1997.5 -982.5 2 1 {name=h2
descr="Run ngSpice simulation (ctrl+left-click)" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 2000 -930 0 0 {name=h1
descr="Load ngSpice waveforms (ctrl+left-click)" 
tclcommand="xschem raw_read $netlist_dir/Local_mirror_biasing_tb.raw tran"
}
C {title-2.sym} 0 0 0 0 {name=l9 author="Time Transcenders" lock=true rev=1.0 page=1}
C {isource.sym} 370 -970 0 1 {name=I0 value=10u}
C {gnd.sym} 370 -900 0 0 {name=l5 lab=GND}
C {vdd.sym} 160 -2170 0 0 {name=l1 lab=VDD}
C {vsource.sym} 160 -2110 0 0 {name=V1 value=3.3 savecurrent=false}
C {gnd.sym} 160 -2040 0 0 {name=l2 lab=GND}
C {ammeter.sym} 850 -1270 0 1 {name=Vmeas1 savecurrent=true spice_ignore=0}
C {ammeter.sym} 1090 -1270 0 0 {name=Vmeas2 savecurrent=true spice_ignore=0}
C {ammeter.sym} 1330 -1270 0 0 {name=Vmeas3 savecurrent=true spice_ignore=0}
C {res.sym} 850 -1360 0 0 {name=R1
value=1K
footprint=1206
device=resistor
m=1}
C {res.sym} 1090 -1360 0 0 {name=R2
value=1K
footprint=1206
device=resistor
m=1}
C {res.sym} 1330 -1360 0 0 {name=R3
value=1K
footprint=1206
device=resistor
m=1}
C {vdd.sym} 850 -1420 0 0 {name=l3 lab=VDD}
C {vdd.sym} 1090 -1420 0 0 {name=l4 lab=VDD}
C {vdd.sym} 1330 -1420 0 0 {name=l6 lab=VDD}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Biasing_network_with_local_mirros.sym} 690 -1000 0 0 {name=x1}
C {vdd.sym} 370 -1180 0 0 {name=l7 lab=VDD}
