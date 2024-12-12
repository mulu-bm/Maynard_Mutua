#%%
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

#import os
import os

#Reveal the current working directory
root_folder = Path.cwd().parent
data_folder = root_folder / 'Data'
#create route to scratch folder
scratch_folder = root_folder / 'Scratch'
scripts_folder = root_folder / 'Scripts'
#print(root_folder)
#print(scratch_folder)


#Set workspace
arcpy.env.workspace = str(scratch_folder)
arcpy.env.overwriteOutput = True


#%% Fire Probability Script

#takes input of model type, scenario type, and time frame to create a shapefile of the fire probability
def fire_input(user_input_model, user_input_scenario, user_input_time):

    #data souce
    r = requests.get('http://api.cal-adapt.org/api/')
    #checking available data
    r.json()
    #fire data is in section 'series'
    series = requests.get('http://api.cal-adapt.org/api/series/')

    #for loop to assign user chosen model to name of model to be used in querying data
    if user_input_model == 'average simulation':
        slug_model = 'CanESM2'
    elif user_input_model == 'warmer/drier simulation':
        slug_model = 'HadGEM2-ES'
    elif user_input_model == 'cooler/wetter simulation':
        slug_model = 'CNRM-CM5'
    elif user_input_model == 'dissimilar simulation':
        slug_model = 'MIROC5'
    
    #for loop to assign user chosen scenario to name of scenario to be used in querying data
    if user_input_scenario == 'medium emissions scenario':
        slug_scenario = 'rcp45'
    elif user_input_scenario == 'high emissions scenario':
        slug_scenario = 'rcp85'

    #fixed variables in slug query
    slug_var = 'fireprob' #fixed
    slug_per = '10y' #fixed
    slug_time = 'bau' #fixed, other options: 01 through 12, changes month, just 'bau' contains yearly data
    

    #warmer/drier simulation: HadGEM2
    #average simulation: CanESM2
    #cooler/wetter simulation: CNRM-CM5
    #dissimlar simulation (unlike other three to produce maximal coverage): MIROC5

    #RCP 4.5: medium emissions scenario, GHG peak by 2040 and decline
    #RCP 8.5: high emissions scenario, GHG continue to rise throughout the 21st century

    #create slug query
    slug = slug_var + '_' + slug_per + '_' + slug_model + '_' + slug_scenario + '_' + slug_time
    params = {'slug': [slug], 'pagesize': 100}

    #query data
    response = requests.get('http://api.cal-adapt.org/api/series/', params=params)

    #print out data
    if response.ok:
        data = response.json()
        # Get a list of raster series from results property of data object
        results = data['results']
        # Iterate through the list and print the url property of each object
        for item in results:
            print(item['slug'])

    #json is list of dictionaries of data
    json = response.json()
    #this is a list of all the years
    data_list = json['results'][0]['rasters'] #select bau, just yearly data

    #if statement to select the time frame of the data
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

    #get just data from selected time
    response = requests.get(time_selection)
    #read data
    test = pd.read_json(response.text, typ='series')

    #create output file name in scratch folder using slug and input time
    outFileName = str(scratch_folder/f'{slug}_{user_input_time}')

    #open data source
    ds = gdal.Open(test['image'])
    print(f'ds is a {type(ds)} object')
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()

    #create mask based on quantile value
    #quantile value chosen as method for mask so reative risk can be studied
    arr_mask_val = np.nanquantile(arr, [ .50]) 
    arr_mask = np.where(arr > arr_mask_val, 1, np.nan) #replace 1 with 'arr' if you want to replace with actual value

    #shape of output file
    [cols, rows] = arr.shape

    #specify driver as geotiff
    driver = gdal.GetDriverByName("GTiff")

    #create output file
    outdata = driver.Create(f'{outFileName}_mask.tif', rows, cols, 1, gdal.GDT_Float32)
    #outdata = driver.Create(f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask.tif', rows, cols, 1, gdal.GDT_Float32)
    #set geotransform and projection
    outdata.SetGeoTransform(ds.GetGeoTransform()) #set same geotransform as input
    outdata.SetProjection(ds.GetProjection()) #set the same projection as input
    #write array to output file and save to disk
    outdata.GetRasterBand(1).WriteArray(arr_mask)
    outdata.FlushCache() #saves to disk

    #clear variables
    outdata = None
    band=None
    ds=None

    #convert raster to integer values for shapefile conversion
    outInt = Int(arcpy.Raster(f'{outFileName}_mask.tif'))
    outInt.save(f'{outFileName}_mask_int.tif')

    #outInt = Int(arcpy.Raster(f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask.tif'))
    #outInt.save(f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask_int.tif')

    #convert raster to polygon shapefile for intersection analysis
    arcpy.conversion.RasterToPolygon(f'{outFileName}_mask_int.tif', f'{scratch_folder}/{slug}_{user_input_time}_mask.shp')
    #arcpy.conversion.RasterToPolygon(f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask_int.tif', f'v:/Maynard_Mutua/Scratch/{slug}_{user_input_time}_mask.shp')

    #return output file name so it can be selected in intersection analysis
    return f'{outFileName}_mask.shp'
#%%
#testing fire function outside of arcpro
#file_name = fire_input('average simulation', 'medium emissions scenario', '1980-1989')

# %% Flood Script

#takes input of flood scenario to create a shapefile of the flood probability areas based on flood scenarios

def flood_input(flood_scenario):
    #if statement to select the flood scenario
    if flood_scenario == '100 year':
        #read in data from url
        floodrisk_100_year_FEMA = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/5' #FEMA Effective
        floodrisk_100_year_Regional = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/7' #Regional/Special Studies
        floodrisk_100_year_DWR = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/8' #DWR Awareness
        floodrisk_100_year_USACE = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/9' #USACE Comprehensive Study

        #create feature layers from urls
        floodrisk_100yearlayer1 = FeatureLayer(floodrisk_100_year_FEMA)
        floodrisk_100yearlayer2 = FeatureLayer(floodrisk_100_year_Regional)
        floodrisk_100yearlayer3 = FeatureLayer(floodrisk_100_year_DWR)
        floodrisk_100yearlayer4 = FeatureLayer(floodrisk_100_year_USACE)
        #combine feature layers into list
        hundredYearFeatureLayers = [floodrisk_100yearlayer1, floodrisk_100yearlayer2, floodrisk_100yearlayer3, floodrisk_100yearlayer4]
        #print out fields in feature layers
        for layer in hundredYearFeatureLayers:
            for f in layer.properties.fields:
                print(f['name'])
            print('---------------')


        #Add code to merge or dissolve layers into one
        addSourceInfo = 'ADD_SOURCE_INFO'

        # Create FieldMappings object to manage merge output fields
        fieldMappings = arcpy.FieldMappings()

        # Add all fields from all layers
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

        #return output file name for use in intersection
        return combined100YearFlood

    elif flood_scenario == '200 year':
        #read in data from url and convert to shapefile
        floodrisk_200_year_USACE = 'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/BAM/MapServer/11'
        arcpy.conversion.ExportFeatures(floodrisk_200_year_USACE, str(scratch_folder / 'floodrisk_200_year_USACE'))
        #return output file name for use in intersection
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

        # Add all fields 
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
        #return output file name for use in intersection
        return combined500YearFlood
    
        # Display any messages, warnings or errors
        print(arcpy.GetMessages())#Repeat for 500 year flood plain data
     
#%%

#%% Sea Level Rise Script

#takes input of sea level rise scenario and time frame to create a shapefile of the sea level rise areas based on sea level rise scenarios

def sea_level_input(user_input_flood_time, user_input_flood_scenario):
    #testing variables
    #user_input_flood_time = '2080-2100' #other options: 2020-2040
    #user_input_flood_scenario = 'min' #other options: max, med


    r = requests.get('http://api.cal-adapt.org/api/')
    r.json()

    #set slug to query based on user input, no need for if statement as variable names are the same as user input options
    slug = f'cosmosflooding_{user_input_flood_time}_{user_input_flood_scenario}_mosaic'
    params = {'slug': [slug]}
    #get response based on slug query
    response = requests.get('https://api.cal-adapt.org/api/rstores', params = params)

    # It is a good idea to check there were no problems with the request.
    if response.ok:
        data = response.json()
        # Get a list of raster series from results property of data object
        results = data['results']
        # Iterate through the list and print the url property of each object
        for item in results:
            print(item['slug'])

    #create list of items from response
    item_list = []
    for i in json['results']:
        item_list.append(i)
    print(item_list)

    #create list of rasters to combine
    rastersToCombine = []
    #for loop to create tif files from rasters for each item in the list
    for item in item_list:
        dataset = gdal.Open(item['image'], gdal.GA_ReadOnly)
        print(dataset.RasterCount)
        #name with slug
        filename = item['slug']
        print(filename)
        output_file = f'{filename}.tif'  # Defining output filename
        #append to list
        rastersToCombine.append(output_file)
        driver = gdal.GetDriverByName("GTiff")  # Specifying format to create copy
        driver.CreateCopy(output_file, dataset,0,['COMPRESS=DEFLATE'])

        # Close the datasets
        dataset = None

    rastersToCombine

    #create combined raster file name
    combinedRasterFilename = f'{period}+{scenario}.tif'

    ## Mosaic the TIFF images from the different locations to a new TIFF image
    arcpy.MosaicToNewRaster_management(rastersToCombine, str(scratch_folder),\
                                    combinedRasterFilename, '', '', '', '1','LAST','FIRST')
    
     #return output file name for use in intersection
    return str(scratch_folder/combinedRasterFilename)



#%%

from arcgis import GIS
gis = GIS('home')
from arcgis.features.analysis import merge_layers

#%%

#get user input from arcpro on extreme weather type and infrastructure type
weather_type_input = arcpy.GetParameterAsText(0)
infastructure_type_input = arcpy.GetParameterAsText(7) #options: power plants, transmission, solar footprints
#weather_type_input = 'fire probability'

#function to take user input of weather type and infastructure type to create files
#this was done as a function so data and operations were only called when needed

def user_input(weather_type_input, infastructure_type_input):
    model = arcpy.GetParameterAsText(1)
    scenario = arcpy.GetParameterAsText(2)
    time_fire = arcpy.GetParameterAsText(3)
    flood_scenario = arcpy.GetParameterAsText(4)
    sea_level_scenario = arcpy.GetParameterAsText(5)
    sea_level_time = arcpy.GetParameterAsText(6)

    
#Add error messages to guide user on selecting only variables that correspond to the extreme weather type
    if weather_type_input == 'fire probability':
        if flood_scenario != '' or sea_level_scenario != '' or sea_level_time != '':
            arcpy.AddError('Please select variables only corresponding to fire probability scenario')
            print('Please select only one extreme weather')
    elif weather_type_input == 'flood plane':
        if model != '' or scenario != '' or time_fire != '' or sea_level_scenario != '' or sea_level_time != '':
            arcpy.AddError('Please select variables only corresponding to flood plane scenario')
            print('Please select only one extreme weather')
    elif weather_type_input == 'sea level rise':
        if model != '' or scenario != '' or time_fire != '' or flood_scenario != '':
            arcpy.AddError('3 Please select variable from one extreme weather type')
            print('Please select variables only corresponding to sea level rise scenario')

    #if statement to select the extreme weather type
    if weather_type_input == 'fire probability':
        #assign user input to variables
        #model type: average simulation, warmer/drier simulation, cooler/wetter simulation, dissimilar simulation
        #scenario type: medium emissions scenario, high emissions scenario
        #select time frame, 10 year increments from 1960-2099 eg: 1960-1969, 1970-1979, etc
        #model = 'average simulation'
        #scenario = 'medium emissions scenario'
        #time_fire = '1980-1989'
        #fire_input(model, scenario, time_fire)
        #call fire_input function to create file and assign name of file to in_file_name for intersection
        in_file_name = fire_input(model, scenario, time_fire)
        
    elif weather_type_input == 'flood plane':
        #get flood scenario (100 year, 200 year, 500 year)
        #flood_scenario = '100 year' #other options: 200 year, 500 year
        #call flood_input function to create file and assign name of file to in_file_name for intersection
        in_file_name = flood_input(flood_scenario)

    elif weather_type_input == 'sea level rise':
        #get sea level rise scenario (min, max, med) and time frame (2020-2040, 2080-2100)
        #sea_level_scenario = 'min' #other options: max, med
        #sea_level_time = '2080-2100'
        #call sea_level_input function to create file and assign name of file to in_file_name for intersection
        in_file_name = sea_level_input(sea_level_time, sea_level_scenario)

    #if statement to select the infastructure type to be intersected with
    if infastructure_type_input == 'power plants':
        #read in data from url
        powerplants_url = 'https://services3.arcgis.com/bWPjFyq029ChCGur/arcgis/rest/services/Power_Plant/FeatureServer/0'
        #feature to be intersected is from return statement from above funtions
        area__feature = in_file_name
        #intersecting features
        inFeatures = [str(area__feature), powerplants_url]
        #output file name
        intersectOutput = 'powerplants_intersection'
        #perform intersection, write to scratch folder
        arcpy.analysis.Intersect(inFeatures, intersectOutput, '', '', 'point')

    elif infastructure_type_input == 'transmission':
        #read in data from url
        transmission_url = 'https://services3.arcgis.com/bWPjFyq029ChCGur/arcgis/rest/services/Transmission_Line/FeatureServer/2'
        #feature to be intersected is from return statement from above funtions
        area__feature = in_file_name
        #intersecting features
        inFeatures = [str(area__feature), transmission_url]
        #output file name
        intersectOutput = 'transmission_intersection'
        #perform intersection, write to scratch folder
        arcpy.analysis.Intersect(inFeatures, intersectOutput, '', '', 'line')

    elif infastructure_type_input == 'solar footprints':
        #read in data from url
        solar_footprints_url = 'https://services3.arcgis.com/bWPjFyq029ChCGur/arcgis/rest/services/Solar_Footprints_V2/FeatureServer/0'
        #feature to be intersected is from return statement from above funtions
        area__feature = in_file_name
        #intersecting features
        inFeatures = [str(area__feature), solar_footprints_url]
        #output file name
        intersectOutput = 'solar_footprints_intersection'
        #perform intersection, write to scratch folder
        arcpy.analysis.Intersect(inFeatures, intersectOutput, '', '', 'point')


#%% testing!

#user_input('fire probability', 'solar footprints')

#%%
#Call with inputs from arcpro to create files
#output is files in scratch folder
user_input(weather_type_input, infastructure_type_input)


#%%
import os

data_dir = scratch_folder
file_list = os.listdir(data_dir)




# %%
import os
import zipfile

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

# Example usage
zip_shapefile(str(scratch_folder/'solar_footprints_intersection.shp'), str(scratch_folder/'solar_footprints_intersection.zip'))


# %%
data = 'solar_footprints_intersection.zip'
shpfile = gis.content.add({}, data)

# %%
shpfile
# %%
published_service = shpfile.publish()
# %%
display(published_service)
# %%
