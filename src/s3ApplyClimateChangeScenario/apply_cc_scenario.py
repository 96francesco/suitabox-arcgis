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

def table_to_dataframe(in_table, input_fields=None, where_clause=None):
      """
      Convert an ArcGIS table into a pd.DataFrame with an object ID index,
      and the selected input fields using an arcpy.da.SearchCursor
      
      Parameters
      ----------
      in_table:     str
                        The directory of the table to convert.
      input_fields: str
                        A list (or tuple) of field names. 
                        For a single field, you can use a string instead 
                        of a list of strings.
      wbere_clause: str
                        An optional expression that limits the records 
                        returned. For more information on where 
                        clauses and SQL statements
      
      Returns
      -------
      pd.DataFrame
                        The converted table to a pd.DataFrame.
      """
      OIDFieldName = arcpy.Describe(in_table).OIDFieldName
      
      if input_fields:
            final_fields = [OIDFieldName] + input_fields
      else:
            final_fields = [field.name for field in arcpy.ListFields(in_table)]
      
      data = [
            row
            for row in arcpy.da.SearchCursor(
                  in_table, final_fields, where_clause=where_clause
            )
      ]
      fc_dataframe = pd.DataFrame(data, columns=final_fields)
      fc_dataframe = fc_dataframe.set_index(OIDFieldName, drop=True)
      
      return fc_dataframe

def extract_raster_values(raster_file, ws_points):
      """
      !!!
      """

      # read raster input and make a raster layer
      raster = arcpy.Raster(raster_file)
      arcpy.MakeRasterLayer_management(raster, 'raster_layer')
      in_raster = 'raster_layer'

      # make feature layer from the input feature class
      arcpy.MakeFeatureLayer_management(ws_points, "feature_layer")  
      in_point_features = 'feature_layer'
      
      # make feature layer for the output feature class
      arcpy.MakeFeatureLayer_management(ws_points, "output_layer")
      extracted_values = 'output_layer'
      
      extracted_values = ExtractValuesToPoints(in_point_features=in_point_features,
            in_raster=in_raster,
            out_point_features=extracted_values)
      
      return extracted_values


def apply_cc_scenario(dataset, points, raster_file, field_name):
      """
      !!!
      """

      # extract raster values
      extracted_values = extract_raster_values(raster_file, points)
      arcpy.AddMessage(type(extracted_values))

      # copy the table in memory to avoid the error
      table_copy = 'table_copy'
      arcpy.CopyRows_management(dataset, table_copy)

      # joined_table = arcpy.AddJoin_management(
      #       table_copy, "ID", extracted_values, "ID", join_type="KEEP_ALL"
      # )
      arcpy.JoinField_management(table_copy, "ID", extracted_values, "ID",
            ["RASTERVALU"])

      # arr = arcpy.da.TableToNumPyArray(joined_table, '*')
      # joined_df = pd.DataFrame.from_records(arr)
     
      # Load the joined table into a pandas dataframe
      arr = arcpy.da.TableToNumPyArray(table_copy, '*')
      joined_df = pd.DataFrame.from_records(arr)

      arcpy.AddMessage(joined_df.columns.tolist())
      joined_df['T_RCP'] = joined_df[field_name] + joined_df['RASTERVALU']
      
      return joined_df