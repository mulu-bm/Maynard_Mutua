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

def flood_input(flood_scenario):
    if flood_scenario == '100 year':
        floodrisk_100_year_FEMA = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/5' #FEMA Effective
        floodrisk_100_year_Regional = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/7' #Regional/Special Studies
        floodrisk_100_year_DWR = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/8' #DWR Awareness
        floodrisk_100_year_USACE = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/9' #USACE Comprehensive Study

        floodrisk_100yearlayer1 = FeatureLayer(floodrisk_100_year_FEMA)
        floodrisk_100yearlayer2 = FeatureLayer(floodrisk_100_year_Regional)
        floodrisk_100yearlayer3 = FeatureLayer(floodrisk_100_year_DWR)
        floodrisk_100yearlayer4 = FeatureLayer(floodrisk_100_year_USACE)
        hundredYearFeatureLayers = [floodrisk_100yearlayer1, floodrisk_100yearlayer2, floodrisk_100yearlayer3, floodrisk_100yearlayer4]
        for layer in hundredYearFeatureLayers:
            for f in layer.properties.fields:
                print(f['name'])
            print('---------------')


        #Add code to merge or dissolve layers into one
        addSourceInfo = 'ADD_SOURCE_INFO'

        # Create FieldMappings object to manage merge output fields
        fieldMappings = arcpy.FieldMappings()

        # Add all fields from both oldStreets and newStreets
        fieldMappings.addTable(floodrisk_100_year_FEMA)
        fieldMappings.addTable(floodrisk_100_year_Regional)
        fieldMappings.addTable(floodrisk_100_year_DWR)
        fieldMappings.addTable(floodrisk_100_year_USACE)

        # Remove all output fields from the field mappings, except fields 
        # 'Shape', 'Shape_Length', & 'Shape_Area'
        for field in fieldMappings.fields:
            if field.name not in ['Shape', 'Shape_Length', 'Shape_Area']:
                fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))

        # Use Merge tool to move features into single dataset
        combined100YearFlood = str(scratch_folder / 'combined100YearFlood') 
        arcpy.management.Merge([floodrisk_100_year_FEMA, 
                                floodrisk_100_year_Regional, 
                                floodrisk_100_year_DWR,
                                floodrisk_100_year_USACE],combined100YearFlood, '', addSourceInfo)

        # Display any messages, warnings or errors
        print(arcpy.GetMessages())

        arcpy.ListFields(floodrisk_100_year_DWR)

    elif flood_scenario == '200 year':
        floodrisk_200_year_USACE = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/11'
        arcpy.conversion.ExportFeatures(floodrisk_200_year_USACE, str(scratch_folder / 'floodrisk_200_year_USACE'))

    elif flood_scenario == '500 year':
        #Add code to merge or dissolve layers into one
        addSourceInfo = 'ADD_SOURCE_INFO'

        floodrisk_500_year_FEMA = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/13' #FEMA Effective
        floodrisk_500_year_Regional = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/15' #Regional/Special Studies
        floodrisk_500_year_USACE = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/16' #USACE Comprehensive Study

        floodrisk_500yearlayer1 = FeatureLayer(floodrisk_500_year_FEMA)
        floodrisk_500yearlayer2 = FeatureLayer(floodrisk_500_year_Regional)
        floodrisk_500yearlayer3 = FeatureLayer(floodrisk_500_year_USACE)

        # Create FieldMappings object to manage merge output fields
        fieldMappings = arcpy.FieldMappings()

        # Add all fields from both oldStreets and newStreets
        fieldMappings.addTable(floodrisk_500_year_FEMA)
        fieldMappings.addTable(floodrisk_500_year_Regional)
        fieldMappings.addTable(floodrisk_500_year_USACE)

        # Remove all output fields from the field mappings, except fields 
        # 'Shape', 'Shape_Length', & 'Shape_Area'
        for field in fieldMappings.fields:
            if field.name not in ['Shape', 'Shape_Length', 'Shape_Area']:
                fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))

        # Use Merge tool to move features into single dataset
        combined500YearFlood = str(scratch_folder / 'combined500YearFlood') 
        arcpy.management.Merge([floodrisk_500_year_FEMA, 
                                floodrisk_500_year_Regional,
                                floodrisk_500_year_USACE],combined500YearFlood, '', addSourceInfo)

        # Display any messages, warnings or errors
        print(arcpy.GetMessages())#Repeat for 500 year flood plain data





#%%

flood_input('500 year')

# %%
