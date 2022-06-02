# Interface libraries
from tkinter import *
from PIL import ImageTk, Image

#Data management libraries
from matplotlib.cm import get_cmap
from mpl_toolkits.basemap import Basemap
from wrf import to_np, getvar, smooth2d, latlon_coords, get_basemap, enable_basemap
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset as NetCDFFile

import os

root = Tk()
root.title('Visualizer')
root.geometry("500x300")
root.resizable(False,False)

def plot(data):
    variable = entry_variable.get()
    try:
        val = getvar(data, variable)
    except:
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
    #bm.contour(x, y, to_np(smooth_slp), 10, colors="black")
    bm.contourf(x, y, to_np(smooth_data), 10)
    # Add a color bar
    plt.colorbar(shrink=.47)
    plt.title(f"{variable} ({val.units})")
    plt.show()


# Get data
cur_path = os.path.dirname(__file__)
new_path = os.path.relpath('..\\data\\original_0_4.nc', cur_path)
data = NetCDFFile(new_path)

entry_variable=Entry(root,text='Variable', width= 25)
entry_variable.pack()

graph_button = Button(root,text='Graph', command= lambda:plot(data))
graph_button.pack()

root.mainloop()