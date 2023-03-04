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

from table_to_dataframe import table_to_dataframe

def manage_subset_range(input_range, num_of_datasets):
      """
      Consume the input DoY range and create subsets of
      the input weather datasets.

      Parameters
      ----------
      input_range:  str
                        A string containing the start and 
                        end DoY, divided by a dash. It will
                        be splitted in 2 integers.
      num_of_datasets:    int
                              The number of input datasets
      """
      start_doy = int(input_range.split("-")[0])
      end_doy = int(input_range.split("-")[1])

      counter = 0
      while counter <= int(num_of_datasets - 1):
            weather_dataframe = table_to_dataframe(
                  "memory/weather_dataset_{}".format(counter)
            )
            weather_dataframe = weather_dataframe.loc[
                  (weather_dataframe["doy"] >= start_doy)
                  & (weather_dataframe["doy"] <= end_doy)
            ]
            counter += 1

      return