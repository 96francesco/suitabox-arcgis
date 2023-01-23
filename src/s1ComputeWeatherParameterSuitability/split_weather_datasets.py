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

def split_weather_datasets(input_datasets, num_of_datasets):
      """
      Split the list of weather datasets in single tables 
      saved in memory.

      Parameters
      ----------
      input_datasets:     list
                              The list of datasets to be splitted.
      num_of_datasets:    int
                              The number of input datasets.
      """
      counter = 0
      while counter <= int(num_of_datasets - 1):
            weather_dataset = input_datasets[counter]
            arcpy.TableToTable_conversion(
                  weather_dataset, "memory", "weather_dataset_{}".format(counter)
            )
            counter += 1
      return