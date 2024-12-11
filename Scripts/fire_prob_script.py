
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

#Import the Path function
from pathlib import Path

#Import arcpy
import arcpy

#%%

#Reveal the current working directory
root_folder = Path.cwd().parent
data_folder = root_folder / 'Data'
scratch_folder = root_folder / 'Scratch'
scripts_folder = root_folder / 'Scripts'
print(root_folder)
print(scratch_folder)


#Set workspace
arcpy.env.workspace = str(scratch_folder)
arcpy.env.overwriteOutput = True


#%%
r = requests.get('http://api.cal-adapt.org/api/')
r.json()

series = requests.get('http://api.cal-adapt.org/api/series/')



#%%
#user_input_model = arcpy.GetParameterAsText(0)
user_input_model = 'average simulation'

if user_input_model == 'average simulation':
    slug_model = 'CanESM2'
elif user_input_model == 'warmer/drier simulation':
    slug_model = 'HadGEM2-ES'
elif user_input_model == 'cooler/wetter simulation':
    slug_model = 'CNRM-CM5'
elif user_input_model == 'dissimilar simulation':
    slug_model = 'MIROC5'

#user_input_scenario = arcpy.GetParameterAsText(1)
user_input_scenario = 'medium emissions scenario'

if user_input_scenario == 'medium emissions scenario':
    slug_scenario = 'rcp45'
elif user_input_scenario == 'high emissions scenario':
    slug_scenario = 'rcp85'


slug_var = 'fireprob' #fixed
slug_per = '10y' #fixed

#slug_model = 'CNRM-CM5' #other options: 'CanESM2', 'HadGEM2', 'MIROC5'
#warmer/drier simulation: HadGEM2
#average simulation: CanESM2
#cooler/wetter simulation: CNRM-CM5
#dissimlar simulation (unlike other three to produce maximal coverage): MIROC5

#slug_scenario = 'rcp45' #other options: 'rcp85'
#RCP 4.5: medium emissions scenario, GHG peak by 2040 and decline
#RCP 8.5: high emissions scenario, GHG continue to rise throughout the 21st century
#%%
slug_time = 'bau' #fixed, other options: 01 through 12, changes month, just 'bau' contains yearly data
slug = slug_var + '_' + slug_per + '_' + slug_model + '_' + slug_scenario + '_' + slug_time

params = {'slug': [slug], 'pagesize': 100}
#params = {'name': ['fire'], 'slug': 'prob', 'pagesize': 100}

#slug: {variable}_{period}_{model}_{scenario}

# Use params with the url.
response = requests.get('http://api.cal-adapt.org/api/series/', params=params)

# It is a good idea to check there were no problems with the request.
if response.ok:
    data = response.json()
    # Get a list of raster series from results property of data object
    results = data['results']
    # Iterate through the list and print the url property of each object
    for item in results:
        print(item['slug'])



#%%
json = response.json()
json


#%%
data_list = json['results'][0]['rasters'] #select bau, just yearly data
data_list

#%%
#user_input_time = arcpy.GetParameterAsText(2)
user_input_time = '2040-2049'

#user_input_time = '2060-2069'
if user_input_time == '1960-1969':
    time_selection = json['results'][0]['rasters'][0]
if user_input_time == '1970-1979':
    time_selection = json['results'][0]['rasters'][1]
if user_input_time == '1980-1989':
    time_selection = json['results'][0]['rasters'][2]
if user_input_time == '1990-1999':
    time_selection = json['results'][0]['rasters'][3]
if user_input_time == '2000-2009': 
    time_selection = json['results'][0]['rasters'][4]
if user_input_time == '2010-2019':
    time_selection = json['results'][0]['rasters'][5]
if user_input_time == '2020-2029':
    time_selection = json['results'][0]['rasters'][6]
if user_input_time == '2030-2039':
    time_selection = json['results'][0]['rasters'][7]
if user_input_time == '2040-2049':
    time_selection = json['results'][0]['rasters'][8]
if user_input_time == '2050-2059':
    time_selection = json['results'][0]['rasters'][9]
if user_input_time == '2060-2069':
    time_selection = json['results'][0]['rasters'][10]
if user_input_time == '2070-2079':
    time_selection = json['results'][0]['rasters'][11]
if user_input_time == '2080-2089':
    time_selection = json['results'][0]['rasters'][12]
if user_input_time == '2090-2099':
    time_selection = json['results'][0]['rasters'][13]

#time_selection = json['results'][0]['rasters'][0]
print(time_selection)

#%%
response = requests.get(time_selection)
test = pd.read_json(response.text, typ='series')
test['image']

#%%
outFileName = (scratch_folder/f'{slug}_{user_input_time}.tif')
outFileName

#%%
 
ds = gdal.Open(test['image'])
print(f'ds is a {type(ds)} object')
band = ds.GetRasterBand(1)
arr = band.ReadAsArray()

arr_mask_val = np.nanquantile(arr, [ .50]) 
arr_mask = np.where(arr > arr_mask_val, 1, np.nan) #replace 1 with 'arr' if you want to replace with actual value

[cols, rows] = arr.shape

driver = gdal.GetDriverByName("GTiff")

outdata = driver.Create(f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask.tif', rows, cols, 1, gdal.GDT_Float32)
outdata.SetGeoTransform(ds.GetGeoTransform()) #set same geotransform as input
outdata.SetProjection(ds.GetProjection()) #set the same projection as input
outdata.GetRasterBand(1).WriteArray(arr_mask)
outdata.FlushCache() #saves to disk

outdata = None
band=None
ds=None

#print(f'arr_1 is a {type(arr_1)} object')


#%%
from arcpy.sa import *

# %%

outInt = Int(arcpy.Raster(f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask.tif'))
outInt.save(f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask_int.tif')


#%%

arcpy.conversion.RasterToPolygon(f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask_int.tif', f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask.shp')

# %%
