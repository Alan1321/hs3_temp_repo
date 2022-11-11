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
import time

#main variables
base_path = '/home/asubedi/Desktop/hs3_temp_repo'
file_name = 'AE20130912.Gabrielle.loc.nc'
path = f'{base_path}/{file_name}'
engine = 'netcdf4'
var_name = 'Subset_Of_Stations'
split_range = 10000
current_setting = "Full"

files = []
lat_len = 0
lat = []
lon = []
lon_len = 0
npData = []

def listDir(dir):
    fileNames = os.listdir(dir)
    for i in range(len(fileNames)):
        global lat_len, lon_len, npData, lat, lon, files
        files = []
        lat_len = 0
        lat = []
        lon = []
        lon_len = 0
        npData = []
        generate_cog(fileNames[i])

def generate_cog(filename):

    try:
        start_time = time.time()
        print("---------------------------------------------------------------------------------------------------")
        print(f"Starting file: {filename}")
        #open file here
        path = f"{FOLDER_PATH}/{filename}"
        file1 = xa.open_dataset(path, engine=engine, decode_coords='all', decode_times=False)

        #lat, lon, data
        latitude = file1.Latitude.data
        longitude = file1.Longitude.data
        data = file1[var_name].data  

        full_dict = []
        for i in range(len(data)):
            full_dict.append({
                "latitude":latitude[i],
                "longitude":longitude[i],
                "data":data[i]
        })

        print("Full Dict Length: ", len(full_dict))

        if(len(full_dict) > 25000):
            print(f"TOO_BIG_ERROR -- FILE: {filename} SIZE:{len(full_dict)}   .................")
            print("---------------------------------------------------------------------------------------------------")
            return

        #Sort geolocation here
        full_sorted_lat = np.sort(np.copy(latitude), axis=0)
        full_sorted_lon = np.sort(np.copy(longitude), axis=0)

        # split_sorted_lat = np.sort(np.copy(split_lat), axis=0)
        # split_sorted_lon = np.sort(np.copy(split_lon), axis = 0)

        #init grid here
        full_grid = np.zeros((len(latitude), len(latitude)))
        # split_grid = np.zeros((split_range, split_range))

        def find_full_lat_lon(lat, lon):
            lat_index = None
            lon_index = None
            for i in range(len(full_sorted_lat)):
                if(full_sorted_lat[i] == lat):
                    lat_index = i
                    break
            for i in range(len(full_sorted_lon)):
                if(full_sorted_lon[i] == lon):
                    lon_index = i
                    break
            #print(lat_index, lon_index)
            return [lat_index, lon_index]

        for di in full_dict:
            index = find_full_lat_lon(di["latitude"], di["longitude"])
            full_grid[index[0]][index[1]] = di["data"]

        new_xarray = xa.DataArray(
        data = full_grid,
        dims=("latitude", "longitude"),
        coords={
            "latitude":full_sorted_lat,
            "longitude":full_sorted_lon
        },
        attrs=dict(
            description="",
            units="",
        ),
        )

        new_xarray = new_xarray.transpose('latitude', 'longitude')
        new_xarray.rio.set_spatial_dims(x_dim='longitude', y_dim='latitude', inplace=True)
        new_xarray.rio.crs
        new_xarray.rio.set_crs('epsg:4326', inplace=TRUE)

        cog_path = f'{base_path}/hs3-cogs-3/{filename}.tif'
        new_xarray.rio.to_raster(rf'{cog_path}', driver='COG')

        print(f"Complete!! Time Taken: {time.time() - start_time}")
        print("---------------------------------------------------------------------------------------------------")
    except KeyboardInterrupt:
        sys.exit()
    else:
        print(f"Error {filename}")

FOLDER_PATH = "/home/asubedi/Desktop/hs3-datasets"

listDir(FOLDER_PATH)