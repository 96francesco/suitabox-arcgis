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
import pandas as pd

def table_to_data_frame(in_table, input_fields=None, where_clause=None):
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