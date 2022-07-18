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

# imports
import os
import pandas as pd
import arcpy
from arcpy.sa import *
import datetime
import locale
from importlib import reload

# some general settings
arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False
time_run = datetime.datetime.now()
separator = locale.localeconv()["decimal_point"] # take the decimal separator of the machine
tbx_dir = os.path.realpath(__file__)
tbx_dir = tbx_dir.split("stb")[0] # take the directory where the toolbox is stored

#####################################
############ USER INPUTS ############
#####################################

# 1. general inputs
arcpy.AddMessage("Reading your inputs...")  
crop_species = arcpy.GetParameterAsText(0) # considered tree crop
cultivar = arcpy.GetParameterAsText(1) # cultivar
mask_area = arcpy.GetParameterAsText(2) # area of study 
ws_points = arcpy.GetParameterAsText(3) # points shapefile of the weather stations
hourly_data = arcpy.GetParameterAsText(4) # hourly weather dataset
topography = arcpy.GetParameterAsText(5) # digital elevation model

# 3. climate change scenarios
rcp_model = arcpy.GetParameterAsText(11) # choose the RCP model
rcp_period = arcpy.GetParameterAsText(12) # choose the period of projections

# 4. interpolation settings
idw_power = int(arcpy.GetParameterAsText(13)) # IDW power
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

# 5. output settings
dir = arcpy.GetParameterAsText(17) # directory where outputs will be saved
name = arcpy.GetParameterAsText(18) # output name
output_type = arcpy.GetParameterAsText(19) # the output type chosen
clc_categories = arcpy.GetParameter(20) # corine land cover areas to consider
add_on = arcpy.GetParameterAsText(21) # additional outputs to create

#################################################
############ STARTING THE PROCESSING ############
#################################################

if __name__ == "__main__":
        # set extent
        arcpy.env.extent = mask_area

        # create a folder for the output inside the directory selected by user
        folder_name = "{}_output".format(name)
        new_path = arcpy.CreateFolder_management(dir, folder_name)
        path = "{}\\".format(str(new_path))
        arcpy.env.workspace = path
        os.chdir(path)
        arcpy.AddMessage("The current working directory is: " + path)

        # produce the layer for topographic correction if topography exists
        if topography:
                # set spatial resolution equal to the DEM resolution
                spatial_resolution = str(arcpy.GetRasterProperties_management(topography, "CELLSIZEX"))
                cell_size = int(spatial_resolution.split(separator)[0])

                # calculate the lapse rate correction layer
                arcpy.AddMessage("Producing the raster layer for topographic correction...")
                arcpy.MakeFeatureLayer_management(ws_points, 'ws_points_FeatureLayer')
                dem_idw = Idw('ws_points_FeatureLayer', 'alt', cell_size, idw_power, search_radius, "")
                dem_difference = dem_idw - topography
                arcpy.gp.ExtractByMask_sa(dem_difference, mask_area,
                        "{}\\dem_difference.tif".format(path))
                dem_difference = arcpy.Raster("{}\\dem_difference.tif".format(path))
                lapse_rate_correction = dem_difference * 0.0065
                arcpy.gp.ExtractByMask_sa(lapse_rate_correction, mask_area,
                        "{}\\lapse_rate_correction.tif".format(path))
                lapse_rate_correction = arcpy.Raster("{}\\lapse_rate_correction.tif".format(path))
                del dem_idw, dem_difference
                arcpy.Delete_management('ws_points_FeatureLayer')
        else:
                # if DEM is not uploaded by user, set a default spatial resolution of 100 m
                cell_size = 100

        # produce the raster layer with agricultural areas if required
        output_options = ["Reclassified map", 'Reclassified map considering CORINE land cover categories',
                "Stretched values map", "Stretched values map considering CORINE land cover categories"]
        if output_type in [output_options[i] for i in (1, 3)]:
                clc = arcpy.Raster("{}\\clc18.tif".format(tbx_dir))
                arcpy.AddMessage("Extracting the CORINE categories you have selected...")
                arcpy.gp.ExtractByMask_sa(clc, mask_area, "{}\\clc_mask.tif".format(path))
                clc_mask = arcpy.Raster("{}\\clc_mask.tif".format(path))

                clc_len = len(clc_categories)
                clc_counter = 0
                while clc_counter < clc_len:
                        cat = clc_categories[clc_counter]
                        cat_value = int(cat.split(".")[0])
                        clc_mask = arcpy.sa.Con((clc_mask == cat_value), 1, clc_mask)
                        clc_counter = clc_counter + 1

                if output_type == output_options[1]:
                        selected_areas = arcpy.sa.Con((clc_mask == 1), 1, 0)
                        selected_areas.save("{}\\selected_areas.tif".format(path))
                        selected_areas = arcpy.Raster("{}\\selected_areas.tif".format(path))
                        del clc_mask
                elif output_type == output_options[3]:
                        selected_areas = SetNull(clc_mask != 1, clc_mask)
                        selected_areas.save("{}\\selected_areas.tif".format(path))
                        selected_areas = arcpy.Raster("{}\\selected_areas.tif".format(path))
                        del clc_mask

                # if the DEM cell size is not the same of CORINE (100 m), do a resampling of CORINE raster layer
                # in order to obtain a new raster layer with the DEM cell size
                if topography and spatial_resolution != 100:
                        arcpy.Resample_management(selected_areas, "{}\\resample.tif".format(path),
                                 cell_size, "NEAREST")
                        selected_areas = arcpy.Raster("{}\\resample.tif".format(path))

        # split the multiple data sets imported 
        arcpy.AddMessage("Splitting the weather data sets...")
        single_datasets = hourly_data.split(";")
        datasets_len = len(single_datasets)

        # export every single dataset with an index
        counter = 0
        while counter <= int(datasets_len - 1):
                weather_dataset = hourly_data.split(";")[counter]

                # convert the dataset to pandas dataframe and save it in the working directory
                weather_dataset = pd.DataFrame(pd.read_csv(weather_dataset))
                weather_dataset.to_csv("{path}\\weather_dataset_{index}.csv".format(path=path, 
                        index=counter), index=False)
                counter = counter + 1

        # produce new weather datasets, according to the selected RCP model
        if rcp_model != "None":   
                arcpy.AddMessage("Selected RCP: {rcp}, period: {period}".format(
                        rcp=rcp_model, period=rcp_period))
                rcp = arcpy.Raster("{path}\\RCPs\\{rcp}_{period}.tif".format(
                        path=tbx_dir, rcp=rcp_model, period=rcp_period))
                arcpy.MakeFeatureLayer_management(ws_points, 'ws_points_layer')
                in_layer = "ws_points_layer"
                arcpy.MakeRasterLayer_management(rcp, "rcp_layer")
                rcp_layer = "rcp_layer"
                ExtractValuesToPoints(in_layer, rcp_layer, "ws_layer")

                for file in os.listdir(path):
                        os.chdir(path)
                        if file.startswith("weather_dataset_"):
                                csv = pd.read_csv(file)
                                csv_name = os.path.basename(path + str(file))
                                csv_index = csv_name.split("_")[2]
                                csv_index = csv_index.split(".")[0]
                                ws_layer = "{}\\ws_layer.shp".format(path)

                                arcpy.MakeTableView_management(file, "csv")
                                memory_table = arcpy.CopyRows_management("csv", "memory/copied")

                                arcpy.JoinField_management(memory_table, "ID", ws_layer, "ID", "RASTERVALU")

                                out_name = "weather_dataset_{}.csv".format(str(csv_index))
                                arcpy.TableToTable_conversion(memory_table, path, out_name)

                                # do the correction with the predicted temperature increase
                                new_csv = pd.read_csv(file)
                                new_csv["Tair"] = new_csv["Tair"] + new_csv["RASTERVALU"]
                                new_csv.to_csv("{path}\\new_dataset_{index}.csv".format(path=path, 
                                        index=str(csv_index)))
                                os.remove("{path}\\weather_dataset_{index}.csv".format(path=path, 
                                        index=str(csv_index)))
                # remove useless files from working directory
                xml_files = [i for i in os.listdir(path) if i.endswith(".txt.xml") or\
                         i.endswith(".csv.xml")]
                for n in xml_files:
                        os.remove(os.path.join(path, n))

        # call the method related to the crop species selected by the user
        arcpy.AddMessage("Doing the computation. It can take a few minutes, depending on your inputs...")
        if crop_species == "Avocado":
                import avocado_pro
                avocado_pro = reload(avocado_pro)
                avocado_pro.avocado_fun()
        elif crop_species == "Kiwifruit":
                import kiwifruit_pro
                kiwifruit_pro = reload(kiwifruit_pro)
                kiwifruit_pro.kiwifruit_fun()
        elif crop_species == "Walnut":
                import walnut_pro
                walnut_pro = reload(walnut_pro)
                walnut_pro.walnut_fun()
        elif crop_species == "European hazelnut":
                import hazelnut_pro
                hazelnut_pro = reload(hazelnut_pro)
                hazelnut_pro.hazelnut_fun()
        elif crop_species == "Custom crop":
                import custom_crop_pro
                custom_crop_pro = reload(custom_crop_pro)
                custom_crop_pro.custom_crop_fun()


        #################################################
        ############ PREPARING THE FINAL MAP ############
        #################################################

        arcpy.AddMessage("Computation completed. Preparing your map...")

        # list all the single year suitability laers
        suitability_layers = [f for f in os.listdir(path) if f.startswith(name + "_") and f.endswith(".tif")]

        # set map document and dataframe
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        map = aprx.listMaps("Map")[0]

        # calculate average map among single year suitability layers
        avg_map = CellStatistics(suitability_layers, "MEAN") 
        avg_map.save("memory/avg_map")
        avg_map = arcpy.Raster("memory/avg_map")

        # calculate standard devition among single year suitability layers if required
        if add_on == "Standard deviation map" or add_on == "Both":
                arcpy.AddMessage("Creating standard deviation map...")
                std_map = CellStatistics(suitability_layers, "STD") 
                std_map.save("memory/std_map")
                std_map = arcpy.Raster("memory/std_map")
                arcpy.gp.ExtractByMask_sa(std_map, mask_area, "{path}\\{name}_std.tif".format(path=path, name=name))
                std_map = arcpy.Raster("{path}\\{name}_std.tif".format(path=path, name=name))

                # upload symbology and add to canvas
                std_layer = arcpy.MakeRasterLayer_management(std_map, "std_map")[0]
                arcpy.management.ApplySymbologyFromLayer(std_layer, "{}symbology\\std_map.lyrx".format(tbx_dir),
                        None, "MAINTAIN")
                map.addLayer(std_layer)

        # clip the average map with the mask area
        arcpy.gp.ExtractByMask_sa(avg_map, mask_area, "{}\\temp_suitability.tif".format(path))
        suitability_map = arcpy.Raster("{}\\temp_suitability.tif".format(path))

        # create the final output depending on the output type selected by the user
        if output_type == output_options[0]: # reclassified map
                arcpy.AddMessage("Doing the map reclassification...")
                
                # do the reclassification and save the raster
                final_suitability = arcpy.sa.Con((suitability_map >= 0) & (suitability_map < 0.25), 1,
                (arcpy.sa.Con(((suitability_map >= 0.25) & (suitability_map < 0.50)), 2,
                (arcpy.sa.Con(((suitability_map >= 0.50) & (suitability_map < 0.75)), 3, 4)))))
                final_suitability.save("{path}\\final_{name}.tif".format(path=path, name=name))
                final_suitability = arcpy.Raster("{path}\\final_{name}.tif".format(path=path, name=name))

                # upload the symbology
                arcpy.AddColormap_management(final_suitability, "#", "{}symbology\\symbology_0.clr".format(tbx_dir))

                # delete bindings and useless raster
                del suitability_map

        elif output_type == output_options[1]: # reclassified map + corine land cover
                arcpy.AddMessage("Doing the map reclassification considering the CORINE land cover categories you selected...")

                # do the reclassification
                final_suitability_reclass = arcpy.sa.Con((suitability_map >= 0) & (suitability_map < 0.25), 1,
                        (arcpy.sa.Con(((suitability_map >= 0.25) & (suitability_map < 0.50)), 2,
                        (arcpy.sa.Con(((suitability_map >= 0.50) & (suitability_map < 0.75)), 3, 4)))))
                
                # multiplicate for the CLC selected areas and sace the raster
                suitability_clc = final_suitability_reclass * selected_areas
                suitability_clc.save("{path}\\final_{name}.tif".format(path=path, name=name))
                final_suitability = arcpy.Raster("{path}\\final_{name}.tif".format(path=path, name=name))

                # upload the symbology
                arcpy.AddColormap_management(final_suitability, "#", "{}symbology\\symbology_1.clr".format(tbx_dir))

                # delete bindings and useless raster
                del final_suitability_reclass, suitability_map, selected_areas, suitability_clc

        elif output_type == output_options[2]: # stretched values map
                final_suitability = suitability_map
                arcpy.gp.ExtractByMask_sa(final_suitability, mask_area, "{path}\\final_{name}.tif".format(
                        path=path, name=name))
                final_suitability = arcpy.Raster("{path}\\final_{name}.tif".format(path=path, name=name))
                del suitability_map

        else: # stretched values map + corine land cover
                arcpy.AddMessage("Preparing your map depending on the CORINE land cover categories you selected...")
                suitability_clc = suitability_map * selected_areas
                suitability_clc.save("{path}\\final_{name}.tif".format(path=path, name=name))
                final_suitability = arcpy.Raster("{path}\\final_{name}.tif".format(path=path, name=name))
                del suitability_map, selected_areas, suitability_clc

        # compute uncertainty map if required
        if add_on == "Uncertainty map" or add_on == "Both":
                arcpy.AddMessage("Creating an uncertainty map...")
                uncertainty = EucDistance(ws_points, cell_size=cell_size, 
                        out_direction_raster="{}\\uncertainty.tif".format(path))
                uncertainty.save("{}\\uncertainty.tif".format(path))
                uncertainty = arcpy.Raster("{}\\uncertainty.tif".format(path))
                arcpy.gp.ExtractByMask_sa(uncertainty, mask_area, "{path}\\{name}_uncertainty.tif".format(
                        path=path, name=name))
                uncertainty = arcpy.Raster("{path}\\{name}_uncertainty.tif".format(
                        path=path, name=name))

                unc_layer = arcpy.MakeRasterLayer_management(uncertainty, "uncertainty_map")[0]
                arcpy.management.ApplySymbologyFromLayer("uncertainty_map", "{}symbology\\uncertainty_map.lyrx".format(tbx_dir),\
                        None, "MAINTAIN")
                map.addLayer(unc_layer)

        # add the final layer on canvas and save the project
        final_layer = arcpy.MakeRasterLayer_management(final_suitability, "final_{}".format(name))[0]
        map.addLayer(final_layer)
        aprx.save() 

        # delete bindings
        del ws_points, avg_map, final_suitability, suitability_layers, final_layer, aprx
        if topography:
                del lapse_rate_correction

        # remove temporary/useless layers from path
        arcpy.AddMessage("Removing temporary files from the working directory...") 
        trash_files = [f for f in os.listdir(path) if not (f.startswith(name) or f.startswith("info")\
                or f.startswith("final_"))]
        for f in trash_files:
                os.remove(os.path.join(path, f))
        
        del path