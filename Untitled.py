#!/usr/bin/env python
# coding: utf-8

# In[1]:


from curses import flash
import os
from pickle import TRUE
from re import L
import requests
import validators
import gzip
import shutil
from urllib.parse import urlparse

import sys
import math
import xarray as xa
import numpy as np
from rio_cogeo import cog_validate
import rioxarray

# Mapping
import matplotlib as mpl
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker


# In[2]:


base_path = '/home/asubedi/Desktop/work/hs3_cog_converter/'
file_name = 'AE20141015.Gonzalo.loc.nc'
path = '/home/asubedi/Desktop/work/hs3_cog_converter/AE20141015.Gonzalo.loc.nc'
engine = 'netcdf4'
variable = 'VHRMC_LIS_FRD'


# In[3]:


file1 = xa.open_dataset(path, engine=engine, decode_coords='all', decode_times=False)


# In[4]:


print(file1)


# In[5]:


print(file1.Energy.data, len(file1.Energy.data))


# In[6]:


print(file1.Latitude.data, len(file1.Latitude.data))
#Create new np array here with sorted latitude
sorted_lat = np.sort(np.copy(file1.Latitude.data), axis=0)


# In[7]:


print(file1.Longitude.data, len(file1.Longitude.data))
#Create new sorted np lon array here
sorted_lon = np.sort(np.copy(file1.Longitude.data), axis=0)


# In[8]:


data_dict = []
data_length = len(file1.Longitude.data)


# In[9]:


for i in range(data_length):
    data_dict.append({
        "latitude":file1.Latitude.data[i],
        "longitude":file1.Longitude.data[i],
        "value":file1.Energy.data[i]
    })


# In[10]:


grid = np.zeros((data_length, data_length))


# In[11]:


print(grid)
print(sorted_lat)
print(sorted_lon)


# In[12]:


def find_lat_index(lat_value):
    index = 0
    for lat in sorted_lat:
        if(lat == lat_value):
            return index
        index = index + 1
        
def find_lon_index(lon_value):
    index = 0
    for lon in sorted_lon:
        if(lon == lon_value):
            return index
        index = index + 1


# In[13]:


i = 0
for data in data_dict:
    lat_index = find_lat_index(data["latitude"])
    lon_index = find_lon_index(data["longitude"])
    grid[lat_index][lon_index] = data["value"]
    i = i+1
print(i)


# In[ ]:





# In[14]:


new_xarray = xa.DataArray(
    data = grid,
    dims=("latitude", "longitude"),
    coords={
        "latitude":sorted_lat,
        "longitude":sorted_lon
    },
    attrs=dict(
        description="",
        units="",
    ),
)


# In[ ]:


new_xarray = new_xarray.transpose('latitude', 'longitude')
new_xarray.rio.set_spatial_dims(x_dim='longitude', y_dim='latitude', inplace=True)
new_xarray.rio.crs
new_xarray.rio.set_crs('epsg:4326', inplace=TRUE)
#new_xarray.plot()
cog_path = f'{base_path}alan.tif'
new_xarray.rio.to_raster(rf'{cog_path}', driver='COG')


# In[ ]:




