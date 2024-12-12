#%%
import arcpy

#%%

import fire_prob_script_function
import flood_script_function
import sea_level_script_function

#%%
fire_prob_script_function.fire_input('average simulation', 'medium emissions scenario', '1980-1989')

#%%
flood_script_function.flood_input('200 year')

#%%
sea_level_script_function.sea_level_input('2080-2100', 'min')

#%%

#data options: fire probability, flood plain, extreme heat, sea level rise
#infastructure options: transmission, power plants, ev charging

def user_input(data_type, infastructure):

    data_type = arcpy.GetParameterAsText(0)
    data_type = 'fire probability'

    if data_type == 'fire probability':
        model = arcpy.GetParameterAsText(1)
        scenario = arcpy.GetParameterAsText(2)
        time_fire = arcpy.GetParameterAsText(3)
        model = 'average simulation'
        scenario = 'medium emissions scenario'
        time_fire = '1980-1989'
        fire_prob_script_function.fire_input(model, scenario, time_fire)
        
    elif data_type == 'flood plain':
        flood_scenario = arcpy.GetParameterAsText(4)
        flood_scenario = '100 year' #other options: 200 year, 500 year
        flood_script_function.flood_input(flood_scenario)

    elif data_type == 'sea level rise':
        sea_level_scenario = arcpy.GetParameterAsText(5)
        sea_level_time = arcpy.GetParameterAsText(6)
        sea_level_scenario = 'min' #other options: max, med
        sea_level_time = '2080-2100'
        sea_level_script_function.sea_level_input(sea_level_time, sea_level_scenario)