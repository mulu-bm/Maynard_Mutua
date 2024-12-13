#script to zip and save shapefile to arcgis online
#%%
import os
import zipfile

#Importing necessary libraries
import pandas as pd
import numpy as np
#import geopandas as gpd
#import geopandas as gpd
from arcgis.features import FeatureLayer
from arcgis.features import GeoAccessor

#import gdal
from osgeo import gdal
from matplotlib import pyplot as plt

#import requests
import requests

#Import the Path function
from pathlib import Path

#Import arcpy
import arcpy
from arcpy.sa import *

from arcgis import GIS
gis = GIS('home')

#Reveal the current working directory
root_folder = Path.cwd().parent
data_folder = root_folder / 'Data'
#create route to scratch folder
scratch_folder = root_folder / 'Scratch'
scripts_folder = root_folder / 'Scripts'
processed_folder = root_folder / 'Processed'


data_dir = processed_folder
file_list = os.listdir(data_dir)

arcpy.env.workspace = str(processed_folder)
arcpy.env.overwriteOutput = True


#%%

def zip_shapefile(shapefile_path, output_zip):
    """
    Zip a shapefile's component files.
    
    Parameters:
    shapefile_path (str): Path to the shapefile (e.g., '/path/to/shapefile.shp').
    output_zip (str): Path for the output zip file (e.g., '/path/to/output.zip').
    """
    # Get the base name of the shapefile (without extension)
    shapefile_base = os.path.splitext(shapefile_path)[0]
    
    # List of possible extensions for shapefile components
    shapefile_extensions = ['.shp', '.shx', '.dbf', '.prj', '.cpg']
    
    # Open a zip file for writing
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for ext in shapefile_extensions:
            file_path = shapefile_base + ext
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=os.path.basename(file_path))
                print(f"Added {file_path} to {output_zip}")
    
    print(f"Shapefile successfully zipped into {output_zip}")

#%% Example usage
zip_shapefile(str(processed_folder/'evChargers_combined500YearFlood_intersection.shp'), str(processed_folder/'solar_footprints_intersection.zip'))
zip_shapefile(str(processed_folder/'evChargers_fireprob_10y_HadGEM2-ES_rcp45_bau_2030-2039_mask_intersection.shp'), str(processed_folder/'solar_footprints_intersection.zip'))
zip_shapefile(str(processed_folder/'inaccessibleEVChargers_combined500YearFlood.shp'), str(processed_folder/'solar_footprints_intersection.zip'))
zip_shapefile(str(processed_folder/'inaccessibleEVChargers_fireprob_10y_HadGEM2-ES_rcp45_bau_2030-2039_mask.shp'), str(processed_folder/'solar_footprints_intersection.zip'))
zip_shapefile(str(processed_folder/'inaccessibleEVChargers_floodrisk_200_year_USACE.shp'), str(processed_folder/'solar_footprints_intersection.zip'))
zip_shapefile(str(processed_folder/'inaccessibleTransmissionLines_combined500YearFlood.shp'), str(processed_folder/'solar_footprints_intersection.zip'))
zip_shapefile(str(processed_folder/'inaccessibleTransmissionLines_fireprob_10y_HadGEM2-ES_rcp45_bau_2030-2039_mask.shp'), str(processed_folder/'solar_footprints_intersection.zip'))
zip_shapefile(str(processed_folder/'inaccessibleTransmissionLines_floodrisk_200_year_USACE.shp'), str(processed_folder/'solar_footprints_intersection.zip'))
zip_shapefile(str(processed_folder/'powerplants_combined500YearFlood_intersection.shp'), str(processed_folder/'solar_footprints_intersection.zip'))
zip_shapefile(str(processed_folder/'powerplants_fireprob_10y_HadGEM2-ES_rcp45_bau_2030-2039_mask_intersection.shp'), str(processed_folder/'solar_footprints_intersection.zip'))
zip_shapefile(str(processed_folder/'solar_footprintsfireprob_10y_HadGEM2-ES_rcp85_bau_2090-2099_mask_intersection.shp'), str(processed_folder/'solar_footprints_intersection.zip'))


#%%
file_list = ['evChargers_combined500YearFlood_intersection.shp', 'evChargers_fireprob_10y_HadGEM2-ES_rcp45_bau_2030-2039_mask_intersection.shp', 
             'inaccessibleEVChargers_combined500YearFlood.shp', 'inaccessibleEVChargers_fireprob_10y_HadGEM2-ES_rcp45_bau_2030-2039_mask.shp',
             'inaccessibleEVChargers_floodrisk_200_year_USACE.shp', 'inaccessibleTransmissionLines_combined500YearFlood.shp',
             'inaccessibleTransmissionLines_fireprob_10y_HadGEM2-ES_rcp45_bau_2030-2039_mask.shp', 'inaccessibleTransmissionLines_floodrisk_200_year_USACE.shp',
             'powerplants_combined500YearFlood_intersection.shp', 'powerplants_fireprob_10y_HadGEM2-ES_rcp45_bau_2030-2039_mask_intersection.shp',
             'solar_footprintsfireprob_10y_HadGEM2-ES_rcp85_bau_2090-2099_mask_intersection.shp']

#%%
for i in list(file_list):
    zip_shapefile(str(processed_folder/i), str(processed_folder/i.replace('.shp', '.zip')))

# %%
zip_list = []
for i in file_list:
    zip_list.append(i.replace('.shp', '.zip'))

#%%
for i in zip_list:
    print(i)
    data = str(processed_folder/i)
    shpfile = gis.content.add({}, data)
    published_service = shpfile.publish()
