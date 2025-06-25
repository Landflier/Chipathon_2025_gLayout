#!/usr/bin/env python
# coding: utf-8

# # GLayout Installation & Simple Via Creation Tutorial
# 

# <a href="https://colab.research.google.com/github/idea-fasoc/OpenFASOC/blob/main/docs/source/notebooks/glayout/GLayout_Via.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
# 

# ```
# OpenFASOC Team, Feb 2024
# SPDX-License-Identifier: Apache-2.0
# ```

# ## Introduction
# Welcome!
# This notebook serves as an introduction to the GDSFactory-based layout automation tool **GLayout** and an example producing a VIA to explain grules and glayers, as a part of [OpenFASoC](https://github.com/idea-fasoc/OpenFASOC).  
# 
# This Notebook will run as-is on Google Collab, or you can run locally by using the install steps in [this document](https://docs.google.com/document/d/e/2PACX-1vRL8ksIvB-fHaqWgkgBPDUznOcDmmFhNrvzPNx9GSSkZyfhJYexEI9gBZCJ0SNNnHdUrAf1EBOeU182/pub). If you choose a local install, skip part 1 of this notebook.
# 

# ## Installation On Google Collab
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


# #### 1.3. Importing Libraries and Utility Functions

# In[ ]:


from glayout import sky130
from glayout import gf180
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


# 
# ## Building a Simple Via
# 
# **1. Open Your Favorite IDE, Create a File**
# - Open your preferred code editor.
# - Create a new Python file: `example.py`.
# - In this collab env, we will edit in code blocks below
# 
# **2. Import Required Modules**

# The via function will use several imports:
# 
# * gf180_mapped_pdk from the glayout.pdk.gf180_mapped module: PDK for GF180 (180-nanometer technology node) provided by the glayout package. The PDK contains technology-specific information including rules and layers.
# 
# * MappedPDK from the glayout.pdk.mappedpdk module: This is a class for mapping generic layers and design rules to the specific layers and design rules present in the chosen PDK.
# 
# * Component from gdsfactory: This is a class representing a layout component, which includes polygons, paths, etc.
# 
# * rectangle from gdsfactory.components: This function creates a rectangle polygon.

# In[ ]:


from gdsfactory import Component
from gdsfactory.components import rectangle


# 
# **3. Define the Via Function**

# The function create_via which takes a single argument which is the PDK. Inside the function, the following steps are executed:
# 
# * Via Dimensions: Using the get_grule method of the PDK object, the width of the via is retrieved from the technology's design rules. This rule specifies the minimum size that the via can be. This dimension is set as both the length and width for a via.
# 
# * Metal Dimensions: The dimensions of the metal layers above and below the via are determined. These dimensions must accommodate the via and any required enclosure space as mandated by the PDK. Enclosure space refers to the required minimum spacing between the edge of the via and the edge of the surrounding metal layer.
# 
# * Layer Retrieval: The get_glayer method retrieves the specific layer numbers or names from the PDK. These are then used to assign the correct graphical layers to the shapes that will be generated.
# 
# * Shape Creation and Placement: An empty Component instance named top_level is created, representing the top component in which all shapes will be placed. Using the insertion operator (<<), rectangles representing the metal layers and via are added to the top_level component with their specified sizes and layers.
# 
# * Return Value: The top_level component, now containing the layout shapes for the metals and via, is the return value of the function. This component can be written out as a GDSII file.

# In[ ]:


def create_via(pdk):
  # Define the via dimensions and rules
  via_dimension = pdk.get_grule('via1')['width']
  metal1_dimension = via_dimension + 2 * pdk.get_grule('via1','met1')['min_enclosure']
  metal2_dimension = via_dimension + 2 * pdk.get_grule('via1','met2')['min_enclosure']

  # Get the layers for via and metals
  via_layer = pdk.get_glayer('via1')
  metal1_layer = pdk.get_glayer('met1')
  metal2_layer = pdk.get_glayer('met2')

  # Create the component and add the layers
  top_level = Component(name='via_example')
  top_level << rectangle(size=(via_dimension, via_dimension), layer=via_layer)
  top_level << rectangle(size=(metal1_dimension, metal1_dimension), layer=metal1_layer)
  top_level << rectangle(size=(metal2_dimension, metal2_dimension), layer=metal2_layer)

  return top_level


# **4. Run the Via Function and Generate Layout**

# In[ ]:


create_via(pdk=gf180).write_gds("via_example_gf180.gds")


# **5. View the Generated Layout**
# - Open KLayout and load the generated GDS file to view your layout.
# - Or view in notebook with the following code block.

# In[ ]:


display_gds('via_example_gf180.gds',scale=20)


# By concluding these steps, you will have downloaded Glayout, installed the necessary dependencies, and completed the construction of a simple via using Glayout.
