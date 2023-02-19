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
from arcpy.sa import *
import pandas as pd

def extract_raster_values(raster_file, points):
      """
      Extract values from a raster layer using points. 

      Parameters
      ----------
      raster_file : str
                        Path to the raster file.
      points : Feature class
                        Feature class object containing the points.
      
      Returns
      -------
      extracted_values : Feature class
                        Feature class object containing the extracted values.
      """
      # read raster input and make a raster layer
      raster = arcpy.Raster(raster_file)
      arcpy.MakeRasterLayer_management(raster, 'raster_layer')
      in_raster = 'raster_layer'

      # make feature layer from the input feature class
      arcpy.MakeFeatureLayer_management(points, "feature_layer")  
      in_point_features = 'feature_layer'
      
      # make feature layer for the output feature class
      arcpy.MakeFeatureLayer_management(points, "output_layer")
      extracted_values = 'output_layer'
      
      extracted_values = ExtractValuesToPoints(
            in_point_features=in_point_features,
            in_raster=in_raster,
            out_point_features=extracted_values)
      
      return extracted_values


def apply_cc_scenario(dataset, points, raster_file, field_name):
      """
      Apply climate change scenario to the weather dataset.
      This is done adding the values extracted from RCP raster layer 
      to the selected air temperature field.

      Parameters
      ----------
      dataset : ArcGIS Table
                        Table object containing the weather data.
      points : Feature class
                        Feature class object containing the points.
      raster_file : str
                        Path to the raster file.
      field_name : str
                        Name of the field containing the
                        air temperature values.
      
      Returns
      -------
      joined_df : pd.DataFrame
                        Dataframe containing the weather dataset
                        with a new column containing the air temperature
                        obtained by summing the values extracted from the
                        RCP raster layer to the original air temperature values.
      """
      # extract raster values
      extracted_values = extract_raster_values(raster_file, points)
      arcpy.AddMessage(type(extracted_values))

      # copy the table in memory to avoid the error
      table_copy = 'table_copy'
      arcpy.CopyRows_management(dataset, table_copy)

      # join the table with the extracted values
      arcpy.JoinField_management(table_copy, "ID", extracted_values, "ID",
            ["RASTERVALU"])
     
      # Load the joined table into a pandas dataframe
      arr = arcpy.da.TableToNumPyArray(table_copy, '*')
      joined_df = pd.DataFrame.from_records(arr)

      # add a new column to the dataframe containing the sum of the original
      joined_df['T_RCP'] = joined_df[field_name] + joined_df['RASTERVALU']
      
      return joined_df