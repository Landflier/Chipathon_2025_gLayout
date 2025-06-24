#!/usr/bin/env python
import pathlib
import os

from glayout.flow.pdk.sky130_mapped import sky130_mapped_pdk as sky130
from glayout.flow.pdk.gf180_mapped  import gf180_mapped_pdk  as gf180
import gdstk
import svgutils.transform as sg
import IPython.display
from IPython.display import clear_output
import ipywidgets as widgets

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

from glayout.flow.pdk.gf180_mapped import gf180_mapped_pdk
from glayout.flow.pdk.mappedpdk import MappedPDK
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


def create_via(PDK: MappedPDK):
  # Define the via dimensions and rules
  via_dimension = PDK.get_grule('via1')['width']
  metal1_dimension = via_dimension + 2 * PDK.get_grule('via1','met1')['min_enclosure']
  metal2_dimension = via_dimension + 2 * PDK.get_grule('via1','met2')['min_enclosure']

  # Get the layers for via and metals
  via_layer = PDK.get_glayer('via1')
  metal1_layer = PDK.get_glayer('met1')
  metal2_layer = PDK.get_glayer('met2')

  # Create the component and add the layers
  top_level = Component(name='via_example')
  top_level << rectangle(size=(via_dimension, via_dimension), layer=via_layer)
  top_level << rectangle(size=(metal1_dimension, metal1_dimension), layer=metal1_layer)
  top_level << rectangle(size=(metal2_dimension, metal2_dimension), layer=metal2_layer)

  return top_level


# **4. Run the Via Function and Generate Layout**

# In[ ]:


via_component = create_via(PDK=gf180_mapped_pdk)
via_component.write_gds('via_example.gds')


# **5. View the Generated Layout**
# - Open KLayout and load the generated GDS file to view your layout.
# - Or view in notebook with the following code block.

# In[ ]:


display_gds('via_example.gds',scale=20)


# By concluding these steps, you will have downloaded Glayout, installed the necessary dependencies, and completed the construction of a simple via using Glayout.
