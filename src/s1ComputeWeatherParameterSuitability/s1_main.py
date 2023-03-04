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

import os
import arcpy
from arcpy.sa import *
import sys
from importlib import reload # !!!

sys.path.insert(1, 'src')


## USER INPUTS

# Category: General inputs
study_area = arcpy.GetParameter(0)  # feature class of the study area
ws_points = arcpy.GetParameter(1)  # feature class of the weather stations (points)
weather_data = arcpy.GetParameter(2)  # weather dataset table(s). read as list
pixel_size = arcpy.GetParameterAsText(3)  # desired pixel size for the output raster
field = arcpy.GetParameterAsText(4)  # field with the weather parameter value
statistics = arcpy.GetParameterAsText(5)  # statistics to compute on the weather dataset(s)
data_subset_range = arcpy.GetParameterAsText(6)  # DoY-based subset for the weather dataset(s)
reclass_table = arcpy.GetParameter(7)  # reclasification table with the new values

# Category: Interpolation settings
interpolation_method = arcpy.GetParameterAsText(8)  # default = IDW
idw_power = arcpy.GetParameterAsText(9)  # default = 2
idw_search_radius = arcpy.GetParameterAsText(10)  # default = RadiusVariable
idw_points_num = arcpy.GetParameterAsText(11)  # default = 12
idw_distance = arcpy.GetParameterAsText(12)  # default = None
dem = arcpy.GetParameterAsText(13)  # DEM raster for lapse rate correction
altitude_field = arcpy.GetParameterAsText(14)  # field with stations' altitude 

# Category: Output settings
output_name = arcpy.GetParameterAsText(15)  # name to give to the output raster layer
normalise = arcpy.GetParameterAsText(16)  # normalise the output raster layer

## CONSTANTS
## they are still treated as variable, i.e., named with lower-case lettersm
## since their value can change according to user necessities. 

list_length = len(weather_data)  # number of datasets uploaded by user
pixel_size = int(pixel_size)  # pixel size string to integer conversion

tbx_dir = os.path.realpath(__file__).split("single")[0]  # .tbx file directory
aprx = arcpy.mp.ArcGISProject("CURRENT")  # set the project file !!!
map = aprx.listMaps("Map")[0]  # set the current map dataframe !!!

arcpy.env.overwriteOutput = True  # tool will overwrite the output dataset
arcpy.env.qualifiedFieldNames =  False  # output field name won't include the table name
                                        # this setting is crucial for the correct reading 
                                        # of the the feature attribute tables

arcpy.env.extent = study_area  # set the uploaded study area as map extent
arcpy.env.workspace = "memory"  # set workspace in memory

# make feature layers from the feature classes
arcpy.MakeFeatureLayer_management(study_area, "study_area_feature_layer")
arcpy.MakeFeatureLayer_management(ws_points, "ws_feature_layer")  


## EXECUTION

if __name__ == "__main__":
      
      # Wipe out the memory workspace
      for table in arcpy.ListTables():
            arcpy.Delete_management(table)

      # import required functions
      from split_weather_datasets import split_weather_datasets
      from handle_stat import handle_stat
      from interpolate_weather_parameter import interpolate_weather_parameter
      import compute_final_raster
      compute_final_raster = reload(compute_final_raster) # !!!
      from compute_final_raster import *

       # check if input pixel size and DEM resolution match
      if dem and int(pixel_size) != round(float(str(arcpy.GetRasterProperties_management(dem, 
                                                'CELLSIZEX')))):
            arcpy.AddError("Desired pixel size and DEM resolution do not match.")
            exit()

      split_weather_datasets(weather_data, list_length)

      # if user has a custom DoY range, modify the input dataset accordingly
      if data_subset_range != "-":
            # from manage_subset_range import manage_subset_range
            import manage_subset_range
            manage_subset_range = reload(manage_subset_range)
            from manage_subset_range import manage_subset_range
            manage_subset_range(data_subset_range, list_length)

      # call the correct function to calculate the required statistics
      handle_stat(list_length, statistics, field)
      interpolated_param_layers = interpolate_weather_parameter(
            idw_power, idw_search_radius, pixel_size
      )

      # if user upload a DEM raster, compute the lapse rate correction
      if dem:
            from compute_lapse_rate_correction import compute_lapse_rate_correction
            
            arcpy.AddMessage("Computing the topographic correction...")
            interpolated_param_layers = compute_lapse_rate_correction(
                  interpolated_param_layers,
                  statistics,
                  ws_points,
                  altitude_field,
                  pixel_size,
                  idw_power,
                  idw_search_radius,
                  dem,
            )

      # compute final output
      average_raster = compute_average_raster(interpolated_param_layers, study_area)
      reclassified_raster = reclassify_raster(
            average_raster, reclass_table, output_name
      )
      if normalise:
            import normalisation
            normalisation = reload(normalisation) # !!!
            from normalisation import normalise_raster
            normalised_raster = normalise_raster(reclassified_raster, output_name)

