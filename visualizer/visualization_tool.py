import streamlit as st

from matplotlib.cm import get_cmap
from mpl_toolkits.basemap import Basemap
from wrf import to_np, getvar, smooth2d, latlon_coords, get_basemap, enable_basemap
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset as NetCDFFile

import os

st.set_page_config(page_title='Visualization tool',
                   page_icon=':bar_chart:',
                   layout='wide')

st.set_option('deprecation.showPyplotGlobalUse', False)

def get_data():
    cur_path = os.path.dirname(__file__)
    new_path = os.path.relpath('..\\data\\original_0_4.nc', cur_path)
    data = NetCDFFile(new_path)
    return data

def plot(data):
    variable = entry_variable
    try:
        val = getvar(data, variable)
    except:
        print('passed')
        return
    if len(val.dims) > 2:
        val = val.isel(bottom_top=0)
    # Smooth the sea level pressure since it tends to be noisey near the mountains
    smooth_data = smooth2d(val, 3)
    # Get the latitude and longitude coordinates
    lats, lons = latlon_coords(val)
    bm = get_basemap(smooth_data)
    # Create a figure that's 10x10
    fig = plt.figure(figsize=(10,10))
    try:
        bm.drawcoastlines(linewidth=0.5)
    except:
        pass
    bm.drawstates(linewidth=5)
    bm.fillcontinents(color='0')
    bm.drawcountries(linewidth=5)
    # Convert the lats and lons to x and y. Make sure you convert the lats and lons to
    # numpy arrays via to_np, or basemap crashes with an undefined RuntimeError.
    x, y = bm(to_np(lons), to_np(lats))
    # Draw the contours and filled contours
    bm.contour(x, y, to_np(smooth_data), 10, colors="black")
    bm.contourf(x, y, to_np(smooth_data), 10)
    # Add a color bar
    plt.colorbar(shrink=.47)
    plt.title(f"{variable} ({val.units})")
    return fig

# -- Sidebar --
st.sidebar.header("Please Filter Here:")
entry_variable = st.sidebar.text_input(
    "Input the variable:"
)


# -- main page --
st.title(":bar_chart: Visualization tool")
st.markdown("###")
with st.spinner('Creating your plot...'):
    chart = plot(get_data())

content = st.columns(1)[0]
content.pyplot(chart)