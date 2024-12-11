#%%

#Importing necessary libraries
import pandas as pd
import numpy as np
#import geopandas as gpd
#import geopandas as gpd
from arcgis.features import FeatureLayer
from arcgis.features import GeoAccessor

from osgeo import gdal
from matplotlib import pyplot as plt
import requests
import json
import re

#Import the Path function
from pathlib import Path

#Import arcpy
import arcpy
from arcpy.sa import *


#Reveal the current working directory
root_folder = Path.cwd().parent
data_folder = root_folder / 'Data'
scratch_folder = root_folder / 'Scratch'
scripts_folder = root_folder / 'Scripts'
#print(root_folder)
#print(scratch_folder)


#Set workspace
arcpy.env.workspace = str(scratch_folder)
arcpy.env.overwriteOutput = True


#%%
def sea_level_input(user_input_flood_time, user_input_flood_scenario):
    user_input_flood_time = '2080-2100' #other options: 2020-2040
    user_input_flood_scenario = 'min' #other options: max, med


    r = requests.get('http://api.cal-adapt.org/api/')
    r.json()

    slug = f'cosmosflooding_{user_input_flood_time}_{user_input_flood_scenario}_mosaic'
    params = {'slug': [slug]}
    response = requests.get('https://api.cal-adapt.org/api/rstores', params = params)

    # It is a good idea to check there were no problems with the request.
    if response.ok:
    data = response.json()
    # Get a list of raster series from results property of data object
    results = data['results']
    # Iterate through the list and print the url property of each object
    for item in results:
        print(item['slug'])


    item_list = []
    for i in json['results']:
        item_list.append(i)
    print(item_list)


    rastersToCombine = []
    for item in item_list:
        dataset = gdal.Open(item['image'], gdal.GA_ReadOnly)
        print(dataset.RasterCount)
        filename = item['slug']
        print(filename)
        output_file = f'{filename}.tif'  # Defining output filename
        rastersToCombine.append(output_file)
        driver = gdal.GetDriverByName("GTiff")  # Specifying format to create copy
        driver.CreateCopy(output_file, dataset,0,['COMPRESS=DEFLATE'])

        # Close the datasets
        dataset = None



    rastersToCombine

    combinedRasterFilename = f'{period}+{scenario}.tif'

    ## Mosaic the TIFF images from the different locations to a new TIFF image
    arcpy.MosaicToNewRaster_management(rastersToCombine, str(scratch_folder),\
                                    combinedRasterFilename, '', '', '', '1','LAST','FIRST')


#%%

r = requests.get('http://api.cal-adapt.org/api/')
r.json()

#flood_time = '2020-2040'
flood_time = '2080-2100'
flood_scenario = 'min'
slug = f'cosmosflooding_{flood_time}_{flood_scenario}_mosaic'
params = {'slug': [slug]}
response = requests.get('https://api.cal-adapt.org/api/rstores', params = params)

# It is a good idea to check there were no problems with the request.
if response.ok:
    data = response.json()
    # Get a list of raster series from results property of data object
    results = data['results']
    # Iterate through the list and print the url property of each object
    for item in results:
        print(item['slug'])


item_list = []
for i in json['results']:
    item_list.append(i)
print(item_list)


#%%
rastersToCombine = []
for item in item_list:
    dataset = gdal.Open(item['image'], gdal.GA_ReadOnly)
    print(dataset.RasterCount)
    filename = item['slug']
    print(filename)
    output_file = f'{filename}.tif'  # Defining output filename
    rastersToCombine.append(output_file)
    driver = gdal.GetDriverByName("GTiff")  # Specifying format to create copy
    driver.CreateCopy(output_file, dataset,0,['COMPRESS=DEFLATE'])

    # Close the datasets
    dataset = None



# %%
rastersToCombine
# %%
combinedRasterFilename = f'{period}+{scenario}.tif'

## Mosaic the TIFF images from the different locations to a new TIFF image
arcpy.MosaicToNewRaster_management(rastersToCombine, str(scratch_folder),\
                                   combinedRasterFilename, '', '', '', '1','LAST','FIRST')
# %%
