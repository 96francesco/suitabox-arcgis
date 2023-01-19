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

def dataframe_to_table(dataframe, df_index):
      """
      Convert a pd.DataFrame to ArcGIS table.

      Parameters
      ----------
      dataframe:  pd.DataFrame
                  The dataframe to be converted.
      df_index:   int
                  The dataframe index in the 
                  dataframe list.
      """
      # Convert the DataFrame to a list of tuples
      records = dataframe.to_records(index=False)

      # Create an in-memory table
      arcpy.CreateTable_management("memory", "weather_stat_{}".format(df_index))

      # Add fields to the in-memory table
      arcpy.AddField_management(
            "memory/weather_stat_{}".format(df_index), 
            "ID", 
            "LONG"
            )
      arcpy.AddField_management(
            "memory/weather_stat_{}".format(df_index), 
            "STAT", 
            "LONG"
            )

      # Use an InsertCursor to insert the rows into the in-memory table
      fields = ["ID", "STAT"]
      cursor = arcpy.da.InsertCursor(
            "memory/weather_stat_{}".format(df_index), 
            fields
            )

      for record in records:
            cursor.insertRow(record)
      del cursor