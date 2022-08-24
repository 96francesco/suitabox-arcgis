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

      # general settings
      separator = locale.localeconv()["decimal_point"]
      path = arcpy.env.workspace + "\\"

      # user inputs
      cultivar = arcpy.GetParameterAsText(1) # cultivar
      mask_area = arcpy.GetParameterAsText(2) # area of study 
      ws_points = arcpy.GetParameterAsText(3) # points shapefile of the weather stations
      topography = arcpy.GetParameterAsText(5) # digital elevation model

      budding_period = arcpy.GetParameterAsText(7) # custom budding period
      flowering_period = arcpy.GetParameterAsText(8) # custom flowering period
      chilling_period = arcpy.GetParameterAsText(10) # custom chilling accumulation period

      # set custom chilling period if required
      if chilling_period != '-': # use custom period set by user
            chilling_start_doy = int(chilling_period.split("-")[0])
            chilling_end_doy = int(chilling_period.split("-")[1])
            arcpy.AddMessage("Custom period of chilling accumulation: {start}-{end}".format(
                  start=str(chilling_start_doy), end=str(chilling_end_doy)))

      # set the custom flowering period if required
      if flowering_period != '-': # use the custom period set by user
            flowering_start_doy = int(flowering_period.split("-")[0])
            flowering_end_doy = int(flowering_period.split("-")[1])
            arcpy.AddMessage("Custom flowering period: {start}-{end}".format(
                  start=str(flowering_start_doy), end=str(flowering_end_doy)))
      
      #set the custom budding period if required
      if budding_period != '-': # use the custom period set by user
            budding_start_doy = int(budding_period.split("-")[0])
            budding_end_doy = int(budding_period.split("-")[1])
            arcpy.AddMessage("Custom flowering period: {start}-{end}".format(
                  start=str(budding_start_doy), end=str(budding_end_doy)))

      idw_power = int(arcpy.GetParameterAsText(13)) # power to be used in interpolation
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
      else: # use default resolution (100 m)
            cell_size = 100
      
      # define the method
      def kiwifruit_fun():
            """
            This function computes the single years suitability layers for
            the crop species "kiwifruit".
            """
            global dem_difference, lapse_rate_correction
            for file in os.listdir(path):
                  os.chdir(path)
                  if file.startswith("weather_dataset_") or file.startswith("new_dataset"):
                        weather_df = pd.DataFrame(pd.read_csv(file, error_bad_lines=False))
                        dataset_name = os.path.basename(path + str(file))
                        dataset_index = dataset_name.replace(".", "_").split("_")[2]
                        weather_df.columns = weather_df.columns.str.strip()

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
                        
                        # calculate the minimum temperature when there are still fruits 
                        # on the trees (01 Oct - 15 Nov)
                        fall_df = weather_df.loc[(weather_df['doy'] >= 274) &
                              (weather_df['doy'] <= 320)]
                        fall_df = pd.DataFrame(fall_df)
                        fall_min = fall_df.groupby('ID', as_index=False)['Tair'].min()
                        fall_min = pd.DataFrame(fall_min)
                        fall_min.columns = ["ID1", "fall_min"]

                        # calculate annual maximum temperature
                        annual_max = weather_df.groupby('ID', as_index=False)['Tair'].max()
                        annual_max = pd.DataFrame(annual_max)
                        annual_max.columns = ["ID2", "annual_max"]

                        # calculate the minimum temperature during flowering
                        if flowering_period != '-': # use the custom period set by user
                              flowering_df = weather_df.loc[(weather_df['doy'] >= flowering_start_doy) &
                                    (weather_df['doy'] <= flowering_end_doy)]
                              flowering_df = pd.DataFrame(flowering_df)
                              flowering_frost = flowering_df.groupby('ID', as_index=False)['Tair'].min()
                              flowering_frost = pd.DataFrame(flowering_frost)
                              flowering_frost.columns = ["ID3", "FrostFlow"]
                        elif flowering_period == '-': # use default period (01/05 - 31/05)
                              flowering_df = weather_df.loc[(weather_df['doy'] >= 121) &
                                    (weather_df['doy'] <= 151)]
                              flowering_df = pd.DataFrame(flowering_df)
                              flowering_frost = flowering_df.groupby('ID', as_index=False)['Tair'].min()
                              flowering_frost = pd.DataFrame(flowering_frost)
                              flowering_frost.columns = ["ID3", "FrostFlow"]
                              
                        # calculate the minimum temperature during vegetation budding
                        if budding_period != '-': # use the custom period set by user
                              budding_df = weather_df.loc[(weather_df['doy'] >= budding_start_doy) &
                                    (weather_df['doy'] <= budding_end_doy)]
                              budding_df = pd.DataFrame(budding_df)
                              budding_frost = budding_df.groupby('ID', as_index=False)['Tair'].min()
                              budding_frost = pd.DataFrame(budding_frost)
                              budding_frost.columns = ["ID4", "FrostBuds"]
                        elif budding_period == '-': # use default period (01/03 - 31/05)
                              budding_df = weather_df.loc[(weather_df['doy'] >= 60) & 
                                    (weather_df['doy'] <= 151)]
                              budding_df = pd.DataFrame(budding_df)
                              budding_frost = budding_df.groupby('ID', as_index=False)['Tair'].min()
                              budding_frost = pd.DataFrame(budding_frost)
                              budding_frost.columns = ["ID4", "FrostBuds"]
                              

                        # join the dataframes
                        df_list = [fall_min, annual_max, flowering_frost, budding_frost]
                        joined_df = chilling_hours.join(df_list, sort=False)
                        final_df = joined_df.drop(['ID1', 'ID2', 'ID3', 'ID4'], 1)

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
                        fall_min = Idw(out_feature, "fall_min", cell_size, idw_power, search_radius, "")
                        annual_max = Idw(out_feature, "annual_max", cell_size, idw_power, search_radius, "")
                        flowering_frost = Idw(out_feature, "FrostFlow", cell_size, idw_power, search_radius, "")
                        budding_frost = Idw(out_feature, "FrostBuds", cell_size, idw_power, search_radius, "")

                        # topographic correction
                        if topography:
                              dem_difference = arcpy.Raster(path + "\\dem_difference.tif")
                              lapse_rate_correction = arcpy.Raster(path + "\\lapse_rate_correction.tif")

                              chill_h = arcpy.sa.Con((dem_difference >= -400), 
                                    chill_h - (-0.0032 * (dem_difference)**2), chill_h)
                              arcpy.gp.ExtractByMask_sa(chill_h, mask_area,
                                    "{}\\chill_h.tif".format(path))
                              chill_h = arcpy.Raster("{}\\chill_h.tif".format(path))

                              fall_min = fall_min + lapse_rate_correction
                              fall_min.save("memory/fall_min")
                              fall_min = arcpy.Raster("memory/fall_min")

                              annual_max = annual_max + lapse_rate_correction
                              annual_max.save("memory/annual_max")
                              annual_max = arcpy.Raster("memory/annual_max")

                              flowering_frost = flowering_frost + lapse_rate_correction
                              flowering_frost.save("memory/flowering_frost")
                              flowering_frost = arcpy.Raster("memory/flowering_frost")

                              budding_frost = flowering_frost + lapse_rate_correction
                              budding_frost.save("memory/budding_frost")
                              budding_frost = arcpy.Raster("memory/budding_frost")

                              del dem_difference, lapse_rate_correction

                        # raster reclassification
                        fall_min = arcpy.sa.Con((fall_min <= -1), 0,
                              (arcpy.sa.Con(((fall_min < 0) & (fall_min > -1)), 0.25, 1)))

                        annual_max = arcpy.sa.Con((annual_max > 40), 0, 1)

                        flowering_frost = arcpy.sa.Con((flowering_frost <= -3), 0,
                              (arcpy.sa.Con(((flowering_frost > -3) & (flowering_frost <= -2)), 0.25,
                                    (arcpy.sa.Con(((flowering_frost > -2) & (flowering_frost <= -1)), 
                                                0.75, 1)))))
                        
                        budding_frost = arcpy.sa.Con((flowering_frost <= -2), 0,
                              (arcpy.sa.Con(((flowering_frost > -2) & (flowering_frost <= -1.5)), 0.25,
                                    (arcpy.sa.Con(((flowering_frost > -1.5) & (flowering_frost <= 0)),
                                                0.75, 1)))))

                        if cultivar == 'Hayward' :
                              # chilling hours reclassification
                              chill_h = arcpy.sa.Con((chill_h < 768), 0, 1)

                              # produce Kiwifruit - cv Hayward suitability map (provisional)
                              suitability = annual_max * fall_min * flowering_frost \
                                    * budding_frost * chill_h
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

                        elif cultivar == 'Donghong':
                              # reclassification according to the vegetative budbreak requirements
                              chill_h_vegetation = arcpy.sa.Con((chill_h < 222), 0, 1)

                              # reclassification of the chilling hours according to the flowering requirements
                              chill_h_flowers = arcpy.sa.Con((chill_h < 655), 0, 1)

                              # produce Kiwifruit - cv Hayward suitability map (provisional)
                              suitability = annual_max * fall_min * flowering_frost \
                                    * budding_frost * chill_h_flowers * chill_h_vegetation
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

                        elif cultivar == 'Jintao':
                              # reclassification according to the vegetative budbreak requirements
                              chill_h_vegetation = arcpy.sa.Con((chill_h < 776), 0, 1)

                              # reclassification of the chilling hours according to the flowering requirements
                              chill_h_flowers = arcpy.sa.Con((chill_h < 1013), 0, 1)

                              # produce Kiwifruit - cv Hayward suitability map (provisional)
                              suitability = annual_max * fall_min * flowering_frost \
                                    * budding_frost * chill_h_flowers * chill_h_vegetation
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

                        elif cultivar == 'Jinyan':
                              chill_h = arcpy.sa.Con((chill_h < 720), 0, 1)

                              # produce Kiwifruit - cv Jinyan suitability map (provisional)
                              suitability = annual_max * chill_h * budding_frost \
                                    * flowering_frost * fall_min
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

                        elif cultivar == 'Hort 16A':
                              chill_h = arcpy.sa.Con((chill_h < 528), 0,
                                    (arcpy.sa.Con(((chill_h >= 528) & (chill_h < 600)), 0.75, 1)))

                              # produce Kiwifruit - cv Jinyan suitability map (provisional)
                              suitability = annual_max * chill_h * budding_frost \
                                    * flowering_frost * fall_min
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

                        elif cultivar == 'Golden Sunshine' :
                              # reclassification according to the vegetative budbreak requirements
                              chill_h_vegetation = arcpy.sa.Con((chill_h < 500), 0,
                                    (arcpy.sa.Con(((chill_h >= 500) & (chill_h < 600)), 0.25,
                                    (arcpy.sa.Con(((chill_h >= 600) & (chill_h < 700)), 0.75, 1)))))

                              # reclassification of the chilling hours according to the flowering requirements
                              chill_h_flowers = arcpy.sa.Con((chill_h < 700), 0,
                                    (arcpy.sa.Con(((chill_h >= 700) & (chill_h < 800)), 0.25,
                                    (arcpy.sa.Con(((chill_h >= 800) & (chill_h < 900)), 0.75, 1)))))

                              # produce Kiwifruit - cv Golden sunshine suitability map (provisional)
                              suitability = annual_max * chill_h_vegetation * chill_h_flowers \
                                    * budding_frost * flowering_frost * fall_min
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

                        elif cultivar == 'Golden Dragon' :
                              # reclassification of the chilling hours
                              chill_h = arcpy.sa.Con((chill_h < 600), 0,
                                    (arcpy.sa.Con(((chill_h >= 600) & (chill_h < 700)), 0.25,
                                    (arcpy.sa.Con(((chill_h >= 700) & (chill_h < 800)), 0.75, 1)))))

                              # produce Kiwifruit - cv Golden Dragon suitability map (provisional)
                              suitability = annual_max * chill_h * budding_frost \
                                    * flowering_frost * fall_min
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

                        elif cultivar == "Hongyang":
                              # reclassification of the chilling hours
                              chill_h = arcpy.sa.Con((chill_h < 600), 0,
                                    (arcpy.sa.Con(((chill_h >= 600) & (chill_h < 700)), 0.75, 1)))

                              # produce Kiwifruit - cv Hongyang suitability map (provisional)
                              suitability = annual_max * chill_h * budding_frost \
                                    * flowering_frost * fall_min
                              arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}\\{name}_{num}.tif".format(path=path, 
                                    name=name, num=str(dataset_index)))

                              # remove bindings
                              del chill_h
            
            return 
      