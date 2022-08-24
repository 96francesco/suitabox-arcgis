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

## requirements

import   os
import   pandas    as pd
import   arcpy
import   locale
from     arcpy.sa  import *
from     importlib import reload


## User inputs, determined through the tool wizard

arcpy.AddMessage("Reading your inputs...")           # just a message

# Category: General inputs
crop_species =   arcpy.GetParameterAsText(0)         # the selected crop species
cultivar     =   arcpy.GetParameterAsText(1)         # cultivar
mask_area    =   arcpy.GetParameterAsText(2)         # area of study 
ws_points    =   arcpy.GetParameterAsText(3)         # points shapefile of the weather stations
hourly_data  =   arcpy.GetParameterAsText(4)         # weather dataset (.csv)
topography   =   arcpy.GetParameterAsText(5)         # digital elevation model (.tif)

# Category: Climate change scenarios
rcp_model    =   arcpy.GetParameterAsText(11)        # choose the RCP model
                                                     # Options: 2.6, 4.5, 6, 8.5

rcp_period   =   arcpy.GetParameterAsText(12)        # choose the period of projections
                                                     # Options: 2020-2039, 2040-2059
                                                     #          2060-2079, 2080-2099   

# Category: Interpolation settings
idw_power    =   int(arcpy.GetParameterAsText(13))   # IDW power
search       =   arcpy.GetParameterAsText(14)        # type of search radius
points_num   =   arcpy.GetParameterAsText(15)        # number of points to consider
distance     =   arcpy.GetParameterAsText(16)        # distance to consider

if search   == 'RadiusVariable':
        search_radius = "{search}({points}, {dist})".format(search=search, 
                points=points_num, dist=distance)
elif search == 'RadiusFixed':
        search_radius = "{search}({dist}, {points})".format(search=search,
                dist=distance, points=points_num)

# Category: Output settings
dir              =   arcpy.GetParameterAsText(17)     # directory where outputs will be saved
name             =   arcpy.GetParameterAsText(18)     # output name
output_type      =   arcpy.GetParameterAsText(19)     # the output type chosen
clc_categories   =   arcpy.GetParameter(20)           # corine land cover areas to consider
add_on           =   arcpy.GetParameterAsText(21)     # additional outputs to create


## Constants
path      =    "{}\\".format(str(arcpy.CreateFolder_management(dir, 
                        "{}_output".format(name))))        # create output folder
separator =    locale.localeconv()["decimal_point"]        # get the decimal separator of the local machine
tbx_dir   =    os.path.realpath(__file__).split("crop")[0] # get the path where the .tbx file is stored
os.chdir(path)                                             # set the new path as working directory

arcpy.env.workspace            =   path                    # set the new path as workspace
arcpy.env.overwriteOutput      =   True                    # tool will execute and overwrite the output dataset 
arcpy.env.qualifiedFieldNames  =   False                   # the output field name will not include the table name
                                                           # this setting is crucial for the correct reading of
                                                           # the the feature attribute tables
arcpy.env.extent               =   mask_area               # use the study area uploaded by user as map extent 
arcpy.MakeFeatureLayer_management(ws_points, 
                'ws_points_FeatureLayer')                  # make a feature layer of the weather stations shapefile

arcpy.AddMessage("The current working directory is: {}".format(path)) # just a message

if topography:
        spatial_resolution = str(arcpy.GetRasterProperties_management(topography, 
                                                        "CELLSIZEX"))
else: 
        spatial_resolution = 100       # set output spatial resolution equal to the DEM if uploaded
                                       # otherwise set it equal to 100 m

aprx   =   arcpy.mp.ArcGISProject("CURRENT")   # set the map document
map    =   aprx.listMaps("Map")[0]             # set the correct map dataframe


## Functions

def create_dem_difference(points, DEM):
        """
        FeatureLayer Raster -> Raster
        Consume the weather station shapefile and the original DEM layer
        to produce the DEM difference (Interpolated - Original) layer
        """
        dem_int        =    Idw(points, 'alt', int(spatial_resolution.split(separator)[0]), 
                                        idw_power, search_radius, "")  # create interpolated DEM with stations' altitude
        dem_difference =    dem_int - DEM                              # calculate the DEM difference
        
        del    dem_int         # delete binding
        return dem_difference

def create_lapse_rate(dem_difference):
        """
        Raster -> Raster
        consume the DEM difference layer to produce the lapse rate correction layer
        """
        lapse_rate_correction = dem_difference * 0.0065            # apply the formula
        lapse_rate_correction = arcpy.Raster(ExtractByMask(lapse_rate_correction, 
                                        mask_area))                # extract the layer
        del    dem_difference                                      # delete useless binding
        return lapse_rate_correction

def create_corine_areas(toolbox_directory, selected_corine_areas):
        """
        Object Object -> Raster
        Consume the CORINE areas selected by the user to create a raster layer representing them, 
        depending on the type of output selected by the user
        """
        clc_mask    =   arcpy.Raster("{}\\clc18.tif".format(toolbox_directory)) # read the CLC layer located in 
                                                                                # toolbox directory
        
        clc_mask    =   arcpy.Raster(ExtractByMask(clc_mask, mask_area))        # clip the CLC layer with the study
                                                                                # area

        clc_length  =   len(selected_corine_areas)
        clc_counter =   0
        while clc_counter < clc_length:
                cat         =   selected_corine_areas[clc_counter]
                cat_value   =   int(cat.split(".")[0])
                clc_mask    =   arcpy.sa.Con((clc_mask == cat_value), 1, clc_mask)
                clc_counter =   clc_counter + 1
        
        if output_type == 'Reclassified map considering CORINE land cover categories':
                selected_areas = arcpy.sa.Con((clc_mask == 1), 1, 0)
                selected_areas.save("{}\\selected_areas.tif".format(path))
                del clc_mask
        elif output_type == "Stretched values map considering CORINE land cover categories":
                selected_areas = SetNull(clc_mask != 1, clc_mask)
                selected_areas.save("{}\\selected_areas.tif".format(path))
                del clc_mask
        
        return selected_areas

def corine_resampling(corine_layer, new_resolution):
        """
        Raster -> Raster
        Do a resampling of CORINE Land Cover mask to obtain a new raster with
        the same DEM cell size (if DEM cell size is not 100 m - the same as CORINE)
        """
        global selected_areas
        if spatial_resolution != 100:
                arcpy.Resample_management(corine_layer, "{}\\resample.tif".format(path),
                                 new_resolution, "NEAREST") # create new layer
                selected_areas = arcpy.Raster("{}\\resample.tif".format(path)) # read it as a Raster
                return selected_areas

def manage_weather_datasets(input_datasets):
        """
        CSV file -> CSV file
        Split and export as CSV files the weather datasets uploaded by user, in order to make them
        readable by the specific (crop) subroutine
        """
        single_datasets = input_datasets.split(";") # split the datasets in a list
        datasets_length = len(single_datasets) # get the list length

        # export every single dataset with an index number
        counter = 0
        while counter <= int(datasets_length - 1):
                weather_dataset = hourly_data.split(";")[counter]

                # convert the dataset to pandas dataframe and save it in the working directory
                weather_dataset = pd.DataFrame(pd.read_csv(weather_dataset))
                weather_dataset.to_csv("{path}\\weather_dataset_{index}.csv".format(path=path, 
                        index=counter), index=False)
                counter = counter + 1

def create_suitability_map(annual_suitability_layers): 
        """
        Raster(s) -> Raster
        Consume the list of suitability layers obtained from each year of weather data
        to obtain a single average raster suitability layer
        """      
        avg_map = CellStatistics(annual_suitability_layers, "MEAN") # calculate the average layer
        avg_map.save("memory/avg_map")
        avg_map = arcpy.Raster("memory/avg_map")

        arcpy.gp.ExtractByMask_sa(avg_map, mask_area, "{}\\temp_suitability.tif".format(path)) # clip layer
        suitability_map = arcpy.Raster("{}\\temp_suitability.tif".format(path)) # read it as a raster
        
        del avg_map #delete bindings 

        return suitability_map

def create_sd_map(annual_suitability_layers, study_area):
        """
        Raster Shapefile -> Raster
        Compute the standard deviation (pixel per pixel) among the annual suitability layers,
        creating a new raster
        """
        if add_on == "Standard deviation map" or add_on == "Both":
                std_map = CellStatistics(annual_suitability_layers, "STD")           # compute standard deviation
                std_map = arcpy.Raster(ExtractByMask(std_map, study_area))           # clip the new raster with
                                                                                     # the study area
                std_map.save("{path}\\{name}_std.tif".format(path=path, name=name))  # save it in the
                                                                                     # working directory
                std_layer = arcpy.MakeRasterLayer_management(std_map, "std_map")[0]
                arcpy.ApplySymbologyFromLayer_management(std_layer, "{}symbology\\std_map.lyrx".format(tbx_dir),
                        None, "MAINTAIN")   # change symbology
                map.addLayer(std_layer)     # upload to canvas

def create_uncertainty_map(points, spatial_resolution):
        """
        Point shapefile -> Raster
        Consume the weather station shapefile to produce the uncertainty map
        through the Euclidean distance formula
        """
        uncertainty_map = EucDistance(points, cell_size=spatial_resolution, 
                out_direction_raster="{path}\\{name}_uncertainty.tif".format(path=path, 
                                                        name=name))   # compute euclidean distance
        uncertainty_map = ExtractByMask(uncertainty_map, mask_area)   # clip it with study area
        uncertainty_map.save("{path}\\{name}_uncertainty.tif".format(path=path, 
                                                        name=name))   # save it inside working directory

        uncertainty_layer = arcpy.MakeRasterLayer_management(uncertainty_map, "uncertainty_map")[0]
        arcpy.management.ApplySymbologyFromLayer("uncertainty_map", 
        "{}symbology\\uncertainty_map.lyrx".format(tbx_dir), None, "MAINTAIN") #change symbology
        map.addLayer(uncertainty_layer) #upload to canvas

def create_reclassified_map(provisional_suitability_map):
        """
        Raster -> Raster
        Consume the provisional suitability map with stretched values to do a reclassification 
        in the 4 considered suitability classes
        """
        global suitability_map
        # do the reclassification with arcpy Con() module
        final_suitability = arcpy.sa.Con((provisional_suitability_map >= 0) & (provisional_suitability_map < 0.25), 1,
                (arcpy.sa.Con(((provisional_suitability_map >= 0.25) & (provisional_suitability_map < 0.50)), 2,
                (arcpy.sa.Con(((provisional_suitability_map >= 0.50) & (provisional_suitability_map < 0.75)), 3, 4)))))
        
        final_suitability.save("{path}\\final_{name}.tif".format(path=path, name=name)) #save it in the working directory

        arcpy.AddColormap_management(final_suitability, "#", 
                "{}symbology\\symbology_0.clr".format(tbx_dir)) # upload symbology

        del suitability_map # delete bindings

        return final_suitability

def create_reclassified_clc_map(provisional_suitability_map, clc_areas):
        """
        Raster(s) -> Raster
        Consume the provisional suitability map with stretched values and the CORINE selected
        areas to produce a reclassified layer with the 4 considered suitability class, only
        considering the CORINE selected areas
        """
        global suitability_map, selected_areas

        # do the reclassification
        final_suitability_reclass = arcpy.sa.Con((provisional_suitability_map >= 0) & (provisional_suitability_map < 0.25), 1,
                (arcpy.sa.Con(((provisional_suitability_map >= 0.25) & (provisional_suitability_map < 0.50)), 2,
                (arcpy.sa.Con(((provisional_suitability_map >= 0.50) & (provisional_suitability_map < 0.75)), 3, 4)))))
        
        suitability_clc = final_suitability_reclass * clc_areas # multiplicate the reclassified raster
                                                                # for the CLC selected areas
        suitability_clc.save("{path}\\final_{name}.tif".format(path=path, name=name)) # save it in the working diretory
        final_suitability = arcpy.Raster("{path}\\final_{name}.tif".format(path=path, name=name)) # read it as a raster

        # upload the symbology
        arcpy.AddColormap_management(final_suitability, "#", "{}symbology\\symbology_1.clr".format(tbx_dir))

        # delete bindings and useless raster
        del final_suitability_reclass, suitability_map, selected_areas, suitability_clc

        return final_suitability

def create_stretched_clc_map(provisional_suitability_map, clc_areas):
        """
        Raster(s) -> Raster
        Consume the provisional suitability map with stretched values and the CORINE selected
        areas to produce a stretched values map only considering the CORINE selected areas
        """
        global suitability_map, selected_areas
        
        suitability_clc   =  provisional_suitability_map * clc_areas         # obtain the new layer

        suitability_clc.save("{path}\\final_{name}.tif".format(path=path,
                                                                 name=name)) # save it

        final_suitability =  arcpy.Raster("{path}\\final_{name}.tif".format(path=path, 
                                                                name=name))  # read it as a Raster
        
        del    suitability_map, selected_areas, suitability_clc              # delete bindings
        
        return final_suitability

def delete_temp_files():
        """
        List all the useless files in the working directory and delete it
        """
        trash_files = [f for f in os.listdir(path) if not (f.startswith(name) or f.startswith("info")\
                                or f.startswith("final_"))]
        
        for f in trash_files:
                os.remove(os.path.join(path, f))


if __name__ == "__main__":

        if topography:
                dem_difference = create_dem_difference('ws_points_FeatureLayer', topography)
                lapse_rate_correction = arcpy.Raster(create_lapse_rate(dem_difference))

        if output_type in ['Reclassified map considering CORINE land cover categories', 
                           "Stretched values map considering CORINE land cover categories"]:
                selected_areas = create_corine_areas(tbx_dir, clc_categories)

                if topography:
                        selected_areas = corine_resampling(selected_areas, spatial_resolution)

        manage_weather_datasets(hourly_data)

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
        arcpy.AddMessage("Doing the computation. It can take a few minutes, depending on your inputs...") # just a message
        if crop_species   ==   "Avocado":
                import avocado
                avocado   = reload(avocado)
                avocado.avocado_fun()
        elif crop_species ==   "Kiwifruit":
                import kiwifruit
                kiwifruit_pro = reload(kiwifruit)
                kiwifruit.kiwifruit_fun()
        elif crop_species == "Walnut":
                import walnut
                walnut    = reload(walnut)
                walnut.walnut_fun()
        elif crop_species == "European hazelnut":
                import hazelnut
                hazelnut  = reload(hazelnut)
                hazelnut.hazelnut_fun()
        elif crop_species == "Custom crop":
                import custom_crop
                custom_crop = reload(custom_crop)
                custom_crop.custom_crop_fun()



        arcpy.AddMessage("Computation completed. Preparing your map...") # just a message


        suitability_layers = [f for f in os.listdir(path) if 
                        f.startswith(name + "_") and f.endswith(".tif")]   # list all the single year suitability laers
        
        suitability_map    = create_suitability_map(suitability_layers)    # create the provisional suitability map

        if add_on == "Standard deviation map" or add_on == "Both":
                create_sd_map(suitability_layers, mask_area)
        
        if add_on == "Uncertainty map"        or add_on == "Both":
                create_uncertainty_map(ws_points, spatial_resolution)



        # create the final output depending on the output type selected by the user
        if output_type     ==   "Reclassified map":
                final_suitability = create_reclassified_map(suitability_map)
        
        elif output_type   ==   "Reclassified map considering CORINE land cover categories": 
                final_suitability = create_reclassified_clc_map(suitability_map, selected_areas)
                
        elif output_type   ==   "Stretched values map": 
                final_suitability = suitability_map

                del suitability_map

        else:
                final_suitability = create_stretched_clc_map(suitability_map, selected_areas)


        # add the final layer on canvas and save the project
        final_layer = arcpy.MakeRasterLayer_management(final_suitability, "final_{}".format(name))[0]
        map.addLayer(final_layer)
        aprx.save() 

        del ws_points, final_suitability, suitability_layers, final_layer, aprx
        if topography:
                del    lapse_rate_correction # delete useless bindings

        delete_temp_files()                  # remove temporary files
        
        del path