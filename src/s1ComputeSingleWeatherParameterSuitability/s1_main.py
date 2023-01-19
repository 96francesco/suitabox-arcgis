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
import pandas as pd
from arcpy.sa import *
import sys

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
output_gdb = arcpy.GetParameterAsText(16)  # geodatabase to store the output raster layer


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

# just a message
arcpy.AddMessage(
    "The output will be saved in the geodatabase: {}".format(output_gdb)
)  


## FUNCTIONS














def join_data_to_stations(index):
    """
      !!!
      """
    in_table = "weather_stat_{}".format(index)
    in_field = "ID"
    in_features = "ws_feature_layer"

    joined_table = arcpy.AddJoin_management(
        in_features, in_field, in_table, in_field, join_type="KEEP_ALL"
    )
    arcpy.CopyFeatures_management(joined_table, "joined_ws_{}".format(index))

    return "joined_ws_{}".format(index)


def compute_lapse_rate_correction(
    suitability_layers, stat, points, alt_field, cell_size, power, search_radius, dem
):
    """
      !!!
      """

    def create_lapse_rate_layer():
        """
            !!!
            """
        interpolated_dem = Idw(points, alt_field, cell_size, power, search_radius)
        dem_difference = interpolated_dem - dem
        lapse_rate_correction = dem_difference * 0.0065

        return (dem_difference, lapse_rate_correction)

    dem_difference, lapse_rate_layer = [
        create_lapse_rate_layer()[0],
        create_lapse_rate_layer()[1],
    ]

    for i, f in enumerate(suitability_layers):
        if stat != "chilling hours":
            suitability_layers[i] = f + lapse_rate_layer
        else:
            suitability_layers[i] = Con(
                (dem_difference >= -400), f - (-0.0032 * (dem_difference) ** 2), f
            )

    return suitability_layers


def compute_interpolation(stations_with_data, cell_size, power, search_radius):
    """
      !!!
      """
    interpolated_raster = Idw(
        stations_with_data, "STAT", cell_size, power, search_radius
    )

    return interpolated_raster


def compute_average_raster(single_year_rasters, study_area):
    """
    Raster -> Raster
    """
    average_raster = CellStatistics(single_year_rasters, "MEAN")
    average_raster = ExtractByMask(average_raster, study_area)

    return average_raster


def interpolate_weather_parameter(power, search_radius):
    for table in arcpy.ListTables():
        table_index = table.split("_")[2]
        joined_ws = join_data_to_stations(table_index)
        interpolated_raster = compute_interpolation(
            joined_ws, pixel_size, power, search_radius
        )
        interpolated_raster.save("memory/idw_raster_{}".format(table_index))
    interpolated_param_layers = [f for f in arcpy.ListRasters() if f.startswith("idw")]
    return interpolated_param_layers


def reclassify_raster(in_raster, remap_table, out_dir, out_name):

      raster_layer = arcpy.MakeRasterLayer_management(in_raster, "raster_layer")
      reclassified_raster = Reclassify(raster_layer, "Value", remap_table)
      reclassified_raster = Float(reclassified_raster)
      arcpy.CopyRaster_management(
            reclassified_raster, "{gdb}//{name}".format(gdb=out_dir, name=out_name)
      )

      return reclassified_raster


## EXECUTION

if __name__ == "__main__":


      from split_weather_datasets import split_weather_datasets
      
      split_weather_datasets(weather_data, list_length)

      if data_subset_range != "-":
            from src import manage_subset_range
            manage_subset_range(data_subset_range, list_length)

      handle_stat(list_length, statistics, field)
      interpolated_param_layers = interpolate_weather_parameter(
            idw_power, idw_search_radius
      )

      if dem:
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

      average_raster = compute_average_raster(interpolated_param_layers, study_area)
      reclassified_raster = reclassify_raster(
            average_raster, reclass_table, output_gdb, output_name
      )

