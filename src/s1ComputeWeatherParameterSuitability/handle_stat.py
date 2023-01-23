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
from table_to_dataframe import table_to_dataframe
from dataframe_to_table import dataframe_to_table


## Functions to compute the different statistics

def handle_mean(weather_dataframe, field):
      """
      Compute the mean from the input datasets, grouping
      using the stations ID.

      Parameters
      ----------
      weather_dataframe:      pd.DataFrame
                              The dataframe to be used to
                              compute the mean.
      field:                  str
                              The field containing the 
                              relevant data.
      
      Returns
      -------
      pd.Dataframe
                        The resulting dataframe with the mean
                        value computer for each station ID.
      """
      weather_stat = weather_dataframe.groupby("ID", as_index=False)[field].mean()
      return weather_stat


def handle_max(weather_dataframe, field):
      """
      Compute the maximum value from the input datasets,
      grouping using the stations ID.

      Parameters
      ----------
      weather_dataframe:      pd.DataFrame
                              The dataframe to be used to
                              compute the mean.
      field:                  str
                              The field containing the 
                              relevant data.
      
      Returns
      -------
      pd.Dataframe
                        The resulting dataframe with the max
                        value computer for each station ID.
      """
      weather_stat = weather_dataframe.groupby("ID", as_index=False)[field].max()
      return weather_stat


def handle_min(weather_dataframe, field):
      """
      Compute the minimum value from the input datasets,
      grouping using the stations ID.

      Parameters
      ----------
      weather_dataframe:      pd.DataFrame
                              The dataframe to be used to
                              compute the minimum.
      field:                  str
                              The field containing the 
                              relevant data.
      
      Returns
      -------
      pd.Dataframe
                        The resulting dataframe with the min
                        value computer for each station ID.
      """
      weather_stat = weather_dataframe.groupby("ID", as_index=False)[field].min()
      return weather_stat


def handle_daily_min(weather_dataframe, field):
      """
      Compute the average daily minimum value from the input datasets,
      grouping using the stations ID.

      Parameters
      ----------
      weather_dataframe:      pd.DataFrame
                              The dataframe to be used.
      field:                  str
                              The field containing the 
                              relevant data.
      
      Returns
      -------
      pd.Dataframe
                        The resulting dataframe with the average daily
                        minimum value computed for each station ID.
      """
      daily_min = weather_dataframe.groupby(["ID", "doy"], as_index=False)[field].min()
      daily_min = pd.DataFrame(daily_min)
      daily_min.columns = ["ID", "doy", "STAT"]
      weather_stat = daily_min.groupby("ID", as_index=False)["STAT"].mean()
      return weather_stat


def handle_daily_max(weather_dataframe, field):
      """
      Compute the average daily maximum value from the input datasets,
      grouping using the stations ID.

      Parameters
      ----------
      weather_dataframe:      pd.DataFrame
                              The dataframe to be used.
      field:                  str
                              The field containing the 
                              relevant data.
      
      Returns
      -------
      pd.Dataframe
                        The resulting dataframe with the average daily
                        maximum value computed for each station ID.
      """
      daily_max = weather_dataframe.groupby(["ID", "doy"], as_index=False)[field].max()
      daily_max = pd.DataFrame(daily_max)
      daily_max.columns = ["ID", "doy", "STAT"]
      weather_stat = daily_max.groupby("ID", as_index=False)["STAT"].mean()
      return weather_stat


def handle_chill_hours(weather_dataframe, field):
      """
      !!!
      """
      chilling_hours = weather_dataframe.loc[
            (weather_dataframe[field] < 7.2) & (weather_dataframe[field] > 0)
      ]
      weather_stat = chilling_hours.groupby("ID", as_index=False)[field].count()
      weather_stat = pd.DataFrame(weather_stat)

      return weather_stat


def handle_stat(num_of_datasets, statistics, field):
      """
      Call the correct function to compute the required
      statistics from the the input weather datasets.

      Parameters
      ----------
      num_of_datasets:  int
                        The number of input datasets. 
      statistics:       str
                        The statistics to be calculated
                        from the weather datasets.
      field:            str
                        The field containing the 
                        relevant data.
      """
      counter = 0
      while counter <= int(num_of_datasets - 1):
            weather_dataframe = table_to_dataframe(
                  "memory/weather_dataset_{}".format(counter)
            )

            # dictionary with all the functions created so far
            weather_stat = {
                  "mean": handle_mean,
                  "maximum": handle_max,
                  "minimum": handle_min,
                  "average of daily maximum": handle_daily_max,
                  "average of daily minimum": handle_daily_min,
                  "chilling hours": handle_chill_hours,
            }[statistics](weather_dataframe, field)

            weather_stat.columns = ["ID", "STAT"]
            dataframe_to_table(weather_stat, counter)
            arcpy.Delete_management("memory/weather_dataset_{}".format(counter))

            counter += 1