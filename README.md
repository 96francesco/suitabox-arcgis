<a href="https://www.repostatus.org/#active"><img src="https://www.repostatus.org/badges/latest/active.svg" alt="Project Status: Active – The project has reached a stable, usable state and is being actively developed." /></a>
[![License: GPL-3.0](https://img.shields.io/github/license/96francesco/suitabox-arcgis)](https://opensource.org/licenses/GPL-3.0)

# Suitabox
This is the repository of Suitabox, an ArcGIS custom toolbox written in Python applicable to ArcGIS Pro.
<img src="https://user-images.githubusercontent.com/88101466/171201971-a2c3b362-279b-450f-95f8-47d6d20967e8.png" width="250" height="350">


* Development: [Francesco Pasanisi](https://github.com/96francesco)
* Software and theoretical contribution: [Dr. Juan Miguel Ramirez-Cuesta](https://www.researchgate.net/profile/Juan-Ramirez-Cuesta)
* Theoretical contribution: 
  - [Prof. Gaetano Alessandro Vivaldi](https://www.researchgate.net/profile/Gaetano_Alessandro_Vivaldi)
  - [Dr. Diego Intrigliolo](https://www.researchgate.net/profile/Diego-Intrigliolo)

**Contents**
1. [Description](#description)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Tools](#tools)
5. [Contributions](#contributions)
6. [License](#license)
7. [Troubleshooting](#troubleshooting)
8. [Alerts](#alerts)

## Description
Suitabox uses meteorological data collected from local station networks to analyze the suitable distribution of a tree crop in a specific area based on agroecological criteria. There are 4 default crops at this moment (avocado, kiwifruit, European hazelnut and walnut), and the criteria applied to these crops were obtained from scientific literature. Suitabox allows users to submit customized parameters, through a specific tool, in order to provide them more flexibility and because there aren't many references about specific agroecological thresholds. In addition, the toolkit allows users to use four [RCP models](https://en.wikipedia.org/wiki/Representative_Concentration_Pathway) to explore how a climate change scenario can influence a crop species within the considered study area. Suitabox now only uses air temperature and elevation data, with no soil data or other meteorological variables, to maintain simplicity for all types of users, but fresh updates will soon fill in these gaps.
 
The goal of this project is to provide an open-source and user-friendly ArcGIS toolbox helpful to carry out suitability mapping for tree crops in Mediterranean areas. Suitabox has been developed in order to make it implementable in different studies and situations:
  - It has the capability to add value to studies on suitability analysis related to a specific crop for a certain area and the evaluation of climate change’s effects on crops’ suitability distribution;
  - It can support decision-making processes in the field of landscape planning and management;
  - It can be a helpful tool to assess the introduction of new crops in a particular area (in addition to other tools and expertises), encouraging researchers, authorities, and other stakeholders to conduct research on these new crops and avoiding new introductions brought on by the fad of the day;
  - By attempting to automate at least the steps of the studies involving meteorological data, the toolbox could be helpful in research to speed up studies about the suitability of an area for the cultivation of a particular crop, which are typically conducted using complicated methodologies (such as multi-criteria decision analysis).

## **Installation**
### 1. Download the toolbox
* Click the green button **Code** on the upper-right corner of this page and select **Download zip**.
  ![image](https://user-images.githubusercontent.com/88101466/171160202-452b9b65-fd10-482f-80c7-13989fee0ec2.png) 
* Once donwloaded, decompress the zip file.

### 2. Connect the toolbox
* In ArcGIS, navigate to the Catalog.
* Right-click on the Folders/Folder connections node and add a new folder connetion.

  ![image](https://user-images.githubusercontent.com/88101466/171161987-b8f00be5-c190-4152-84d2-f49a1974c2a0.png)
* Type the path or navigate to the suitabox folder and click OK.
* Browse into the toolbox and start using its tools. 

  ![image](https://user-images.githubusercontent.com/88101466/181484592-b410fea8-08ba-4318-a7b8-17ca54fd057c.png)


# **Usage**
Double-click on a tool within the toolbox to open it and start using it. Please see the tool metadata/help documentation for more information on how to use each tool, and read the [Tools](#tools) section

# **Tools**
At the moment, Suitabox only has 2 tools. Updates with new tools will be made available soon. **Crop Suitability tool** is the core instrument of this toolbox, while **Custom Crop Pre-Processing** serves as a support for the *Custom Crop* option in the former tool.

<img src="https://user-images.githubusercontent.com/88101466/181483773-20e0213c-355a-4e5d-83bb-6cdd4648fb84.jpg" width="900" height="400">

<img src="https://user-images.githubusercontent.com/88101466/181484001-4aa46103-3ddd-4be0-aaaa-7b8918524215.jpg" width="900" height="300">

The flowchart below shows the interrelationship between the different modules.
<img src="https://user-images.githubusercontent.com/88101466/186447511-d403232c-6c89-47ba-8426-8e2647c45077.png" width="800" height="450">

**Crop Suitability Tool** is the core tool of Suitabox. Its main purpose is to produce, for a given area of study and meteorological conditions, a suitability map of the considered crop species. 
The inputs required to the user in the Crop Suitability tool have been divided into 5 categories:
  1) *General inputs*, where the user is asked to specify:
      - The *Crop species*, choosing one of the default crops (avocado, kiwifruit, European hazelnut or walnut) or the costum crop option. For each one of these crops, different temperature thresholds or requirements have been identified based on literature references and implemented within the code. 
      - The *Cultivar*, required depending on the selected *Crop species* option. This input is essential since winter chilling requirements are cultivar-specific. The chilling requirements are computed following only the Chilling Hours model (Weinberger, 1950) so far, but hopefully, different methods will be available with new releases.
      - *Borders of the study area*, in ESRI shapefile extension (.shp).
      - *Weather stations*, i.e., A point feature layer (.shp) containing the weather stations location. The feature attribute table must have an *ID* column with an integer and unique number for each station. If the user wants to use the *topographic correction* option (explained later), this shapefile must also have an additional column (named *alt*) with the altitude in meters of each meteorological station.
      - *Weather hourly data*, i.e., the dataset(s) obtained from the weather stations, with **hourly resolution**. The user can upload one dataset per year. This dataset must have the following columns: i) an ID column to be joined with the weather stations layer, in integer type; ii) a Day of Year (DoY) column in integer type; iii) an air temperature (Tair) column with the temperature data. If the user selects a crop with a winter chilling hours requirement (i.e. kiwifruit, walnut, hazelnut, or custom crop) the dataset must cover a hydrological year (i.e., from 01 October of year n to 30 September of year n+1) to refer the chilling hours’ calculation to that specific season.
      - The *topographic correction* option. The user can **optionally** (but strongly recommended) upload a Digital Elevation Model (DEM) raster layer (.tif). If provided, the script tool will compute a correction of the interpolated air temperature using the terrain altitude. The temperature will be corrected (Tair.corr) using the following formula, which applies the average environmental lapse rate factor (6.5 ºC/km) through a DEM obtained via interpolation of the altitude (alt) field of the weather stations layer.
       
  2) *Custom periods*: the temperature-based parameters considered for each crop relate to a specific time of the year. Thanks to this information, the relevant data for each parameter are extracted from the weather dataset via the DoY column. Since the same crop can show a slightly different behavior and responses in two distinct locations, this input category allows the user to change, for each specific phenological phase (i.e., growing season, budding, flowering, fruit set and growth, chilling hours accumulation), the DoY range considered to extract the Tair data needed for evaluating the thresholds/requirements of the selected crop. By default, the considered periods are the ones included in the table below. The user should include the initial and final DoY separated by a dash. If the user does not modify the text inside these boxes (i.e., leaving the dash inserted by default), the standard periods will be used. As shown in the table below, not all the considered periods are related to each default crop, depending on the literature references found in bibliography so far, i.e., when the user selects a crop species only some specific periods will be customizable. <img src="https://user-images.githubusercontent.com/88101466/186457910-0abc8c50-91ed-4b49-a5f2-3b60cdc71ac3.png" width="600" height="300">
   
  3) *Climate change scenarios*, where the user can optionally select one of the available RCP  models (2.6, 4.5, 6.0 and 8.5) to simulate the crop suitability distribution under such scenarios. If this option is used, the *Tair* of each weather station will be corrected with the annual average temperature rise predicted by the chosen scenario within the pixel where the weather station is located. Furthermore, the user can select different temporal windows: the near-future (period 2020-2039) and increasingly distant-future projection (periods 2040-2059, 2060-2079, 2080-2099).
   
  4) *Interpolation settings*, where the user can adjust the parameters of the Inverse Distance Weighted interpolation method. This is the only interpolation approach available so far, but different methods (including geostatistical methods, e.g. kriging) will be made available with new releases.
   
  5) *Output settings*, where the user can:
      - Select the output directory. Suitabox will use the information from this input to create a new folder inside the selected path, named *{output name}_output*.
      - Write the output name, for specifying the nomenclature of the file to be created inside the output folder.
      - Select the output type. The user can choose between 2 types of output: a *Reclassified map*, obtained by doing a final reclassification of the suitability map according to the 4 classes shown in the table below, or a *Stretched values map*, computed without executing the final reclassification therefore showing stretched values from 0 to 1, an area being more suitable when closer to 1. Furthermore, the user can decide to exclude some land uses from the map (such as non-agricultural areas) using [CORINE Land Cover](https://land.copernicus.eu/pan-european/corine-land-cover). This option is only available for regions covered by CORINE. The user is provided with a multiple-choice box list, where is possible to select the desired areas. By default, agricultural areas are selected. The tool will apply a specific symbology to the final map depending on the selected output type.
      ![image](https://user-images.githubusercontent.com/88101466/186602512-0afa9fe5-7371-43f2-a076-1b4ffe3ee3fb.png)
      - Select an *Additional output* between the *Standard deviation map*, computed by calculating the standard deviation among the provisional suitability layers, to visualize the variations of a certain pixel, and the *Uncertainty map*, which shows the spatial uncertainty of the obtained map, and it is computed depending on the weather stations’ location and distance, using the Euclidean Distance function of the ArcGIS Spatial Analyst toolbox. This function calculates, for each cell, the Euclidean distance to the closest weather station. The purpose of this additional map is to underline the uncertainties in the toolbox output as a consequence of the closest weather station distance. 
 
The **Custom Crop Pre-processing** tool is preparatory for the use of the *Custom crop* option in the Crop Suitability tool. The purpose of this tool is to prepare a table with the custom crop’s requirements defined by the user, which will be exported as a CSV file inside the toolbox directory and read by the Crop Suitability tool subroutine specific for the Custom crop option.
For the correct functioning of this tool, user must upload the param_schema.csv file located inside the toolbox directory an press the Create table button in the tool pane, without running the tool. 
![image](https://user-images.githubusercontent.com/88101466/186607226-76e7f06d-f3ef-45e9-aa8d-71268e3cb1fc.png)

A new table named Custom_Crop_Pre_processing_Schema will be displayed in the Contents pane, under the Standalone tables category. The user has open this table in order to design the custom parameters, and the image in the [Tools](#tools) section shows an example of how to fulfill this table correctly. The user must follow these instructions:
  - In the *param_name* column, the user should write the desired parameter name, preferably without spaces and special characters. 
  - In the *param_ID* column, the user must provide an integer ID, possibly incrementing this number by one for each parameter uploaded. 
  - In the *function* column, the user writes a specific function to apply for the calculation of the related custom parameter. These functions’ calculations are grouped for each weather station and are related to a specific period. At the moment, there are 6 available functions: *mean*, *min*, and *max* calculate the average, minimum, and maximum *Tair*; *avg_daily_max* and *avg_daily_min* calculate, respectively; the average of daily maximum and minimum T; finally, the *chill_hours* function executes a count of the chilling hours according to Weinberger model. To use this last function, subsequently, the user should upload a weather dataset in hydrological year format inside the Crop Suitability tool.
  - In the *doy_range* column, the user defines the period of time of interest to extract the weather data, expressed in DoY. The starting and the ending DoY must be separated by a hyphen.
  - In the last 4 columns (*unsuitable*, *marginal*, *suitable*, *highly_suit*) the user can specify the value ranges for each class. The two extremes of the range must be separated by a semicolon. To express a range that tends to ±infinity, the use of a great absolute number (positive or negative) is necessary in order to cope with the ArcPy function used to accomplish this task.


## Contributions
If you'd want to contribute as a developer to the project, take these steps to get started:

  1. Fork the toolbox repository (https://github.com/96francesco/suitabox-arcgis)
  2. Create your feature branch (git checkout -b my-new-feature)
  3. Commit your changes (git commit -m 'Add new feature')
  4. Push to the branch (git push origin my-new-feature)
  5. Create a new Pull Request

## License
The ArcGIS Toolbox for Suitabox is distributed under the [GPL 3.0 license](https://opensource.org/licenses/GPL-3.0), a permissive open-source license.

## Troubleshooting
Suitabox is distributed as is and without any kind of warranty. If you encounter software errors or bugs please report the issue. Providing a thorough account of the circumstances in which the problem occurred will aid in the bug's identification. Use the [Issues tracker](https://github.com/96francesco/suitabox/issues) on GitHub to report bugs in the software and ask for feature enhancements

## Alerts
Unfortunately for ArcGIS Pro users, the automatic upload of the symbology does not work for the stretched values maps and the additional outputs due to a possible [bug](https://community.esri.com/t5/python-questions/arcpy-management-applysymbologyfromlayer-works/td-p/1137999) in the [ArcPy ApplySymbologyFromLayer() module](https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/apply-symbology-from-layer.htm). The users can manually upload the symbology provided within the folder using the Symbology panel and select **Import from layer file**.

![image](https://user-images.githubusercontent.com/88101466/171421844-343cfd09-81ff-4f30-9ba4-5c7041f322b5.png)

