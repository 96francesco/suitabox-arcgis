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

if __name__ == "__main__":
      pass
else:
      #imports
      import arcpy
      from arcpy.sa import *
      import pandas as pd
      import os
      import locale
      
      # general settings
      separator = locale.localeconv()["decimal_point"]
      path = arcpy.env.workspace + "\\"
      
      # user inputs
      mask_area = arcpy.GetParameterAsText(2) # area of study 
      ws_points = arcpy.GetParameterAsText(3) # points shapefile of the weather stations
      topography = arcpy.GetParameterAsText(5) # digital elevation model

      flowering_period = arcpy.GetParameterAsText(8) # custom flowering period
      fruit_growth_period = arcpy.GetParameterAsText(9) # custom fruit set and growth period

      # set custom flowering period if required
      if flowering_period != '-':
            flowering_start_doy = int(flowering_period.split("-")[0])
            flowering_end_doy = int(flowering_period.split("-")[1])
            arcpy.AddMessage("Custom flowering period: {start}-{end}".format(
                  start=str(flowering_start_doy), end=str(flowering_end_doy)))

      # set custom fruit growth period if required
      if fruit_growth_period != '-':
            fruit_growth_start_doy = int(fruit_growth_period.split("-")[0])
            fruit_growth_end_doy = int(fruit_growth_period.split("-")[1])
            arcpy.AddMessage("Custom fruit set and growth period: {start}-{end}".format(
                  start=str(fruit_growth_start_doy), end=str(fruit_growth_end_doy)))

      # interpolation settings
      idw_power = int(arcpy.GetParameterAsText(13)) # IDW poer
      search = arcpy.GetParameterAsText(14) # type of search radius
      points_num = arcpy.GetParameterAsText(15) # number of points to consider
      distance = arcpy.GetParameterAsText(16) # distance to consider
      # set the type of search radius depending on user's choice
      if search == 'RadiusVariable':
            search_radius = "{search}({points}, {dist})".format(search=search, 
                  points=points_num, dist=distance)
      elif search == 'RadiusFixed':
            search_radius = "{search}({dist}, {points})".format(search=search,
                  dist=distance, points=points_num)

      name = arcpy.GetParameterAsText(18) # output name

      # if topography exists, set the spatial resolution (the same of DEM)
      if topography:
            spatial_resolution = str(arcpy.GetRasterProperties_management(topography, "CELLSIZEX"))
            cell_size = int(spatial_resolution.split(separator)[0])
      else:
            cell_size = 100

      # define the method
      def avocado_fun():
            """
            This function computes the single years suitability layers for
            the crop species "avocado".
            """
            global lapse_rate_correction
            for file in os.listdir(path):
                  os.chdir(path)
                  if file.startswith("weather_dataset_") or file.startswith("new_dataset_"):
                        weather_df = pd.DataFrame(pd.read_csv(file, error_bad_lines=False))
                        dataset_name = os.path.basename(path + str(file))
                        dataset_index = dataset_name.replace(".", "_").split("_")[2]
                        weather_df.columns = weather_df.columns.str.strip()

                        annual_avg = weather_df.groupby("ID", as_index=False)['Tair'].mean()
                        annual_avg = pd.DataFrame(annual_avg)
                        annual_avg.columns = ["ID", "annual_avg"]

                        # calculate the average winter temperature
                        winter_df = weather_df.loc[(weather_df['doy'] <= 59) | 
                              (weather_df['doy'] > 335)]
                        winter_df = pd.DataFrame(winter_df)
                        winter_avg = winter_df.groupby("ID", as_index=False)['Tair'].mean()
                        winter_avg = pd.DataFrame(winter_avg)
                        winter_avg.columns = ["ID1", "winter_avg"]

                        # calculate the average temperature during flowering
                        if flowering_period != '-': # use the custom period set by user
                              flowering_df = weather_df.loc[(weather_df['doy'] >= flowering_start_doy) &
                                    (weather_df['doy'] <= flowering_end_doy)]
                        elif flowering_period == '-': # use default period
                              flowering_df = weather_df.loc[(weather_df['doy'] >= 60) &
                                    (weather_df['doy'] <= 151)]
                        flowering_avg = flowering_df.groupby("ID", as_index=False)["Tair"].mean()
                        flowering_avg = pd.DataFrame(flowering_avg)
                        flowering_avg.columns = ["ID2", "FlowAvgT"]

                        # calculate the average of the daily maximum temperature during flowering
                        flowering_daily_max = flowering_df.groupby(["ID", "doy"], 
                              as_index=False)["Tair"].max()
                        flowering_daily_max = pd.DataFrame(flowering_daily_max)
                        flowering_daily_max.columns = ["ID", "doy", "Tair"]
                        avg_flowering_daily_max = flowering_daily_max.groupby("ID", 
                              as_index=False)["Tair"].mean()
                        avg_flowering_daily_max = pd.DataFrame(avg_flowering_daily_max)
                        avg_flowering_daily_max.columns = ["ID3", "FlowMaxT"]

                        # calculate the absolute maximum temperature during fruit set and growth
                        if fruit_growth_period != '-': # use the custom period set by user
                              fruit_growth_df = weather_df.loc[(weather_df['doy'] >=\
                                    fruit_growth_start_doy) &
                                    (weather_df['doy'] <= fruit_growth_end_doy)]
                        elif fruit_growth_period == '-': # use default settings
                              fruit_growth_df = weather_df.loc[(weather_df['doy'] >= 152) &
                                    (weather_df['doy'] <= 365)]
                        fruit_growth_max = fruit_growth_df.groupby("ID", as_index=False)["Tair"].max()
                        fruit_growth_max = pd.DataFrame(fruit_growth_max)
                        fruit_growth_max.columns = ["ID4", "FruitMaxT"]

                        # calculate absolute minimum temperature during the year
                        annual_min = weather_df.groupby('ID', as_index=False)['Tair'].min()
                        annual_min = pd.DataFrame(annual_min)
                        annual_min.columns = ["ID5", "annual_min"]

                        # join the df_list
                        df_list = [winter_avg, flowering_avg, avg_flowering_daily_max,\
                              fruit_growth_max, annual_min]
                        joined_df = annual_avg.join(df_list, sort=False)
                        final_df = joined_df.drop(['ID1', 'ID2', 'ID3', 'ID4', 'ID5'], 1)
                        final_df = pd.DataFrame(final_df)

                        # write the final dataframe
                        final_df.to_csv("{path}\\{name}_dataframe_{index}.csv".format(path=path,
                              name=name, index=str(dataset_index)), index=False)
                        in_table = ("{path}\\{name}_dataframe_{index}.csv".format(path=path,
                              name=name, index=str(dataset_index)))
                        arcpy.MakeFeatureLayer_management(ws_points, 'ws_points_layer{}'.format(
                              dataset_index))           
                        in_features = "ws_points_layer{}".format(str(dataset_index))

                        # join the weather dataframe to the weather stations shapefile
                        in_field = "ID"
                        out_feature = "{path}\\joined_ws_{index}.shp".format(path=path,
                              index=str(dataset_index))

                        # join the feature layer to the table
                        joined_table = arcpy.AddJoin_management(in_features, in_field, in_table, in_field, 
                                    join_type = "KEEP_ALL")

                        # Copy the layer to a new permanent feature class 
                        arcpy.CopyFeatures_management(joined_table, out_feature)
                        arcpy.Delete_management(in_features)

                        # do the interpolation of every crop requirement
                        annual_avg = Idw(out_feature, 'annual_avg', cell_size, idw_power, search_radius, "")
                        winter_avg = Idw(out_feature, "winter_avg", cell_size, idw_power, search_radius, "")
                        flowering_avg = Idw(out_feature, "FlowAvgT", cell_size, idw_power, search_radius, "")
                        avg_flowering_daily_max = Idw(out_feature, "FlowMaxT", cell_size, idw_power, search_radius, "")
                        fruit_growth_max = Idw(out_feature, "FruitMaxT", cell_size, idw_power, search_radius, "")
                        annual_min = Idw(out_feature, "annual_min", cell_size, idw_power, search_radius, "")

                        # do topographic correction
                        if topography:
                              lapse_rate_correction = arcpy.Raster(path + "\\lapse_rate_correction.tif")

                              annual_avg = annual_avg + lapse_rate_correction
                              annual_avg.save("memory/annual_avg")
                              annual_avg = arcpy.Raster("memory/annual_avg")

                              winter_avg = winter_avg + lapse_rate_correction
                              winter_avg.save("memory/winter_avg")
                              winter_avg = arcpy.Raster("memory/winter_avg")

                              flowering_avg = flowering_avg + lapse_rate_correction
                              flowering_avg.save("memory/flowering_avg")
                              flowering_avg = arcpy.Raster("memory/flowering_avg")

                              avg_flowering_daily_max = avg_flowering_daily_max + lapse_rate_correction
                              avg_flowering_daily_max.save("memory/avg_flowering_daily_max")
                              avg_flowering_daily_max = arcpy.Raster("memory/avg_flowering_daily_max")

                              fruit_growth_max = fruit_growth_max + lapse_rate_correction
                              fruit_growth_max.save("memory/fruit_growth_max")
                              fruit_growth_max = arcpy.Raster("memory/fruit_growth_max")

                              annual_min = annual_min + lapse_rate_correction
                              annual_min.save("memory/annual_min")
                              annual_min = arcpy.Raster("memory/annual_min")

                              del lapse_rate_correction
                              

                        # raster reclassification
                        annual_avg = arcpy.sa.Con((annual_avg < 12), 0,
                              (arcpy.sa.Con(((annual_avg <= 15) & (annual_avg >= 12)), 0.25, 1)))

                        winter_avg = arcpy.sa.Con((winter_avg <= 5), 0, 1)

                        flowering_avg = arcpy.sa.Con(((flowering_avg < 10) | (flowering_avg > 35)),
                               0, 1)

                        avg_flowering_daily_max = arcpy.sa.Con((avg_flowering_daily_max > 30), 0, 1)

                        fruit_growth_max = arcpy.sa.Con((fruit_growth_max >= 42), 0,
                              (arcpy.sa.Con(((fruit_growth_max < 42) & (fruit_growth_max >= 40)),
                                     0.25, 1)))

                        annual_min = arcpy.sa.Con((annual_min <= -2), 0,
                                                (arcpy.sa.Con(((annual_min > -2) & (annual_min <= 0)), 
                                                      0.25, 1)))

                        # produce Avocado suitability map (provisional)
                        suitability = annual_avg * winter_avg * flowering_avg\
                              * avg_flowering_daily_max * fruit_growth_max *\
                                    annual_min
                        arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                              name=name, num=str(dataset_index)))
