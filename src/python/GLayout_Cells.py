#!/usr/bin/env python
# coding: utf-8

# # GLayout: List of Built-in Cells

# <a href="https://colab.research.google.com/github/idea-fasoc/OpenFASOC/blob/main/docs/source/notebooks/glayout/GLayout_Cells.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# ```
# OpenFASOC Team, Feb 2024
# SPDX-License-Identifier: Apache-2.0
# ```

# ## Introduction
# Welcome!
# This notebook serves as an introduction to the GDSFactory-based layout automation tool **GLayout** and an example two-stage Operational Amplifier (Op-Amp) generator, as a part of [OpenFASoC](https://github.com/idea-fasoc/OpenFASOC).  
# 
# This Notebook will run as-is on Google Collab, or you can run locally by using the install steps in [this document](https://docs.google.com/document/d/e/2PACX-1vRL8ksIvB-fHaqWgkgBPDUznOcDmmFhNrvzPNx9GSSkZyfhJYexEI9gBZCJ0SNNnHdUrAf1EBOeU182/pub). If you choose a local install, skip part 1 of this notebook.
# 
# ### List of Generators
# 
# **Utility Generators**
# - Via
# - Guardring
# - Routing (Straight, L, and C)
# 
# **PCell Generators**
# 1. Primitive Cells / `glayout.primitives`
#   - FET (NMOS, PMOS)
#   - MIM Capacitor
#   - Guard Rings with Metalization
#   - Via
# 
# 
# 2. Intermediate PCells / `glayout.components`
#   - Differential Pair
#   - Differential to Single-Ended Converter
# 
# 
# 3. WIP PCells (The cells can be used inside other PCells, but are not available as standalone PCells yet)
#   - Current Mirror
# 
# **High-Level Design Examples**
# - OPAMP / `glayout.components.opamp`
# 

# ## Preparation
# ### 1. Clone the repository and install dependencies
# **Python Dependencies**
# * [`gdsfactory`](https://github.com/gdsfactory/gdsfactory): Provides the backend for GDS manipulation.
# * [`sky130`](https://github.com/gdsfactory/skywater130): The Skywater 130nm PDK Python package for GDSFactory to use in this demo.
# * [`gf180`](https://github.com/gdsfactory/gf180): The GF 180nm PDK Python package for GDSFactory to use in this demo.
# * [`gdstk`](https://heitzmann.github.io/gdstk/): (installed as a part of gdsfactory) Used for converting GDS files into SVG images for viewing.
# * [`svgutils`](https://svgutils.readthedocs.io/en/latest/): To scale the SVG image.
# 
# **System Dependencies**
# * [`klayout`](https://klayout.de/): For DRC (Design Rule Checking).
# 

# #### 1.1. Installing the binary dependency `klayout` using micromamba
# **You only need to run this once**

# In[ ]:


# Setup the environment for the OpenFASOC GDSFactory generator
# You only need to run this block once!

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


# #### 1.2. Adding the `klayout` binary to the system path, then goto the GLayout directory
# **You need to run this each time you restart the kernel**

# In[ ]:


# Setup the environment for the OpenFASOC GDSFactory generator

# Adding micro-mamba binary directory to the PATH
# This directory contains Klayout
import pathlib
import os
conda_prefix_path = pathlib.Path('conda-env')
CONDA_PREFIX = str(conda_prefix_path.resolve())
get_ipython().run_line_magic('env', 'CONDA_PREFIX={CONDA_PREFIX}')
# Add conda packages to the PATH
PATH = os.environ['PATH']
get_ipython().run_line_magic('env', 'PATH={PATH}:{CONDA_PREFIX}/bin')

get_ipython().run_line_magic('cd', '/content/OpenFASOC/openfasoc/generators/glayout')


# #### 1.3. Importing Libraries and Utility Functions

# In[ ]:


from glayout.flow.pdk.sky130_mapped import sky130_mapped_pdk as sky130
from glayout.flow.pdk.gf180_mapped  import gf180_mapped_pdk  as gf180
import gdstk
import svgutils.transform as sg
import IPython.display
from IPython.display import clear_output
import ipywidgets as widgets

# Redirect all outputs here
hide = widgets.Output()

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


# ## List of Built-in Cells

# ### 1. Primitives
# #### MOSFET (nmos/pmos)
# 
# **Parameters:**
# - **pdk:** Which PDK to use
# - **width:** Width of one finger (um)
# - **length:** Length of one finger (um). The default value is the minimum channel length available
# - **fingers:** Number of fingers per transistor
# - **multipliers:** Number of transistors in this cell
# - **with_tie:** bool
# - **with_dummy:** tuple of 2 bools
# - **with_dnwell:** bool
# - **with_substrate_tap:** bool
# - **sd_route_topmet:** Expose the S/D connection on which metal layer
# - **gate_route_topmet:** Expose the Gate connection on which metal layer
# - **sd_route_left:** Choose which direction the S/D connection goes to
# - **rmult:** Integer multipler of routing width
# - **sd_rmult:** Same as above
# - **gate_rmult:** Same as above
# - **interfinger_rmult:** Same as above
# - **tie_layers:** Run the body tie metal on which layer. This entry is a tuple with 2 elements
#     - X metal
#     - Y metal
# - **substrate_tap_layers:** Run the substrate tie metal on which layer. This entry is a tuple with 2 elements
#     - X metal
#     - Y metal
# - **dummy_routes:** Enable routing to the dummy transistors
# 
# Note that most of the parameters have a default value. The user usually doesn't need to populate all of them.

# In[ ]:


from glayout.flow.primitives.fet import nmos
# Used to display the results in a grid (notebook only)
left = widgets.Output()
leftSPICE = widgets.Output()
grid = widgets.GridspecLayout(1, 2)
grid[0, 0] = left
grid[0, 1] = leftSPICE
display(grid)

comp = nmos(pdk = sky130, fingers=5)
# Display the components' GDS and SPICE netlists
with left:
    print('Skywater 130nm N-MOSFET (fingers = 5)')
    display_component(comp, scale=2.5)
with leftSPICE:
    print('Skywater 130nm SPICE Netlist')
    print(comp.info['netlist'].generate_netlist())


# #### MIM Capacitor
# **Parameters:**
# - **pdk:** Which PDK to use
# - **Size:** A tuple of 2 values
#     - X Size: um
#     - Y Size: um

# In[ ]:


from glayout.flow.primitives.mimcap import mimcap
# Used to display the results in a grid (notebook only)
left = widgets.Output()
leftSPICE = widgets.Output()
grid = widgets.GridspecLayout(1, 2)
grid[0, 0] = left
grid[0, 1] = leftSPICE
display(grid)

comp = mimcap(pdk=sky130, size=[20.0,5.0])
# Display the components' GDS and SPICE netlists
with left:
    print('Skywater 130nm MIM Capacitor (10.0 x 5.0)')
    display_component(comp, scale=2.5)
with leftSPICE:
    print('Skywater 130nm SPICE Netlist')
    print(comp.info['netlist'].generate_netlist())


# #### Guard Ring
# 
# **Parameters:**
# - **pdk:** Which PDK to use
# - **enclosed_rectangle:** A tuple of 2 values
#     - X Size (um)
#     - Y Size (um)
# - **sdlayer:** Which diffusion layer?
# - **horizontal_glayer:** Which metal layer to use for the X routing
# - **vertical_glayer:** Which metal layer to use for the Y routing
# - **sides：** A tuple of 4 bools

# In[ ]:


from glayout.flow.primitives.guardring import tapring
# Used to display the results in a grid (notebook only)
left = widgets.Output()
leftSPICE = widgets.Output()
grid = widgets.GridspecLayout(1, 2)
grid[0, 0] = left
grid[0, 1] = leftSPICE
display(grid)

comp = tapring(pdk=sky130, enclosed_rectangle=[10.0, 5.0])
# Display the components' GDS and SPICE netlists
with left:
    print('Skywater 130nm MIM Capacitor (10.0 x 5.0)')
    display_component(comp, scale=2.5)

# This cell does not have LVS netlist


# ### Intermediate PClls

# #### Diff Pair
# create a diffpair with 2 transistors placed in two rows with common centroid place. Sources are shorted
# 
# **Parameters:**
# - **pdk:** Which PDK to use
# - **width:** Width of the transistors (um)
# - **length:** Length of the transistors, None or 0 means use min length (um)
# - **fingers:** Number of fingers in the transistors (must be 2 or more)
# - **short_source:** If true connects source of both transistors. Otherwise they will be exposed as routing terminals.
# - **n_or_p_fet:** If true the diffpair is made of nfets else it is made of pfets
# - **substrate_tap:** if true place a tapring around the diffpair (connects on met1)

# In[ ]:


from glayout.flow.blocks.elementary.diff_pair import diff_pair
# Used to display the results in a grid (notebook only)
left = widgets.Output()
leftSPICE = widgets.Output()
grid = widgets.GridspecLayout(1, 2)
grid[0, 0] = left
grid[0, 1] = leftSPICE
display(grid)

comp = diff_pair(pdk=sky130)
# Display the components' GDS and SPICE netlists
with left:
    print('Skywater 130nm Differential Pair')
    display_component(comp, scale=2.5)
with leftSPICE:
    print('Skywater 130nm SPICE Netlist')
    print(comp.info['netlist'].generate_netlist())


# #### Cascode load of the OPAMP
# (aka. Differential to Single Ended Converter)
# 
# **Parameters:**
# - **pdk:** Which PDK to use
# - **rmult:** Routing Width Multiplier
# - **half_pload:** a 3-element tuple describing the PMOS inside
#     - Transistor Width (um)
#     - Transistor Length (um)
#     - Transistor Multiplier
# - **via_xlocation:** X position delta of the two staggered vias (um)

# In[ ]:


from glayout.flow.blocks.composite.differential_to_single_ended_converter import differential_to_single_ended_converter
# Used to display the results in a grid (notebook only)
left = widgets.Output()
leftSPICE = widgets.Output()
grid = widgets.GridspecLayout(1, 2)
grid[0, 0] = left
grid[0, 1] = leftSPICE
display(grid)

comp = differential_to_single_ended_converter(pdk=sky130, rmult=1, half_pload=[2,0.5,1], via_xlocation=0)
# Display the components' GDS and SPICE netlists
with left:
    print('Skywater 130nm Cascode Active Load')
    display_component(comp, scale=2.5)
with leftSPICE:
    print('Skywater 130nm SPICE Netlist')
    print(comp.info['netlist'].generate_netlist())


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
# The Op-Amp generator accepts the following optional parameters:
# - `half_diffpair_params`: A tuple of (width, length, fingers) for the differential pair.
# - `diffpair_bias`: A tuple of (width, length, fingers) for the differential pair bias transistors.
# - `half_common_source_params`: A tuple of (width, length, fingers, multipliers) for the common source PMOS transistor.
# - `half_common_source_bias`: A tuple of (width, length, fingers, multipliers) for the common source bias transistors. The `multipliers` only apply to the mirror transistor, reference transistor has a multiplier of 1.
# - `output_stage_params`: A tuple of (width, length, fingers) for the output stage NMOS transistor.
# - `output_stage_bias`: A tuple of (width, length, fingers) for the output stage bias transistors.
# - `half_pload`: A tuple of (width, length, fingers) for the load (differential to single-ended converter). The `fingers` only apply to the bottom two transistors.
# - `mim_cap_size`: A tuple of (width, length) for individual MIM capacitors.
# - `mim_cap_rows`: The number of rows in the MIM capacitor array.
# - `rmult`: The multiplier for the width of the routes.
# 
# These parameters can be changed to generate a very wide range of Op-Amp designs.

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
half_pload = (6,1,6)
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

