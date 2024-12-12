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


#%% Fire Probability Script

def fire_input(user_input_model, user_input_scenario, user_input_time):

    r = requests.get('http://api.cal-adapt.org/api/')
    r.json()
    series = requests.get('http://api.cal-adapt.org/api/series/')

    if user_input_model == 'average simulation':
        slug_model = 'CanESM2'
    elif user_input_model == 'warmer/drier simulation':
        slug_model = 'HadGEM2-ES'
    elif user_input_model == 'cooler/wetter simulation':
        slug_model = 'CNRM-CM5'
    elif user_input_model == 'dissimilar simulation':
        slug_model = 'MIROC5'
    
    if user_input_scenario == 'medium emissions scenario':
        slug_scenario = 'rcp45'
    elif user_input_scenario == 'high emissions scenario':
        slug_scenario = 'rcp85'

    slug_var = 'fireprob' #fixed
    slug_per = '10y' #fixed
    slug_time = 'bau' #fixed, other options: 01 through 12, changes month, just 'bau' contains yearly data
    
    slug = slug_var + '_' + slug_per + '_' + slug_model + '_' + slug_scenario + '_' + slug_time
    params = {'slug': [slug], 'pagesize': 100}

    response = requests.get('http://api.cal-adapt.org/api/series/', params=params)

    # It is a good idea to check there were no problems with the request.
    if response.ok:
        data = response.json()
        # Get a list of raster series from results property of data object
        results = data['results']
        # Iterate through the list and print the url property of each object
        for item in results:
            print(item['slug'])

    json = response.json()
    data_list = json['results'][0]['rasters'] #select bau, just yearly data

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


    response = requests.get(time_selection)
    test = pd.read_json(response.text, typ='series')

    outFileName = (scratch_folder/f'{slug}_{user_input_time}.tif')

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

    outInt = Int(arcpy.Raster(f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask.tif'))
    outInt.save(f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask_int.tif')

    arcpy.conversion.RasterToPolygon(f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask_int.tif', f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask.shp')

    return f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask.shp'
#%%
#file_name = fire_input('average simulation', 'medium emissions scenario', '1980-1989')

# %% Flood Script


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

        #arcpy.ListFields(floodrisk_100_year_DWR)
        return combined100YearFlood

    elif flood_scenario == '200 year':
        floodrisk_200_year_USACE = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/11'
        arcpy.conversion.ExportFeatures(floodrisk_200_year_USACE, str(scratch_folder / 'floodrisk_200_year_USACE'))
        return str(scratch_folder / 'floodrisk_200_year_USACE')
    
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
        return combined500YearFlood
    
        # Display any messages, warnings or errors
        print(arcpy.GetMessages())#Repeat for 500 year flood plain data
     
#%%

#%% Sea Level Rise Script

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
    
    return str(scratch_folder/combinedRasterFilename)



#%%

from arcgis import GIS
gis = GIS('home')
from arcgis.features.analysis import merge_layers
#%%



#%%

weather_type_input = arcpy.GetParameterAsText(0)
infastructure_type_input = arcpy.GetParameterAsText(7) #options: power plants, transmission, solar footprints
#weather_type_input = 'fire probability'

def user_input(weather_type_input, infastructure_type_input):

    if weather_type_input == 'fire probability':
        model = arcpy.GetParameterAsText(1)
        scenario = arcpy.GetParameterAsText(2)
        time_fire = arcpy.GetParameterAsText(3)
        #model = 'average simulation'
        #scenario = 'medium emissions scenario'
        #time_fire = '1980-1989'
        #fire_input(model, scenario, time_fire)
        in_file_name = fire_input(model, scenario, time_fire)
        
    elif weather_type_input == 'flood plane':
        flood_scenario = arcpy.GetParameterAsText(4)
        #flood_scenario = '100 year' #other options: 200 year, 500 year
        in_file_name = flood_input(flood_scenario)

    elif weather_type_input == 'sea level rise':
        sea_level_scenario = arcpy.GetParameterAsText(5)
        sea_level_time = arcpy.GetParameterAsText(6)
        #sea_level_scenario = 'min' #other options: max, med
        #sea_level_time = '2080-2100'
        in_file_name = sea_level_input(sea_level_time, sea_level_scenario)

    if infastructure_type_input == 'power plants':
        powerplants_url = 'https://services3.arcgis.com/bWPjFyq029ChCGur/arcgis/rest/services/Power_Plant/FeatureServer/0'
        area__feature = in_file_name
        inFeatures = [str(area__feature), powerplants_url]
        intersectOutput = 'powerplants_intersection'
        arcpy.analysis.Intersect(inFeatures, intersectOutput, '', '', 'point')

    elif infastructure_type_input == 'transmission':
        transmission_url = 'https://services3.arcgis.com/bWPjFyq029ChCGur/arcgis/rest/services/Transmission_Line/FeatureServer/2'
        area__feature = in_file_name
        inFeatures = [str(area__feature), transmission_url]
        intersectOutput = 'transmission_intersection'
        arcpy.analysis.Intersect(inFeatures, intersectOutput, '', '', 'point')

    elif infastructure_type_input == 'solar footprints':
        solar_footprints_url = 'https://services3.arcgis.com/bWPjFyq029ChCGur/arcgis/rest/services/Solar_Footprints_V2/FeatureServer/0'
        area__feature = in_file_name
        inFeatures = [str(area__feature), solar_footprints_url]
        intersectOutput = 'solar_footprints_intersection'
        arcpy.analysis.Intersect(inFeatures, intersectOutput, '', '', 'point')

#%%
user_input(weather_type_input, infastructure_type_input)


#%% testing!

#user_input('fire probability', 'solar footprints')


# %%
