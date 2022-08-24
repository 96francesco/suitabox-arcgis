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
      import numpy

      separator = locale.localeconv()["decimal_point"]
      path = arcpy.env.workspace + "\\"
      
      pathname = os.path.realpath(__file__)
      pathname = pathname.split("custom")[0]

      # user inputs
      mask_area = arcpy.GetParameterAsText(2) # area of study 
      ws_points = arcpy.GetParameterAsText(3) # points shapefile of the weather stations
      topography = arcpy.GetParameterAsText(5) # digital elevation model

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
            SpatialResolution = str(arcpy.GetRasterProperties_management(topography, "CELLSIZEX"))
            cellSize = int(SpatialResolution.split(separator)[0])
      else: # use default resolution (100 m)
            cellSize = 100

      def custom_crop_fun():
            """
            This function computes the single years suitability layers for
            the Custom Crop option.
            """
            global lapse_rate_correction

            # upload and convert parameter file to dictionary
            params = pd.DataFrame(pd.read_csv(pathname + "custom_params.csv", error_bad_lines=False))
            d = params.set_index("param_ID").T.to_dict("list")

            for file in os.listdir(path):
                  os.chdir(path)
                  if file.startswith("weather_dataset_") or file.startswith("new_dataset"):
                        weather_df = pd.DataFrame(pd.read_csv(file, error_bad_lines=False))
                        dataset_name = os.path.basename(path + str(file))
                        dataset_index = dataset_name.replace(".", "_").split("_")[2]
                        weather_df.columns = weather_df.columns.str.strip()

                        counter = 0
                        df_list = []
                        for i in d:
                              param_vars = d.get(i)
                              function = param_vars[1]
                              doys = param_vars[2]
                              
                              # create the variable 'period'
                              doy_start = int(doys.split("-")[0])
                              doy_end = int(doys.split("-")[1])
                              if doy_start < doy_end:
                                    period = weather_df.loc[(weather_df['doy'] >= doy_start)
                                                            & (weather_df['doy'] <= doy_end)]
                              elif doy_start > doy_end:
                                    period = weather_df.loc[(weather_df['doy'] >= doy_start)
                                                            | (weather_df['doy'] <= doy_end)]
                              period = pd.DataFrame(period)
                              
                              # create the param dataframe
                              if function == "mean":
                                    param = period.groupby("ID", as_index=False)["Tair"].mean()
                              elif function == "max":
                                    param = period.groupby("ID", as_index=False)["Tair"].max()
                              elif function == "min":
                                    param = period.groupby("ID", as_index=False)["Tair"].min()
                              elif function.startswith("avg_daily"):
                                    if function.endswith("_min"):
                                          temp_param = period.groupby(["ID", "doy"], as_index=False)["Tair"].min()
                                    elif function.endswith("_max"):
                                          temp_param = period.groupby(["ID", "doy"], as_index=False)["Tair"].max()
                                    temp_param = pd.DataFrame(temp_param)
                                    temp_param.columns = ["ID", "doy", "Tair"]
                                    param = temp_param.groupby("ID", as_index=False)["Tair"].mean()
                              elif function == "chill_hours":
                                    chilling_df = period.loc[(period["Tair"] < 7.2) &
                                                      (period["Tair"] > 0)]
                                    chilling_df = pd.DataFrame(chilling_df)
                                    param = chilling_df.groupby("ID", as_index=False)["Tair"].count()
                              
                              param = pd.DataFrame(param)
                              if function == "chill_hours":
                                    param.columns = ["ID{}".format(str(counter)), "chill_{}".format(
                                          str(counter))]
                              else:
                                    param.columns = ["ID{}".format(str(counter)), "param{}".format(
                                          str(counter))]
                              df_list.append(param)
                              param.to_csv("{path}\\param_{num}_df.csv".format(path=path, num=counter))
                              counter += 1

                        # join the dataframes
                        first_df = df_list.pop(0)
                        first_df.rename(columns={"ID0": "ID"}, inplace=True)

                        col_list = []
                        for df in df_list:
                              col = list(df.columns)[0]
                              col_list.append(col)

                        joined_df = first_df.join(df_list, sort=False)
                        final_df = joined_df.drop(col_list, 1)

                        # write the final dataframe
                        final_df.to_csv("{path}\\{name}_dataframe_{index}.csv".format(path=path,
                              name=name, index=str(dataset_index)), index=False)
                        in_table = ("{path}\\{name}_dataframe_{index}.csv".format(path=path,
                              name=name, index=str(dataset_index)))
                        arcpy.MakeFeatureLayer_management(ws_points, 'ws_points_layer{}'.format(
                              dataset_index))           
                        in_features = "ws_points_layer{}".format(str(dataset_index))

                        # join the weather dataframe with the weather stations shapefile
                        in_field = "ID"
                        out_feature = "{path}\\joined_ws_{index}.shp".format(path=path,
                              index=str(dataset_index))

                        # join the feature layer to the table
                        JoinedTable = arcpy.AddJoin_management(in_features, in_field, in_table, in_field, 
                                    join_type = "KEEP_ALL")

                        # Copy the layer to a new permanent feature class 
                        arcpy.CopyFeatures_management(JoinedTable, out_feature)
                        arcpy.Delete_management(in_features)

                        # interpolation
                        param_counter = 0
                        for i in range(1, len(final_df.columns)):
                              field = list(final_df.columns)[i]
                              interpolated_param = Idw(out_feature, field, cellSize, idw_power, 
                                    search_radius, "")
                              
                              # topographic correction
                              if topography:
                                    dem_difference = arcpy.Raster(path + "\\dem_difference.tif")
                                    lapse_rate_correction = arcpy.Raster(path + "\\lapse_rate_correction.tif")
                                    if field.startswith("chill_"):
                                          param_correct = arcpy.sa.Con((dem_difference >= -400),
                                                interpolated_param - (-0.0032 * (dem_difference)**2), interpolated_param)
                                    else:
                                          param_correct = lapse_rate_correction + interpolated_param
                                          param_correct.save("memory/param{}_correct".format(param_counter))
                                          interpolated_param = arcpy.Raster("memory/param{}_correct".format(
                                                param_counter))
                                    del dem_difference, lapse_rate_correction
                              
                              # reclassification
                              data_list = list(params.iloc[param_counter])
                              remap_list = []

                              # unsuitable range
                              if len(data_list[4]) > 1:
                                    if "&" not in data_list[4]:
                                          unsuit_start = numpy.double(data_list[4].split(";")[0].strip())
                                          unsuit_end = numpy.double(data_list[4].split(";")[1].strip())

                                          remap_list.append([unsuit_start, unsuit_end, 0])     
                                    else:
                                          range_1 = data_list[4].split("&")[0].strip()
                                          unsuit_start_1 = numpy.double(range_1.split(";")[0].strip())
                                          unsuit_end_1 = numpy.double(range_1.split(";")[1].strip())
                                          
                                          range_2 = data_list[4].split("&")[1].strip()
                                          unsuit_start_2 = numpy.double(range_2.split(";")[0].strip())
                                          unsuit_end_2 = numpy.double(range_2.split(";")[1].strip())
                                          
                                          remap_list.append([unsuit_start_1, unsuit_end_1, 0])
                                          remap_list.append([unsuit_start_2, unsuit_end_2, 0])
                              else:
                                    pass

                              # marginally suitable range
                              if len(data_list[5]) > 1:
                                    if "&" not in data_list[5]:
                                          marginal_start = numpy.double(data_list[5].split(";")[0].strip())
                                          marginal_end = numpy.double(data_list[5].split(";")[1].strip())

                                          remap_list.append([marginal_start, marginal_end, 1])      
                                    else:
                                          range_1 = data_list[5].split("&")[0].strip()
                                          marginal_start_1 = numpy.double(range_1.split(";")[0].strip())
                                          marginal_end_1 = numpy.double(range_1.split(";")[1].strip())
                                          
                                          range_2 = data_list[5].split("&")[1].strip()
                                          marginal_start_2 = numpy.double(range_2.split(";")[0].strip())
                                          marginal_end_2 = numpy.double(range_2.split(";")[1].strip())

                                          remap_list.append([marginal_start_1, marginal_end_1, 1])
                                          remap_list.append([marginal_start_2, marginal_end_2, 1])
                              else:
                                    pass

                              # suitable range
                              if len(data_list[6]) > 1:
                                    if "&" not in data_list[6]:
                                          suit_start = numpy.double(data_list[6].split(";")[0].strip())
                                          suit_end = numpy.double(data_list[6].split(";")[1].strip())

                                          remap_list.append([suit_start, suit_end, 2])
                                    else:
                                          range_1 = data_list[6].split("&")[0].strip()
                                          suit_start_1 = numpy.double(range_1.split(";")[0].strip())
                                          suit_end_1 = numpy.double(range_1.split(";")[1].strip())

                                          range_2 = data_list[6].split("&")[1].strip()
                                          suit_start_2 = numpy.double(range_2.split(";")[0].strip())
                                          suit_end_2 = numpy.double(range_2.split(";")[1].strip())
                                          
                                          remap_list.append([suit_start_1, suit_end_1, 2])
                                          remap_list.append([suit_start_2, suit_end_2, 2])
                              else:
                                    pass

                              # highly suitable range
                              if len(data_list[7]) > 1:
                                    if "&" not in data_list[7]:
                                          high_start = numpy.double(data_list[7].split(";")[0].strip())
                                          high_end = numpy.double(data_list[7].split(";")[1].strip())

                                          remap_list.append([high_start, high_end, 3])
                                    else:
                                          range_1 = data_list[7].split("&")[0].strip()
                                          high_start_1 = numpy.double(range_1.split(";")[0].strip())
                                          high_end_1 = numpy.double(range_1.split(";")[1].strip())

                                          range_2 = data_list[7].split("&")[1].strip()
                                          high_start_2 = numpy.double(range_2.split(";")[0].strip())
                                          high_end_2 = numpy.double(range_2.split(";")[1].strip())

                                          remap_list.append([high_start_1, high_end_1, 3])
                                          remap_list.append([high_start_2, high_end_2, 3])
                              else:
                                    pass
                              
                              # do the reclassification with the RemapRange objectds
                              param_remap = Reclassify(interpolated_param, "VALUE",
                                    remap=RemapRange(remap_list))
                              param_reclass = arcpy.sa.Con((param_remap == 1), 0.25,
                                    (arcpy.sa.Con(((param_remap == 2)), 0.75,
                                          (arcpy.sa.Con((param_remap == 3), 1, 0)))))
                              
                              # multiply params raster layers
                              if param_counter == 0:
                                    suitability = param_reclass
                              elif param_counter > 0:
                                    suitability = suitability * param_reclass
                              param_counter += 1

                        arcpy.gp.ExtractByMask_sa(suitability, mask_area, "{path}{name}_{num}.tif".format(path = path,
                              name=name, num=dataset_index))
            
            return


                               





