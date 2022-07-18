"""
This file is part of Suitabox.

Suitabox is free software: you can redistribute it and/or modify it under the terms of 
the GNU General Public License as published by the Free Software Foundation, either 
version 3 of the License, or (at your option) any later version.

Suitabox is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Suitabox. 
If not, see <https://www.gnu.org/licenses/>.
"""

if __name__ == "__main__":
      pass
else:
      # imports
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

      growing_period = arcpy.GetParameterAsText(6) # custom growing season
      chilling_period = arcpy.GetParameterAsText(10) # custom chilling accumulation period

      # set custom chilling period if required
      if chilling_period != '-': # use custom period set by user
            chilling_start_doy = int(chilling_period.split("-")[0])
            chilling_end_doy = int(chilling_period.split("-")[1])
            arcpy.AddMessage("Custom period of chilling accumulation: {start}-{end}".format(
                  start=str(chilling_start_doy), end=str(chilling_end_doy)))

      # set custom growing season if required
      if growing_period != "-":
            growing_start_doy = int(growing_period.split("-")[0])
            growing_end_doy = int(growing_period.split("-")[1])
            arcpy.AddMessage("Custom growing period: {start}-{end}".format(
                  start=str(growing_start_doy), end=str(growing_end_doy)))

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

      name = arcpy.GetParameterAsText(18) # output name

      if topography:
            spatial_resolution = str(arcpy.GetRasterProperties_management(topography, "CELLSIZEX"))
            cell_size = int(spatial_resolution.split(separator)[0])
      else:
            cell_size = 100

      def walnut_fun():
            """
            This function computes the single years suitability layers for
            the crop species "walnut".
            """
            global dem_difference, lapse_rate_correction
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

                        # calculate average temperature during growth season
                        if growing_period != '-': # use the custom period set by user 
                              growing_df = weather_df.loc[(weather_df['doy'] >= growing_start_doy) &
                                    (weather_df['doy'] <= growing_end_doy)]
                              growing_df = pd.DataFrame(growing_df)
                              growing_avg = growing_df.groupby('ID', as_index=False)['Tair'].mean()
                              growing_avg = pd.DataFrame(growing_avg)
                              growing_avg.columns = ["ID1", "grow_avg"]
                        elif growing_period == '-': # use the default period (01/04 - 31/10)
                              growing_df = weather_df.loc[(weather_df['doy'] >= 91) &
                                    (weather_df['doy'] <= 305)]
                              growing_df = pd.DataFrame(growing_df)
                              growing_avg = growing_df.groupby('ID', as_index=False)['Tair'].mean()
                              growing_avg = pd.DataFrame(growing_avg)
                              growing_avg.columns = ["ID1", "grow_avg"]
                              
                        # calculate the minimum temperature during winter
                        winter_df = weather_df.loc[(weather_df['doy'] >= 335) | 
                              (weather_df['doy'] <= 60)]
                        winter_df = pd.DataFrame(winter_df)
                        winter_min = winter_df.groupby('ID', as_index=False)['Tair'].min()
                        winter_min = pd.DataFrame(winter_min)
                        winter_min.columns = ["ID2", "winter_min"]
                                                      
                        # calculate the maximum temperature during the whole year
                        annual_max = weather_df.groupby('ID', as_index=False)['Tair'].max()
                        annual_max = pd.DataFrame(annual_max)
                        annual_max.columns = ["ID3", "annual_max"]

                        # join the dataframes
                        df_list = [growing_avg, winter_min, annual_max]
                        joined_df = chilling_hours.join(df_list, sort=False)
                        final_df = joined_df.drop(["ID1", "ID2", "ID3"], 1)

                        # write the final dataframe
                        final_df.to_csv("{path}{name}_dataframe_{index}.csv".format(path=path,
                              name=name, index=str(dataset_index)), index=False)
                        in_table = ("{path}{name}_dataframe_{index}.csv".format(path=path,
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
                        growing_avg = Idw(out_feature, "grow_avg", cell_size, idw_power, search_radius, "")
                        winter_min = Idw(out_feature, "winter_min", cell_size, idw_power, search_radius, "")
                        annual_max = Idw(out_feature, "annual_max", cell_size, idw_power, search_radius, "")

                        # do topographic correction
                        if topography:
                              dem_difference = arcpy.Raster(path + "\\dem_difference.tif")
                              lapse_rate_correction = arcpy.Raster(path + "\\lapse_rate_correction.tif")
                              
                              chill_h = arcpy.sa.Con((dem_difference >= -400), 
                                    chill_h - (-0.0032 * (dem_difference)**2), chill_h)
                              arcpy.gp.ExtractByMask_sa(chill_h, mask_area,
                                    "{}\\chill_h.tif".format(path))
                              chill_h = arcpy.Raster("{}\\chill_h.tif".format(path))

                              growing_avg = growing_avg + lapse_rate_correction
                              growing_avg.save("memory/growing_avg")
                              growing_avg = arcpy.Raster("memory/growing_avg")

                              winter_min = winter_min + lapse_rate_correction
                              winter_min.save("memory/winter_min")
                              winter_min = arcpy.Raster("memory/winter_min")

                              annual_max = annual_max + lapse_rate_correction
                              annual_max.save("memory/annual_max")
                              annual_max = arcpy.Raster("memory/annual_max")

                              del dem_difference, lapse_rate_correction

                        # raster reclassification
                        growing_avg = arcpy.sa.Con(((growing_avg < 15) & (growing_avg > 28)), 0,
                              (arcpy.sa.Con(((growing_avg >= 15) & (growing_avg < 18)), 0.25,
                                    (arcpy.sa.Con(((growing_avg >= 18) & (growing_avg < 20)), 0.75, 1)))))

                        winter_min = arcpy.sa.Con((winter_min < -20), 0,
                              (arcpy.sa.Con(((winter_min > -20) & (winter_min < -15)), 0.25,
                                    (arcpy.sa.Con(((winter_min > -15) & (winter_min < -5)), 0.75, 1)))))

                        annual_max = arcpy.sa.Con((annual_max > 38), 0,
                              (arcpy.sa.Con(((annual_max <= 38) & (annual_max > 35)), 0.25,
                                    (arcpy.sa.Con(((annual_max <= 35) & (annual_max >= 30)), 0.75, 1)))))

                        # reclassification of the chilling hours, in according with the cultivar requirements
                        if cultivar == 'Serr':
                              # reclassification according to the vegetative budbreak requirements
                              chill_h_vegetation = arcpy.sa.Con((chill_h < 650), 0,
                                    (arcpy.sa.Con(((chill_h >= 650) & (chill_h < 1000)), 0.75, 1)))

                              # reclassification in according to the flowering requirements
                              chill_h_flowers = arcpy.sa.Con((chill_h < 450), 0,
                                    (arcpy.sa.Con(((chill_h >= 450) & (chill_h < 1000)), 0.75, 1)))

                              # produce Walnut - cv Serr suitability map (provisional)
                              suitability = annual_max * growing_avg * winter_min *\
                                    chill_h_vegetation * chill_h_flowers
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, path + "\\" + name + "_Suit_" +\
                                    str(dataset_index) + ".tif")

                        elif cultivar == 'Lara':
                              # reclassification according to the vegetation budbreak requirements
                              chill_h_vegetation = arcpy.sa.Con((chill_h < 900), 0,
                                    (arcpy.sa.Con(((chill_h >= 900) & (chill_h < 1000)), 0.75, 1)))

                              # reclassification in according to the flowering requirements
                              chill_h_flowers = arcpy.sa.Con((chill_h < 750), 0,
                                    (arcpy.sa.Con(((chill_h >= 750) & (chill_h < 1100)), 0.75, 1)))

                              # produce Walnut - cv Lara suitability map (provisional)
                              suitability = annual_max * growing_avg * winter_min * chill_h_vegetation\
                                    * chill_h_flowers
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, path + "\\" + name + "_" +\
                                    str(dataset_index) + ".tif")
                              
                        elif cultivar == 'Pedro':
                              # reclassification according to lateral vegetation budbreak requirements
                              chill_h_lateral_veg = arcpy.sa.Con((chill_h < 750), 0,
                                    (arcpy.sa.Con(((chill_h >= 750) & (chill_h < 1300)), 0.75, 1)))

                              # reclassification according to the terminal vegetation budbreak
                              chill_h_terminal_veg = arcpy.sa.Con((chill_h < 600), 0,
                                    (arcpy.sa.Con(((chill_h >= 600) & (chill_h < 1300)), 0.75, 1)))

                              # reclassification according to flowering requirements
                              chill_h_flowers = arcpy.sa.Con((chill_h < 600), 0,
                                    (arcpy.sa.Con(((chill_h >= 600) & (chill_h < 1300)), 0.75, 1)))

                              # produce Walnut - cv Pedro suitability map (provisional)
                              suitability = annual_max * growing_avg * winter_min *\
                                    chill_h_terminal_veg * chill_h_lateral_veg * chill_h_flowers 
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, path + "\\" + name + "_" +\
                                    str(dataset_index) + ".tif")
                              
                        elif cultivar == 'Hartley':
                              # reclassification according to lateral vegetation budbreak requirements
                              chill_h_lateral_veg = arcpy.sa.Con((chill_h < 1000), 0,
                                    (arcpy.sa.Con(((chill_h >= 1000) & (chill_h < 1400)), 0.75, 1)))

                              # reclassification according to the terminal vegetation budbreak
                              chill_h_terminal_veg = arcpy.sa.Con((chill_h < 950), 0,
                                    (arcpy.sa.Con(((chill_h >= 950) & (chill_h < 1400)), 0.75, 1)))

                              # reclassification according to flowering requirements
                              chill_h_flowers = arcpy.sa.Con((chill_h < 750), 0,
                                    (arcpy.sa.Con(((chill_h >= 750) & (chill_h < 1400)), 0.75, 1)))

                              # produce Walnut - cv Pedro suitability map (provisional)
                              suitability = annual_max * growing_avg * winter_min *\
                                    chill_h_terminal_veg * chill_h_lateral_veg * chill_h_flowers
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, path + "\\" + name + "_" +\
                                    str(dataset_index) + ".tif")
                              
                        elif cultivar == 'Chandler':
                              ChillHours_reclass = arcpy.sa.Con((chill_h < 1015), 0, 1)

                              # produce Walnut - cv Chandler suitability map (provisional)
                              suitability = annual_max * growing_avg * winter_min *\
                                    ChillHours_reclass
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, path + "\\" + name + "_" +\
                                    str(dataset_index) + ".tif")
            return
