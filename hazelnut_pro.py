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
      import arcpy
      from arcpy.sa import *
      import pandas as pd
      import os
      import locale

      separator = locale.localeconv()["decimal_point"]
      path = arcpy.env.workspace + "\\"

      # user inputs
      cultivar = arcpy.GetParameterAsText(1) # cultivar
      mask_area = arcpy.GetParameterAsText(2) # area of study 
      ws_points = arcpy.GetParameterAsText(3) # points shapefile of the weather stations
      topography = arcpy.GetParameterAsText(5) # digital elevation model

      chilling_period = arcpy.GetParameterAsText(10) # custom chilling accumulation period

      idw_power = int(arcpy.GetParameterAsText(13)) # idw_power to be used in interpolation
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

      # set custom chilling period if required
      if chilling_period != '-': # use custom period set by user
            chilling_start_doy = int(chilling_period.split("-")[0])
            chilling_end_doy = int(chilling_period.split("-")[1])
            arcpy.AddMessage("Custom period of chilling accumulation: {start}-{end}".format(
                  start=str(chilling_start_doy), end=str(chilling_end_doy)))

      name = arcpy.GetParameterAsText(18) # output name

      # if topography exists, set the spatial resolution (the same of DEM)
      if topography:
            spatial_resolution = str(arcpy.GetRasterProperties_management(topography, "CELLSIZEX"))
            cell_size = int(spatial_resolution.split(separator)[0])
      else: # use default resolution (100 m)
            cell_size = 100

      def hazelnut_fun():
            """
            This function computes the single years suitability layers for
            the crop species "hazelnut".
            """
            global lapse_rate_correction
            for file in os.listdir(path):
                  os.chdir(path)
                  if file.startswith("weather_dataset_") or file.startswith("new_dataset_"):
                        weather_df = pd.DataFrame(pd.read_csv(file, error_bad_lines=False))
                        dataset_name = os.path.basename(path + str(file))
                        dataset_index = dataset_name.replace(".", "_").split("_")[2]

                        if chilling_period != '-': # use custom period set by user
                              chilling_df = weather_df.loc[(weather_df['doy'] >= chilling_start_doy) |
                                          (weather_df['doy'] <= chilling_end_doy)]
                              chilling_df = pd.DataFrame(chilling_df)
                              chilling_df = chilling_df.loc[(chilling_df['Tair'] < 7.2) &
                                          (chilling_df['Tair'] > 0)]
                              chilling_df = pd.DataFrame(chilling_df)
                              chilling_hours = chilling_df.groupby("ID", as_index=False)["Tair"].count()
                              chilling_hours = pd.DataFrame(chilling_hours)
                              chilling_hours.columns = ["ID", "chill_h"]
                        elif chilling_period == '-': # use default period (01/10 - 15/02)
                              chilling_df = weather_df.loc[(weather_df['doy'] >= 274) |
                                          (weather_df['doy'] <= 46)]
                              chilling_df = pd.DataFrame(chilling_df)
                              chilling_df = chilling_df.loc[(chilling_df['Tair'] < 7.2) &
                                          (chilling_df['Tair'] > 0)]
                              chilling_df = pd.DataFrame(chilling_df)
                              chilling_hours = chilling_df.groupby("ID", as_index=False)["Tair"].count()
                              chilling_hours = pd.DataFrame(chilling_hours)
                              chilling_hours.columns = ["ID", "chill_h"]

                        # calculate average annual temperature
                        annual_avg = weather_df.groupby("ID", as_index=False)['Tair'].mean()
                        annual_avg = pd.DataFrame(annual_avg)
                        annual_avg.columns = ["ID1", "annual_avg"]

                        # calculate max annual temperature
                        annual_max = weather_df.groupby('ID', as_index=False)['Tair'].max()
                        annual_max = pd.DataFrame(annual_max)
                        annual_max.columns = ["ID2", "annual_max"]

                        # frost
                        frost_df = weather_df.loc[(weather_df["doy"] >= 60) &
                              (weather_df["doy"] <= 121)]
                        frost_df = pd.DataFrame(frost_df)
                        frost = frost_df.groupby("ID", as_index=False)["Tair"].min()
                        frost = pd.DataFrame(frost)
                        frost.columns = ["ID3", "frost"]

                        # monthly average maximum temperature in summer_df
                        summer_df = weather_df.loc[(weather_df["doy"] >= 152) &
                              (weather_df["doy"] <= 244)]
                        summer_df = pd.DataFrame(summer_df)
                        summer_max = summer_df.groupby("ID", as_index=False)["Tair"].max()
                        summer_max = pd.DataFrame(summer_max)
                        summer_max.columns = ["ID", "Tmax"]
                        avg_max = summer_max.groupby("ID", as_index=False)["Tmax"].mean()
                        avg_max = pd.DataFrame(avg_max)
                        avg_max.columns = ["ID4", "avg_max"]

                        # join the dataframes
                        df_list = [annual_avg, annual_max, frost, avg_max]
                        joined_df = chilling_hours.join(df_list, sort=False)
                        final_df = joined_df.drop(["ID1", "ID2", "ID3", "ID4"], 1)

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

                        # interpolation
                        chill_h = Idw(out_feature, "chill_h", cell_size, idw_power, search_radius, "")
                        annual_avg = Idw(out_feature, "annual_avg", cell_size, idw_power, search_radius, "")
                        annual_max = Idw(out_feature, "annual_max", cell_size, idw_power, search_radius, "")
                        frost = Idw(out_feature, "frost", cell_size, idw_power, search_radius, "")
                        avg_max = Idw(out_feature, "avg_max", cell_size, idw_power, search_radius, "")

                        # do the topographic correction
                        if topography:
                              dem_difference = arcpy.Raster(path + "\\dem_difference.tif")
                              lapse_rate_correction = arcpy.Raster(path + "\\lapse_rate_correction.tif")
                              
                              chill_h = arcpy.sa.Con((dem_difference >= -400), 
                                    chill_h - (-0.0032 * (dem_difference)**2), chill_h)
                              arcpy.gp.ExtractByMask_sa(chill_h, mask_area,
                                    "{}\\chill_h.tif".format(path))
                              chill_h = arcpy.Raster("{}\\chill_h.tif".format(path))

                              annual_avg = annual_avg + lapse_rate_correction
                              annual_avg.save("memory/annual_avg")
                              annual_avg = arcpy.Raster("memory/annual_avg")

                              annual_max = annual_max + lapse_rate_correction
                              annual_max.save("memory/annual_max")
                              annual_max = arcpy.Raster("memory/annual_max")

                              frost = frost + lapse_rate_correction
                              frost.save("memory/frost")
                              frost = arcpy.Raster("memory/frost")

                              avg_max = avg_max + lapse_rate_correction
                              avg_max.save("memory/avg_MaxT_corrext")
                              avg_max = arcpy.Raster("memory/avg_MaxT_corrext")

                              del dem_difference, lapse_rate_correction

                        # raster reclassification
                        annual_avg = arcpy.sa.Con(((annual_avg < 12) & (annual_avg > 16)), 0,
                              (arcpy.sa.Con(((annual_avg > 13.5) & (annual_avg < 14.5)), 1, 0.75)))
            
                        annual_max = arcpy.sa.Con((annual_max > 36), 0,
                              arcpy.sa.Con((annual_max < 35), 1, 0.25))

                        frost = arcpy.sa.Con((frost <= -3), 0, 1)

                        avg_max = arcpy.sa.Con(((avg_max > 35) | (avg_max < 18)), 0,
                              (arcpy.sa.Con(((avg_max < 35) & (avg_max >= 33)), 0.25,
                                    (arcpy.sa.Con(((avg_max < 33) & (avg_max >= 30)), 0.75, 
                                          1)))))
                        
                        if cultivar == "Tonda di Giffoni":
                              # catkins chilling requirement
                              chill_h_catkins = arcpy.sa.Con((chill_h < 170), 0,
                                    (arcpy.sa.Con(((chill_h >= 170) & (chill_h < 200)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 200) & (chill_h <= 240)), 0.75, 
                                                1)))))

                              # female flowers chilling requirement
                              chill_h_flowers = arcpy.sa.Con((chill_h < 600), 0,
                                    (arcpy.sa.Con(((chill_h >= 600) & (chill_h < 640)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 640) & (chill_h <= 680)), 0.75, 
                                                1)))))
                              
                              # leaf buds chilling requirement
                              chill_h_buds = arcpy.sa.Con((chill_h < 600), 0,
                                    (arcpy.sa.Con(((chill_h >= 600) & (chill_h < 640)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 640) & (chill_h <= 680)), 0.75, 
                                                1)))))

                              # produce European hazelnut - cv Tonda di Giffoni suitability map (provisional)
                              suitability = annual_avg * annual_max * frost *\
                                    avg_max * chill_h_catkins * chill_h_flowers * chill_h_buds
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

                        elif cultivar == "Camponica":
                              # catkins chilling requirement
                              chill_h_catkins = arcpy.sa.Con((chill_h < 170), 0,
                                    (arcpy.sa.Con(((chill_h >= 170) & (chill_h < 200)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 200) & (chill_h <= 240)), 0.75, 
                                                1)))))

                              # female flowers chilling requirement
                              chill_h_flowers = arcpy.sa.Con((chill_h < 290), 0,
                                    (arcpy.sa.Con(((chill_h >= 290) & (chill_h < 327)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 327) & (chill_h <= 365)), 0.75, 
                                                1)))))

                              # leaf buds chilling requirement
                              chill_h_buds = arcpy.sa.Con((chill_h < 680), 0,
                                    (arcpy.sa.Con(((chill_h >= 680) & (chill_h < 720)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 720) & (chill_h <= 760)), 0.75, 
                                                1)))))

                              # produce cv Camponica suitability map (provisional)
                              suitability = annual_avg * annual_max * frost *\
                                    avg_max * chill_h_catkins * chill_h_flowers * chill_h_buds
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

                        elif cultivar == "Negret":
                              # catkins chilling requirement
                              chill_h_catkins = arcpy.sa.Con((chill_h < 240), 0,
                                    (arcpy.sa.Con(((chill_h >= 240) & (chill_h < 265)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 265) & (chill_h <= 290)), 0.75, 
                                                1)))))

                              # female flowers chilling requirement
                              chill_h_flowers = arcpy.sa.Con((chill_h < 480), 0,
                                    (arcpy.sa.Con(((chill_h >= 480) & (chill_h < 540)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 540) & (chill_h <= 600)), 0.75, 
                                                1)))))

                              # leaf buds chilling requirement
                              chill_h_buds = arcpy.sa.Con((chill_h < 760), 0,
                                    (arcpy.sa.Con(((chill_h >= 760) & (chill_h < 810)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 810) & (chill_h <= 860)), 0.75, 
                                                1)))))

                              # produce cv Negret suitability map (provisional)
                              suitability = annual_avg * annual_max * frost *\
                                    avg_max * chill_h_catkins * chill_h_flowers * chill_h_buds
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

                        elif cultivar == "Barcelona":
                              # catkins chilling requirement
                              chill_h_catkins = arcpy.sa.Con((chill_h < 240), 0,
                                    (arcpy.sa.Con(((chill_h >= 240) & (chill_h < 265)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 265) & (chill_h <= 290)), 0.75, 
                                                1)))))

                              # female flowers chilling requirement
                              chill_h_flowers = arcpy.sa.Con((chill_h < 600), 0,
                                    (arcpy.sa.Con(((chill_h >= 600) & (chill_h < 640)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 640) & (chill_h <= 680)), 0.75, 
                                                1)))))

                              # leaf buds chilling requirement
                              chill_h_buds = arcpy.sa.Con((chill_h < 990), 0,
                                    (arcpy.sa.Con(((chill_h >= 990) & (chill_h < 1015)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 1015) & (chill_h <= 1040)), 0.75, 
                                                1)))))

                              # produce cv Barcelona suitability map (provisional)
                              suitability = annual_avg * annual_max * frost *\
                                    avg_max * chill_h_catkins * chill_h_flowers * chill_h_buds
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

                        elif cultivar == "Tonda Romana":
                              # catkins chilling requirement
                              chill_h_catkins = arcpy.sa.Con((chill_h < 100), 0,
                                    (arcpy.sa.Con(((chill_h >= 100) & (chill_h < 135)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 135) & (chill_h <= 170)), 0.75, 
                                                1)))))

                              # female flowers chilling requirement
                              chill_h_flowers = arcpy.sa.Con((chill_h < 760), 0,
                                    (arcpy.sa.Con(((chill_h >= 760) & (chill_h < 810)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 810) & (chill_h <= 860)), 0.75, 
                                                1)))))

                              # leaf buds chilling requirement
                              chill_h_buds = arcpy.sa.Con((chill_h < 1040), 0,
                                    (arcpy.sa.Con(((chill_h >= 1040) & (chill_h < 1105)), 0.25,
                                          (arcpy.sa.Con(((chill_h >= 1105) & (chill_h <= 1170)), 0.75, 
                                                1)))))

                              # produce cv Tonda Romana suitability map (provisional)
                              suitability = annual_avg * annual_max * frost *\
                                    avg_max * chill_h_catkins * chill_h_flowers * chill_h_buds
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

            return
