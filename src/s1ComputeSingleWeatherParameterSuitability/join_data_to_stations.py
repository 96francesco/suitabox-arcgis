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

def join_data_to_stations(index):
      """
      Joined the computed dataframe with the desired statistics to 
      the stations points based on their ID.

      Parameters
      ----------
      index:     int
                        The index of the dataframe to process.
      """
      in_table = "weather_stat_{}".format(index)
      in_field = "ID"
      in_features = "ws_feature_layer"

      joined_table = arcpy.AddJoin_management(
            in_features, in_field, in_table, in_field, join_type="KEEP_ALL"
      )
      arcpy.CopyFeatures_management(joined_table, "joined_ws_{}".format(index))

      return "joined_ws_{}".format(index)