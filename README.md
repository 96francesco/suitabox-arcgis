[![License: GPL-3.0](https://img.shields.io/github/license/96francesco/suitabox-arcgis)](https://opensource.org/licenses/GPL-3.0)

# Suitabox
This is the repository of Suitabox, an ArcGIS Pro custom toolbox written in Python (using ArcPy). This toolbox was developed as part of my MSc thesis for the programme Agricultural and Environmental Sciences at University of Bari. The thesis manuscript can be found in the file thesis.pdf. 

**Contents**
1. [Description](#description)
2. [Installation](#installation)
3. [Tools](#tools)
4. [Contributions](#contributions)
5. [License](#license)
6. [Troubleshooting](#troubleshooting)

## Description
Suitabox allows to study, through customised thresholds, the suitability distribution of a crop for a certain area based on weather and soil data. 
Please read the tools' metadata for more information about the required data formats. 

The goal of this project is to provide a toolbox helpful to carry out suitability mapping for tree crops in Mediterranean areas. Suitabox has been developed in order to make it implementable in different studies and situations:
  - It has the capability to add value to studies on suitability analysis related to a specific crop for a certain area and the evaluation of climate change’s effects on crops’ suitability distribution;
  - It can support decision-making processes in the field of landscape planning and management;
  - It can be a helpful tool to assess the introduction of new crops in a particular area (in addition to other tools and expertises), encouraging researchers, authorities, and other stakeholders to conduct research on these new crops and avoiding new introductions brought on by the fad of the day;
  - By attempting to automate at least the steps of the studies involving meteorological and soil data, the toolbox could be helpful in research to speed up studies about the suitability of an area for the cultivation of a particular crop, which are typically conducted using complicated methodologies (such as multi-criteria decision analysis).

## **Installation**
### 1. Clone the repository with Git
```
git clone https://github.com/96francesco/suitabox-arcgis.git
```

### 2. Connect the toolbox
* In ArcGIS, navigate to the Catalog.
* Right-click on the Folders/Folder connections node and add a new folder connetion.

  ![image](https://user-images.githubusercontent.com/88101466/171161987-b8f00be5-c190-4152-84d2-f49a1974c2a0.png)
* Type the path or navigate to the suitabox folder and click OK.
* Browse into the toolbox and start using its tools. 


## **Tools**
### 1. **s1ComputeWeatherParameterSuitability**
This tool is used to create a suitability raster layer based on a chosen weather parameter. This tool works with inputs uploaded from a file Geodatabase (tables, raster and feature classes). The suitability distribution is computed through interpolation of the weather parameter, using metereological data from local weather stations, and through reclassification of the interpolated layer. At the moment, the only interpolation method available is [Inverse Distance Weighting (IDW)](https://en.wikipedia.org/wiki/Inverse_distance_weighting), but geostatistics methods will be implemented with next releases. 
The crucial inputs of this tool are:
* A feature class with the boundaries of the study area;
* A feature class with the points of the weather stations. This feature class must have a column named **ID**, showing a unique number for each station. If the user wants the tool to compute the lapse rate correction, another field with the altitude of each station is required.
* One ore more tables containing the weather stations data. These datasets must have an ID column to join them to the relative weather station and carry out calculations and interpolation.
* The statistic to compute. At the moment, there are six options: **mean**, **minimum**, **maximum**, **average of daily minimum**, **average of daily maximum** and **chilling hours** (the last one computed considering Wineberger model).
* The reclassification table to reclassify the interpolated raster. 

### 2. **s2ComputeSoilParameterSuitability**
This tool is used to create a suitability raster layer based on a soil parameter (for instance, pH, EC, texture). The suitability distribution is comptued through reclassification of the values of the input raster, through a reclassification table the user must fill in the tool panel. 

### 3. **s3ApplyClimateChangeScenarios**
This tool is used to modify a weather dataset using values extracted from a [RCP](https://en.wikipedia.org/wiki/Representative_Concentration_Pathway) raster layer
containing the predicted increase of air temperature (expressed in °C) for a certain area.
The user can then import the output CSV file as a table in a file Geodatabase and use it as input for the **s1ComputeWeatherParameterSuitability** tool.

### 4. FinalSuitabilityModel
This tool is useful to combine the results of the previous tools into a an expression in the Raster Calculator, in order to obtain a final, global suitability raster layer.

## **Contributions**
If you'd want to contribute as a developer to the project, take these steps to get started:

  1. Fork the toolbox repository (https://github.com/96francesco/suitabox-arcgis)
  2. Create your feature branch (git checkout -b my-new-feature)
  3. Commit your changes (git commit -m 'Add new feature')
  4. Push to the branch (git push origin my-new-feature)
  5. Create a new Pull Request

## **License**
The ArcGIS Toolbox for Suitabox is distributed under the [GPL 3.0 license](https://opensource.org/licenses/GPL-3.0), a copyleft open-source license.

## **Troubleshooting**
Suitabox is distributed as is and without any kind of warranty. If you encounter software errors or bugs please report the issue. Providing a thorough account of the circumstances in which the problem occurred will aid in the bug's identification. Use the [Issues tracker](https://github.com/96francesco/suitabox-arcgis/issues) on GitHub to report bugs in the software and ask for feature enhancements

