
#%%

import fire_prob_script_function

fire_prob_script_function.fire_input('average simulation', 'medium emissions scenario', '1980-1989')



#%%

#data options: fire probability, flood plain, extreme heat, sea level rise
#infastructure options: transmission, power plants, ev charging

def user_input(data, infastructure):

    #data_type = arcpy.GetParameterAsText(0)

    data_type = 'fire probability'

    if data_type == 'fire probability':
        model = arcpy.GetParameterAsText(1)
        scenario = arcpy.GetParameterAsText(2)
        time = arcpy.GetParameterAsText(3)
        model = 'average simulation'
        scenario = 'medium emissions scenario'
        time = '1980-1989'
        fire_prob_script_function.fire_input(model, scenario, time)
        
    elif data_type == 'flood plain':
    
    elif data_type == 'extreme heat':
        
    elif data_type == 'sea level rise':