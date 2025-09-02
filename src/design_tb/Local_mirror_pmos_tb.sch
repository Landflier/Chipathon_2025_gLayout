v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 1270 -1430 2070 -1030 {flags=graph,unlocked
y1=1e-05
y2=1.1e-05
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-5e-10
x2=9.5e-09
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

sim_type=tran
autoload=1}
T {Desription

NMOS current mirror, meant to provide local 
biasing for each of the circuits in the
top-level

NMOS should be operating in gm/ID = 
} 2880 -2390 0 0 0.4 0.4 {}
N 810 -830 810 -790 {
lab=GND}
N 160 -2080 160 -2040 {
lab=GND}
N 160 -2170 160 -2140 {
lab=VDD}
N 630 -1170 630 -1120 {
lab=VDD}
N 920 -770 920 -690 {
lab=GND}
N 810 -930 810 -920 {
lab=#net1}
N 810 -860 810 -830 {
lab=GND}
N 810 -960 810 -930 {
lab=#net1}
N 920 -960 920 -940 {
lab=#net2}
N 920 -880 920 -830 {
lab=#net3}
N 630 -1120 680 -1120 {
lab=VDD}
C {code.sym} 50 -190 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/sm141064.ngspice mimcap_typical
.lib $::180MCU_MODELS/sm141064.ngspice cap_mim
.lib $::180MCU_MODELS/sm141064.ngspice res_typical
.lib $::180MCU_MODELS/sm141064.ngspice diode_typical
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

    write Local_mirror_pmos_tb.raw

    set appendwrite

    * Transient analysis to observe mixing operation
    tran 1n 0.01u
    write Local_mirror_pmos_tb.raw

.endc
"}
C {devices/launcher.sym} 1317.5 -962.5 2 1 {name=h2
descr="Run ngSpice simulation (ctrl+left-click)" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 1320 -910 0 0 {name=h1
descr="Load ngSpice waveforms (ctrl+left-click)" 
tclcommand="xschem raw_read $netlist_dir/Local_mirror_pmos_tb.raw tran"
}
C {title-2.sym} 0 0 0 0 {name=l9 author="Time Transcenders" lock=true rev=1.0 page=1}
C {isource.sym} 810 -890 0 1 {name=I0 value=10u}
C {gnd.sym} 810 -790 0 0 {name=l5 lab=GND}
C {vdd.sym} 160 -2170 0 0 {name=l1 lab=VDD}
C {vsource.sym} 160 -2110 0 0 {name=V1 value=3.3 savecurrent=true}
C {gnd.sym} 160 -2040 0 0 {name=l2 lab=GND}
C {ammeter.sym} 920 -910 0 1 {name=Vmeas1 savecurrent=true spice_ignore=0}
C {res.sym} 920 -800 0 0 {name=R1
value=1K
footprint=1206
device=resistor
m=1}
C {vdd.sym} 630 -1170 0 0 {name=l3 lab=VDD}
C {/home/vasil/Downloads/SSCS_PICO_2025/src/design_xsch/Local_mirror_pmos.sym} 800 -1020 0 0 {name=x1
l_ref=0.4
w_ref=2
l_mir=0.4
w_mir=6}
C {gnd.sym} 920 -690 0 0 {name=l4 lab=GND}
