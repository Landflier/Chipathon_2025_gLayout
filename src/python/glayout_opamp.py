#!/usr/bin/env python
# coding: utf-8

# # GLayout: PDK-Agnostic P-Cell Based Chip Layout Generation With Reinforcement Learning Optimization
# 

# <a href="https://colab.research.google.com/github/idea-fasoc/OpenFASOC/blob/main/docs/source/notebooks/glayout/glayout_opamp.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# ```
# OpenFASOC Team, November 2023
# SPDX-License-Identifier: Apache-2.0
# ```

# 
# |Name|Affiliation| IEEE Member | SSCS Member |
# |:-----------------:|:----------:|:----------:|:----------:|
# | Harsh Khandeparkar| University of Michigan + Indian Institute of Technology Kharagpur               | No  | No  |
# | Anhang Li         | University of Michigan | Yes | No  |
# | Ali Hammoud       | University of Michigan | Yes | No  |
# | Ayushman Tripathi | University of Michigan | No  | No  |
# | Wen Tian          | University of Michigan | Yes | No  |
# | Mehdi Saligane (Advisor)    | University of Michigan | Yes | Yes |
# 

# # Introduction
# Welcome!
# This notebook serves as an introduction to the GDSFactory-based layout automation tool **GLayout** and an example two-stage Operational Amplifier (Op-Amp) generator, as a part of [OpenFASoC](https://github.com/idea-fasoc/OpenFASOC).  
# 
# This Notebook will run as-is on Google Collab, or you can run locally by using the install steps in [this document](https://docs.google.com/document/d/e/2PACX-1vRL8ksIvB-fHaqWgkgBPDUznOcDmmFhNrvzPNx9GSSkZyfhJYexEI9gBZCJ0SNNnHdUrAf1EBOeU182/pub). If you choose a local install, skip part 1 of this notebook.
# 
# ## GDSFactory
# [GDSFactory](https://gdsfactory.github.io/gdsfactory/index.html) is a Python library for designing integrated circuit layouts in Python and save it directly in the [GDSII](https://en.wikipedia.org/wiki/GDSII) format, and run DRC (Design Rule Checking) and LVS (Layout v/s Schematic) verification, or simulation.
# 
# ## GLayout
# [GLayout](https://github.com/idea-fasoc/OpenFASOC/blob/main/openfasoc/generators/gdsfactory-gen/glayout/) is a layout automation python package which generates _DRC clean_ circuit layouts and SPICE netlists for any PDK (Process Design Kit). It is composed of two main parts: the _generic PDK framework_, and the _circuit generators_.
# 
# The generic PDK framework allows for describing any PDK in a standardized format, defined by the `MappedPDK` class. The generators are Python functions that take as arguments a `MappedPDK` object, and a set of optional layout parameters to produce a DRC (Design Rule Checking) clean layout of a particular circuit design and the pre-PEX (Parasitic Extraction) SPICE netlist, for LVS (Layout v/s Extraction).
# 
# The post-PEX netlist can be used for simulating a circuit. The simulation and performance evaluation of multiple design variations can be parallelized on a cloud platform for fast design space exploration. Fig. 1 describes the GLayout workflow.
# 
# ![workflow](https://i.imgur.com/BA7gY81.png)
# 
# (Fig. 1: GLayout Workflow)
# 
# ### Generators
# Generators in GLayout are Python functions that generate the layout and SPICE netlist for a circuit component. This allows for describing hierarchical and parameterized circuits, or PCells (Parameterized Cells), in Python.
# 
# A generator can be a utility generator such as a Via, a primitive PCell such as a MOSFET, or a complex circuit as an Op-Amp.
# 
# Generators are PDK-agnostic and hierarchical, and may call other generators. This allows complex components to be composed of simpler components hierarchically. Fig. 2 shows the hierarchical usage of generators in an example Op-Amp design, and Fig. 3 shows the creation of a high-level PCell from a primitive PCell.
# 
# The SPICE netlist for a component is also generated hierarchically along with the layout.
# 
# ![hierarchy](https://i.imgur.com/YC4CXrp.png)
# 
# (Fig. 2: Hierarchy of PCells in the Example Op-Amp Design)
# 
# ![high level pcell construction](https://i.imgur.com/KSgSHla.png)
# 
# (Fig. 3: Creation of High-Level PCells from Primitive PCells)
# 
# #### List of Generators
# ##### Utility Generators
# - Via
# - Guardring
# - Routing (Straight, L, and C)
# 
# ##### PCell Generators
# - Primitive Cells
#   - FET (NMOS, PMOS)
#   - MIM Capacitor
# - Intermediate PCells
#   - Differential Pair
#   - Current Mirror
#   - Differential to Single Ended Converter
# 
# ##### Example Designs
# - Two Stage Operational Amplifier

# # Using GLayout
# ### 1. Clone the repository and install dependencies
# #### Python Dependencies
# * [`gdsfactory`](https://github.com/gdsfactory/gdsfactory): Provides the backend for GDS manipulation.
# * [`sky130`](https://github.com/gdsfactory/skywater130): The Skywater 130nm PDK Python package for GDSFactory to use in this demo.
# * [`gf180`](https://github.com/gdsfactory/gf180): The GF 180nm PDK Python package for GDSFactory to use in this demo.
# * [`gdstk`](https://heitzmann.github.io/gdstk/): (installed as a part of gdsfactory) Used for converting GDS files into SVG images for viewing.
# * [`svgutils`](https://svgutils.readthedocs.io/en/latest/): To scale the SVG image.
# 
# #### System Dependencies
# * [`klayout`](https://klayout.de/): For DRC (Design Rule Checking).
# 

# In[ ]:


# Clone OpenFASoC
get_ipython().system('git clone https://github.com/idea-fasoc/OpenFASOC')
# Install python dependencies
get_ipython().system('pip install sky130')
get_ipython().system('pip install gf180 prettyprinttree svgutils')
get_ipython().system('pip install gdsfactory==7.7.0')

import pathlib
import os
# Install KLayout (via conda)
get_ipython().system('curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba')
conda_prefix_path = pathlib.Path('conda-env')
CONDA_PREFIX = str(conda_prefix_path.resolve())
get_ipython().run_line_magic('env', 'CONDA_PREFIX={CONDA_PREFIX}')

get_ipython().system('bin/micromamba create --yes --prefix $CONDA_PREFIX')
# Install from the litex-hub channel
get_ipython().system('bin/micromamba install --yes --prefix $CONDA_PREFIX                          --channel litex-hub                          --channel main                          klayout')

# Add conda packages to the PATH
PATH = os.environ['PATH']
get_ipython().run_line_magic('env', 'PATH={PATH}:{CONDA_PREFIX}/bin')

get_ipython().run_line_magic('cd', '/content/OpenFASOC/openfasoc/generators/glayout')


# ### 2. Basic Usage of the GLayout Framework
# Each generator is a Python function that takes a `MappedPDK` object as a parameter and generates a DRC clean layout for the given PDK. The generator may also accept a set of optional layout parameters such as the width or length of a MOSFET. All parameters are normal Python function arguments.
# 
# The generator returns a `GDSFactory.Component` object that can be written to a `.gds` file and viewed using a tool such as Klayout. In this example, the `gdstk` library is used to convert the `.gds` file to an SVG image for viewing.
# 
# The pre-PEX SPICE netlist for the component can be viewed using `component.info['netlist'].generate_netlist()`.
# 
# In the following example the FET generator `glayout.primitives.fet` is imported and run with both the [Skywater 130](https://skywater-pdk.readthedocs.io/en/main/) and [GF180](https://gf180mcu-pdk.readthedocs.io/en/latest/) PDKs.

# #### Demonstration of Basic Layout / Netlist Generation in SKY130 & GF180

# In[ ]:


from glayout.flow.primitives.fet import nmos
from glayout.flow.pdk.sky130_mapped import sky130_mapped_pdk as sky130
from glayout.flow.pdk.gf180_mapped import gf180_mapped_pdk as gf180
import gdstk
import svgutils.transform as sg
import IPython.display
from IPython.display import clear_output
import ipywidgets as widgets

# Used to display the results in a grid (notebook only)
left = widgets.Output()
leftSPICE = widgets.Output()
right = widgets.Output()
rightSPICE = widgets.Output()
hide = widgets.Output()

grid = widgets.GridspecLayout(1, 4)
grid[0, 0] = left
grid[0, 1] = leftSPICE
grid[0, 2] = right
grid[0, 3] = rightSPICE
display(grid)

def display_gds(gds_file, scale = 3):
  # Generate an SVG image
  top_level_cell = gdstk.read_gds(gds_file).top_level()[0]
  top_level_cell.write_svg('out.svg')

  # Scale the image for displaying
  fig = sg.fromfile('out.svg')
  fig.set_size((str(float(fig.width) * scale), str(float(fig.height) * scale)))
  fig.save('out.svg')

  # Display the image
  IPython.display.display(IPython.display.SVG('out.svg'))

def display_component(component, scale = 3):
  # Save to a GDS file
  with hide:
    component.write_gds("out.gds")

  display_gds('out.gds', scale)

with hide:
  # Generate the sky130 component
  component_sky130 = nmos(pdk = sky130, fingers=5)
  # Generate the gf180 component
  component_gf180 = nmos(pdk = gf180, fingers=5)

# Display the components' GDS and SPICE netlists
with left:
  print('Skywater 130nm N-MOSFET (fingers = 5)')
  display_component(component_sky130, scale=2.5)
with leftSPICE:
  print('Skywater 130nm SPICE Netlist')
  print(component_sky130.info['netlist'].generate_netlist())

with right:
  print('GF 180nm N-MOSFET (fingers = 5)')
  display_component(component_gf180, scale=2)
with rightSPICE:
  print('GF 180nm SPICE Netlist')
  print(component_gf180.info['netlist'].generate_netlist())


# #### Interactive Primitive Generation in SKY130
# The following cell demonstrates the different PCell and Utility generators on the Sky130 PDK.

# In[ ]:


from glayout.flow.primitives import fet, mimcap, guardring
from glayout.flow.blocks import diff_pair
import ipywidgets as widgets

selection_button = widgets.RadioButtons(
  options=['NMOS', 'PMOS', 'MIM Capacitor', 'Differential Pair', 'Guardring'],
  orientation='horizontal',
  description='Generator:',
  layout=widgets.Layout(position='right')
)
generate_button = widgets.Button(description='Generate', disabled=False)
output = widgets.Output(layout = widgets.Layout(position='left', overflow='visible'))
hide = widgets.Output()

grid = widgets.GridspecLayout(1, 2)
grid[0, 0] = widgets.VBox([selection_button, generate_button])
grid[0, 1] = output

display(grid)

with hide:
  component = fet.nmos(pdk = sky130)
with output:
  print('NMOS')
  display_component(component)

def generate_component(_):
  selected_comp = selection_button.value

  with output:
    clear_output()
    print(f"Generating {selected_comp}...")
  with hide:
    match selected_comp:
      case 'NMOS':
        component = fet.nmos(pdk = sky130)
      case 'PMOS':
        component = fet.pmos(pdk = sky130)
      case 'MIM Capacitor':
        component = mimcap.mimcap(pdk = sky130)
      case 'Differential Pair':
        component = diff_pair.diff_pair(pdk = sky130)
      case 'Guardring':
        component = guardring.tapring(pdk = sky130)
  with output:
    clear_output()
    print(selected_comp)
    display_component(component, 3)

generate_button.on_click(generate_component)


# ### 3. Tweak the Parameters
# These are some of the parameters the NMOS FET generator accepts:
# * `width`: The gate width of the FET.
# * `length`: The gate length of the FET.
# * `fingers`: The number of fingers. Each finger shares the same source/drain.
# * `multipliers`: Number of multipliers (a multiplier is a row of fingers).
# 
# Run the below cell and use the sliders to adjust the parameters.

# In[ ]:


# Default Values
width=3
length=0.2
fingers=4
multipliers=1

# Create sliders
width_slider = widgets.FloatSlider(description = 'Width:', min = 1, max = 5, step = 0.5, value = width)
length_slider = widgets.FloatSlider(description = 'Length:', min = 0.2, max = 1, step = 0.1, value = length)
fingers_slider = widgets.IntSlider(description = 'Fingers:', min = 1, max = 10, value = fingers)
multipliers_slider = widgets.IntSlider(description = 'Multipliers:', min = 1, max = 5, value = multipliers)
generate_button = widgets.Button(description='Generate', disabled=False)

inputs_box = widgets.VBox([width_slider, length_slider, fingers_slider, multipliers_slider, generate_button])

output = widgets.Output(layout = widgets.Layout(position='left', overflow='visible'))
hide = widgets.Output()

grid = widgets.GridspecLayout(1, 2)
grid[0, 0] = inputs_box
grid[0, 1] = output

display(grid)

def generate_component(_):
  width = width_slider.value
  length = length_slider.value
  fingers = fingers_slider.value
  multipliers = multipliers_slider.value

  with output:
    clear_output()
    print(f"Generating with width={width}, length={length}, fingers={fingers}, multipliers={multipliers}...")
  with hide:
    component = component = fet.nmos(pdk = sky130, width = width, length=length, fingers = fingers, multipliers = multipliers)
  with output:
    clear_output()
    print(f"N-MOSFET with width={width}, length={length}, fingers={fingers}, multipliers={multipliers}:")
    display_component(component)

generate_component(None)

# Regenerate upon change in value
generate_button.on_click(generate_component)


# ### 4. DRC Checking Using External Tools (KLayout)
# Design Rule Check (DRC) is the process of ensuring that a particular layout does not violate the constraints or _design rules_ imposed by the PDK.
# 
# [Klayout](https://klayout.de/) is a GDSII viewer and editor that also has a DRC feature. The design rules for the PDK, in this case the Skywater 130 PDK, are described in a `.lydrc` file.
# 
# The following cell runs DRC on the component generated in the previous cell. The number of DRC errors reported will be displayed at the end of the output.

# In[ ]:


get_ipython().system('klayout out.gds -zz -r glayout/pdk/sky130_mapped/sky130.lydrc')
get_ipython().system('echo -e "\\n$(grep -c "<value>" sky130_drc.txt) DRC Errors Found"')


# # Complex Circuit Example: Op-Amp
# Using the above generators, complex circuit designs can be created by connecting the components. The function for creating such a design would itself be a generator. For example, differential pair generator uses the FET, Via, and routing generators.
# 
# ### Design
# One such example circuit is the [Operational Amplifier](https://en.wikipedia.org/wiki/Operational_amplifier) (Op-Amp) defined in the `opamp.py` file. This design consists of a differential pair (input stage), a differential to single-ended converter (load), a common source (CS) gain stage, and an output buffer (for testing, it's not a part of the feedback loop), with an improved split-stage feedback  created using a capacitor. The differential pair and the gain and output stages are biased using current mirrors.
# 
# Each of the stages, the feedback capacitor, and the biasing circuitry were generated using the exported generators. See the schematic in Fig. 4 for an overview of the circuit. The PCells used (Differential Pair, Current Mirror, etc.) are highlighted with the dotted border.
# 
# In Fig. 5(a), a Skywater 130nm layout for the Op-Amp is shown with the different components annotated. The annotated components are marked in the circuit schematic in Fig. 5(b) for the first two stages of the Op-Amp.
# 
# ![schematic](https://i.imgur.com/PUEPdXE.png)
# 
# (Fig. 4: Example Op-Amp Circuit Schematic)
# 
# ![schemlayout](https://i.imgur.com/W2askiz.png)
# 
# (Fig. 5: (a) Sky130 Op-Amp Layout and (b) the Corresponding Circuit Schematic for the First Two Stages of the Op-Amp)
# 
# ### Parameters
# The Op-Amp generator accepts the following optional arguments:
# - `half_diffpair_params`: A tuple of (width, length, fingers) for the differential pair. (3 values)
# - `diffpair_bias`: A tuple of (width, length, fingers) for the differential pair bias transistors. (3)
# - `half_common_source_params`: A tuple of (width, length, fingers, multipliers) for the common source PMOS transistor. (4)
# - `half_common_source_bias`: A tuple of (width, length, fingers, multipliers) for the common source bias transistors. The `multipliers` only apply to the mirror transistor, reference transistor has a multiplier of 1. (4)
# - `output_stage_params`: A tuple of (width, length, fingers) for the output stage NMOS transistor. (3)
# - `output_stage_bias`: A tuple of (width, length, fingers) for the output stage bias transistors. (3)
# - `half_pload`: A tuple of (width, length, fingers) for the load (differential to single-ended converter). The `fingers` only apply to the bottom two transistors. (3)
# - `mim_cap_size`: A tuple of (width, length) for individual MIM capacitors. (2)
# - `mim_cap_rows`: The number of rows in the MIM capacitor array (columns are fixed at 2). (1)
# - `rmult`: The multiplier for the width of the routes. (1)
# 
# The above arguments account for a total of 27 individual parameter values. These parameters can be changed to generate a very wide range of Op-Amp designs.

# ### 1. Generating the Op-Amp
# The cell below generates the Op-Amp with a particular set of parameters and a PDK (Sky130 by default). Change any of the parameters or the PDK set at the beginning of the cell to generate different variations of the Op-Amp.

# In[ ]:


from glayout.flow.blocks.composite.opamp import opamp

# Select which PDK to use
pdk = sky130
# pdk = gf180

# Op-Amp Parameters
half_diffpair_params = (6, 1, 4)
diffpair_bias = (6, 2, 4)
half_common_source_params = (7, 1, 10, 3)
half_common_source_bias  = (6, 2, 8, 2)
output_stage_params = (5, 1, 16)
output_stage_bias = (6, 2, 4)
half_pload = (6, 1, 6)
mim_cap_size = (12, 12)
mim_cap_rows = 3
rmult = 2

hide = widgets.Output()

# Generate the Op-Amp
print('Generating Op-Amp...')
with hide:
  component = opamp(pdk, half_diffpair_params, diffpair_bias, half_common_source_params, half_common_source_bias, output_stage_params, output_stage_bias, half_pload,  mim_cap_size, mim_cap_rows, rmult)

# Display the Op-Amp
clear_output()
display_component(component, 0.5)


# ### 2. Sweeping Variations
# The [`sky130_nist_tapeout.py`](https://github.com/idea-fasoc/OpenFASOC/blob/main/openfasoc/generators/gdsfactory-gen/tapeout_and_RL/sky130_nist_tapeout.py) file contains utilities for generating a matrix of Op-Amps with different parameters in the Sky130 PDK, running simulations, and generating statistics. This Python file is documented [here](https://github.com/idea-fasoc/OpenFASOC/blob/main/openfasoc/generators/gdsfactory-gen/tapeout_and_RL/README.md).
# 
# In the cell below, an array of different Op-Amp parameters will be generated and a matrix of all the different variations will be created and displayed. Probe pads and "Nanofab" micropads are added for layout (See Fig. 6).
# 
# The `get_small_parameter_list()` function is used to generate a small list of parameters. The function varies 7 out of the 27 parameters possible. A value is picked from a list for each of the 7 parameters while keeping the other values constant and returns a list of all possible combinations (1700+).
# 
# The `create_opamp_matrix()` function generates Op-Amps from a given list of parameter values and appends them to a single GDS file for display. The function also adds "pads" to the Op-Amp that are used for probing on the physical layout. (See Fig. 6)
# 
# ![pads](https://i.imgur.com/5YIsYSY.png)
# 
# (Fig 6. Pads Added to the Op-Amps in the Matrix)
# 
# In test mode (default), only the first 2 Op-Amp varations will be used. Set the `TEST_MODE` variable to `False` to use all the generated variations. NOTE: This may take a very long time to run.

# In[ ]:


get_ipython().run_line_magic('cd', '/content/OpenFASOC/openfasoc/generators/glayout/tapeout/tapeout_and_RL')
from sky130_nist_tapeout import *

# Test mode. Set to False to generate 1700+ variations.
TEST_MODE = True
TEST_NUM_VARIANTS = 2 # These many variants will be generated if TEST_MODE = True

# Generate parameter list
parameter_list = get_small_parameter_list()

# Generate the Op-Amp matrix
create_opamp_matrix(save_dir_name = '.', params = parameter_list, indices = [i for i in range(TEST_NUM_VARIANTS)] if TEST_MODE else None)

# Display the Op-Amp matrix
display_gds('opamp_matrix.gds', 0.35)


# ### 3. PEX and Spice Simulation
# **Parasitic Extraction** (PEX) is the process of calculating the parasitic capacitive, resistive, and inductive effects of an electronic circuit layout to create an accurate analog model for simulation. In this Op-Amp example, parasitic extraction is done using the open-source tool [Magic](http://opencircuitdesign.com/magic/) and a SPICE netlist is generated for simulation using [this](https://github.com/idea-fasoc/OpenFASOC/blob/main/openfasoc/generators/glayout/tapeout/tapeout_and_RL/extract.bash.template) script.
# 
# [This](https://github.com/idea-fasoc/OpenFASOC/blob/main/openfasoc/generators/glayout/tapeout/tapeout_and_RL/opamp_perf_eval.sp) SPICE testbench is used to run simulations on the post-PEX Op-Amp netlist. The testbench calculates the DC Gain, Unity Gain Bandwidth (UGB), Phase Margin, and 3dB Bandwidth at different values of the bias currents within a range. The best values of these metrics and the values of bias current at which they are achieved are written to `result_ac.txt`. The average total power consumption, and the estimated power consumption for the first two stages of the Op-Amp is written to `result_power.txt`.
# 
# The `brute_force_full_layout_and_PEXsim()` function generates the full layouts for a given list of parameters, runs the post-PEX simulations, and returns an array with the simulation results corresponding to each set of parameters.
# 
# In test mode, only the first 8 sets of parameters are simulated. Set `TEST_MODE` to `False` to run simulations on the whole range. NOTE: This may take a very long time to run.

# In[ ]:


# Test mode. Set to False to simulate the whole 1700+ variations.
TEST_MODE = True

# Define a set of parameters to test
params_array = parameter_list[:8] if TEST_MODE else parameter_list

# Run the simulations and get the results
get_ipython().system('rm -r save_gds_by_index # cleans up any previous simulations')
results_array = brute_force_full_layout_and_PEXsim(sky130, params_array)


# ### 4. Finding The Best Op-Amp (Shotgun Approach)
# The below cell generates a DC Gain v/s Unity Gain Bandwidth (UGB) plot from the results generated above.
# 
# Based on these results, the best variation of the Op-Amp can be chosen for a given user specification. Specifications such as the highest gain or the least power consumption can be targeted.

# In[ ]:


import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import colormaps as cm
cmap = cm.get_cmap('jet')

try:
  params_list_of_dict = [{**opamp_parameters_de_serializer(opparam),**{"index":i}} for i,opparam in enumerate(params_array)]
  results_list_of_dict = [{**opamp_results_de_serializer(opresult),**{"index":i}} for i,opresult in enumerate(results_array)]
except:
  params_list_of_dict = [{**opamp_parameters_de_serializer_old(opparam),**{"index":i}} for i,opparam in enumerate(params_array)]
  results_list_of_dict = [{**opamp_results_de_serializer_old(opresult),**{"index":i}} for i,opresult in enumerate(results_array)]

# ilist is the list of output stage current bias (all of them are the same=93.5uA)
ugblist  =  np.array([opresult["ugb"] for opresult in results_list_of_dict])
gainlist =  np.array([opresult["dcGain"] for opresult in results_list_of_dict])
powerlist = np.array([opresult["power"] for opresult in results_list_of_dict])
freqlist  = ugblist/10**(gainlist/20)

fig, ax = plt.subplots(figsize = (10, 8))
colorlist = []
cnorm = mpl.colors.LogNorm(vmin=10e-5,vmax=1e-3)
sm    = mpl.cm.ScalarMappable(cmap=cmap, norm=cnorm)

for i in powerlist:
    colorlist.append(cmap(cnorm(i)))
ax.scatter(freqlist,gainlist,s=1,alpha=1,c=colorlist)
plt.xlabel('Frequency ugb / Hz')
plt.ylabel('DC Gain / dB20')
ticks=[0.1e-6,1e-6,10e-6,100e-6]
aspect=60
cbar = fig.colorbar(sm, orientation='vertical', ax=ax, label='Power')
ax.set_xscale('log')


# ## Reinforcement Learning Optimization
# Reinforcement Learning (RL) is a field of machine learning and optimal control about finding the most effective behavior of an agent in a dynamic environment to maximize rewards. The focus in RL is finding a balance between exploration and exploitation. The agent learns to perturb the state of the environment to derive maximum reward.
# 
# ### RL Optimization in GLayout
# Here, an RL framework is used to derive the most optimal parameters for a GLayout circuit to maximize the reward derived from the results of the simulation testbench. At each step, the RL agent decides an action (increase/decrease) for each of the parameters based on the specifications observed from the simulation environment. A new set of parameters are generated and fed to the simulation environment, completing the loop. Fig. 6 shows an overview of the framework.
# 
# Each specification is a set of minimum DC Gain and a figure of merit (FoM). The FoM, "Unity Gain Bandwidth (UGB) efficiency", is defined as the ratio of UGB to the average power consumption ($FoM=UGB/power$).
# 
# In this process, two types of specifications are used: Optimized Specifications (oS), with the aim of maximizing their growth, and Capped Specifications (cS), with the aim of reaching the target and stop. As illustrated in Fig. 6, the *cS* reach the target specification, and from that point forward, the *oS* continues to grow as much as possible.
# 
# ![rl-framework](https://i.imgur.com/uHdfs44.png)
# 
# (Fig. 6: Overview of the RL Framework)
# 
# The reward, $r$, is calculated as follows:
# 
# $r_{cS} = \mathrm{min}(\frac{cS-cS*}{cS+cS*}, 0), \hspace{0.5cm} r_{oS} = (\frac{oS-oS*}{oS+oS*})$
# 
# $r = \sum r_{cS} + \sum r_{oS}$
# 
# The example in the following cells demonstrates the training and validation of an RL model for the Op-Amp generated above.

# ### 1. Install Dependencies
# The following libraries are used for the RL optimization:
# 1. [OpenAI Gym](https://github.com/openai/gym)
# 2. [Ray](https://github.com/ray-project/ray)
# 3. [PyTorch](https://github.com/pytorch/pytorch)
# 
# The following cell install all of these libraries and their dependencies.

# In[ ]:


get_ipython().system('pip install gym gymnasium ray[tune] torch dm_tree lz4')


# ### 2. Train the Model
# During training, the _hyperparameters_ (the parameters that define the behaviour of the agent) are tuned. We generate 100 different target specifications within a reasonable range for the training process, to comprehensively cover various regions of the design space.
# 
# The specifications are generated using the `generate_random_specs()` which generates a random set of 100 specifications in a given range. These specifications are saved to `train.yaml`, which is read by `train_model()`. The trained model checkpoint is saved to the `./checkpoint_save` directory.
# 
# NOTE: This will take a very long time.

# In[ ]:


get_ipython().run_line_magic('cd', '/content/OpenFASOC/openfasoc/MLoptimization')

from gen_spec import generate_random_specs

# Generate 100 specifications in train.yaml
generate_random_specs("train.yaml", int(100))


# In[ ]:


from model import train_model

# Train the model and save the checkpoint to ./checkpoint_save
train_model('./checkpoint_save')


# ### 3. Validation
# Given a specification to achieve, the trained model will iterate until the best set of parameters to achieve that specification are found. To validate the training, we generate another set of 100 random specifications. The `evaluate_model()` loads the previously trained checkpoint `./checkpoint_save`, and reports how many of these specifications are achieved with the parameters generated by the trained model within a finite number of iterations.
# 
# An ideal model would be able to achieve all of the generated specifications and within the least possible number of steps. The output of the cell below reports the number of specs tested and the number of specs achieved, as well as logs the reward and action taken at each iteration.
# 
# NOTE: This will take a very long time. This time can be reduced if it is run in parallel.

# In[ ]:


from eval import evaluate_model

generate_random_specs("train.yaml", int(100))
evaluate_model('./checkpoint_save')

