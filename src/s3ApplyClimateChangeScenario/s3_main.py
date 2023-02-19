"""
This file is part of Suitabox.

Suitabox is free software: you can redistribute it and/or modify it under the terms of 
the GNU General Public License as published by the Free Software Foundation, either 
version 3 of the License, or (at your option) any later version.

Suitabox is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Foobar. 
If not, see <https://www.gnu.org/licenses/>.
"""

import arcpy

## USER INPUTS
rcp = arcpy.GetParameterAsText(0)
ws_points = arcpy.GetParameter(1)
weather_data = arcpy.GetParameter(2)
field = arcpy.GetParameterAsText(3)
output_folder = arcpy.GetParameterAsText(4)
output_name = arcpy.GetParameterAsText(5)

## CONSTANTS
## they are still treated as variable, i.e., named with lower-case letters
## since their value can change according to user necessities. 

arcpy.env.overwriteOutput = True  # tool will overwrite the output dataset
arcpy.env.qualifiedFieldNames =  False  # output field name won't include the table name
                                        # this setting is crucial for the correct reading 
                                        # of the the feature attribute tables
#list_length = len(weather_data)  # number of datasets uploaded by user
arcpy.env.workspace = "memory"  # set workspace in memory


## EXECUTION

if __name__ == "__main__":

      # import required functions
      import apply_cc_scenario

      from importlib import reload # !!!
      apply_cc_scenario = reload(apply_cc_scenario) # !!!

      from apply_cc_scenario import apply_cc_scenario, extract_raster_values

     
      
      cc_weather_df =  apply_cc_scenario(weather_data, ws_points, rcp, field)

      cc_weather_df.to_csv('{}\\{}.csv'.format(output_folder, output_name), index=False)
      



