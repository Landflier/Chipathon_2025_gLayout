v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 1300 -1450 2100 -1050 {flags=graph,unlocked
y1=4.7e-05
y2=4.8e-05
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
rawfile=$netlist_dir/Biasing_network_sim.raw
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
N 560 -1460 560 -1420 {
lab=#net1}
N 470 -1190 530 -1190 {
lab=GND}
N 470 -1190 470 -1180 {
lab=GND}
N 560 -1360 560 -1290 {
lab=#net2}
N 160 -2080 160 -2040 {
lab=GND}
N 160 -2170 160 -2140 {
lab=VDD}
N 660 -1580 660 -1530 {
lab=VDD}
N 710 -1580 710 -1520 {
lab=VDD}
N 760 -1580 760 -1520 {
lab=VDD}
N 660 -1330 660 -1290 {
lab=#net3}
N 660 -1470 660 -1390 {
lab=#net4}
N 710 -1330 710 -1290 {
lab=#net5}
N 710 -1460 710 -1390 {
lab=#net6}
N 760 -1330 760 -1290 {
lab=#net7}
N 760 -1460 760 -1390 {
lab=#net8}
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
    
    * operating point
    op
    show

    write Biasing_network_sim.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 1p 0.01u
    write Biasing_network_sim.raw

.endc
"}
C {devices/launcher.sym} 1347.5 -972.5 2 1 {name=h2
descr="Run ngSpice simulation (ctrl+left-click)" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 1350 -930 0 0 {name=h1
descr="Load ngSpice waveforms (ctrl+left-click)" 
tclcommand="xschem raw_read $netlist_dir/Biasing_network_sim.raw tran"
}
C {title-2.sym} 0 0 0 0 {name=l9 author="Time Transcenders" lock=true rev=1.0 page=1}
C {isource.sym} 560 -1390 0 0 {name=I0 value=50u}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Biasing_network_no_hierarchy.sym} 630 -1190 0 0 {name=X_biasing_cmirrors
}
C {gnd.sym} 470 -1180 0 0 {name=l5 lab=GND}
C {vdd.sym} 160 -2170 0 0 {name=l1 lab=VDD}
C {vsource.sym} 160 -2110 0 0 {name=V1 value=3.3 savecurrent=false}
C {gnd.sym} 160 -2040 0 0 {name=l2 lab=GND}
C {ammeter.sym} 660 -1360 0 1 {name=Vmeas1 savecurrent=true spice_ignore=0}
C {ammeter.sym} 710 -1360 0 0 {name=Vmeas2 savecurrent=true spice_ignore=0}
C {ammeter.sym} 760 -1360 0 0 {name=Vmeas3 savecurrent=true spice_ignore=0}
C {res.sym} 660 -1500 0 0 {name=R1
value=10K
footprint=1206
device=resistor
m=1}
C {res.sym} 710 -1490 0 0 {name=R2
value=10K
footprint=1206
device=resistor
m=1}
C {res.sym} 760 -1490 0 0 {name=R3
value=100K
footprint=1206
device=resistor
m=1}
C {vdd.sym} 660 -1580 0 0 {name=l3 lab=VDD}
C {vdd.sym} 710 -1580 0 0 {name=l4 lab=VDD}
C {vdd.sym} 760 -1580 0 0 {name=l6 lab=VDD}
