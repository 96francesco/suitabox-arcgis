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
Double-click on a tool within the toolbox to open it and start using it. Please see the tool metadata/help documentation for more information on how to use each tool.

## Tools
At the moment, Suitabox only has two tools. Updates with new tools will be made available soon. **Crop Suitability tool** is the core instrument of this toolbox, while **Custom Crop Pre-Processing** serves as a support for the *Custom Crop* option in the former tool.

<img src="https://user-images.githubusercontent.com/88101466/181483773-20e0213c-355a-4e5d-83bb-6cdd4648fb84.jpg" width="900" height="400">

<img src="https://user-images.githubusercontent.com/88101466/181484001-4aa46103-3ddd-4be0-aaaa-7b8918524215.jpg" width="900" height="300">

The flowchart below shows the interrelationship between the different modules.
<img src="https://user-images.githubusercontent.com/88101466/186447511-d403232c-6c89-47ba-8426-8e2647c45077.png" width="800" height="450">

Crop Suitability Tool is the core tool of Suitabox. Its main purpose is to produce, for a given area of study and meteorological conditions, a suitability map of the considered crop species. 
The inputs required to the user in the Crop Suitability tool have been divided into 5 categories:
  1) *General inputs*, where the user is asked to specify:
      - The *Crop species*, choosing one of the default crops (avocado, kiwifruit, European hazelnut or walnut) or the costum crop option. For each one of these crops, different temperature thresholds or requirements have been identified based on literature references and implemented within the code. 
      - The *Cultivar*, required depending on the selected *Crop species* option. This input is essential since winter chilling requirements are cultivar-specific. The chilling requirements are computed following only the Chilling Hours model (Weinberger, 1950) so far, but hopefully, different methods will be available with new releases.
      - *Borders of the study area*, in ESRI shapefile extension (.shp).
      - *Weather stations*, i.e., A point feature layer (.shp) containing the weather stations location. The feature attribute table must have an *ID* column with an integer and unique number for each station. If the user wants to use the *topographic correction* option (explained later), this shapefile must also have an additional column (named *alt*) with the altitude in meters of each meteorological station.
      - *Weather hourly data*, i.e., the dataset(s) obtained from the weather stations, with **hourly resolution**. The user can upload one dataset per year. This dataset must have the following columns: i) an ID column to be joined with the weather stations layer, in integer type; ii) a Day of Year (DoY) column in integer type; iii) an air temperature (Tair) column with the temperature data. If the user selects a crop with a winter chilling hours requirement (i.e. kiwifruit, walnut, hazelnut, or custom crop) the dataset must cover a hydrological year (i.e., from 01 October of year n to 30 September of year n+1) to refer the chilling hours’ calculation to that specific season.
      - The *topographic correction* option. The user can **optionally** (but strongly recommended) upload a Digital Elevation Model (DEM) raster layer (.tif). If provided, the script tool will compute a correction of the interpolated air temperature using the terrain altitude. The temperature will be corrected (Tair.corr) using the following formula, which applies the average environmental lapse rate factor (6.5 ºC/km) through a DEM obtained via interpolation of the altitude (alt) field of the weather stations layer.
  2) *Custom periods*: the temperature-based parameters considered for each crop relate to a specific time of the year. Thanks to this information, the relevant data for each parameter are extracted from the weather dataset via the DoY column. Since the same crop can show a slightly different behavior and responses in two distinct locations, this input category allows the user to change, for each specific phenological phase (i.e., growing season, budding, flowering, fruit set and growth, chilling hours accumulation), the DoY range considered to extract the Tair data needed for evaluating the thresholds/requirements of the selected crop. By default, the considered periods are the ones included in the table below. The user should include the initial and final DoY separated by a dash. If the user does not modify the text inside these boxes (i.e., leaving the dash inserted by default), the standard periods will be used. As shown in the table below, not all the considered periods are related to each default crop, depending on the literature references found in bibliography so far, i.e., when the user selects a crop species only some specific periods will be customizable. <img src="https://user-images.githubusercontent.com/88101466/186457910-0abc8c50-91ed-4b49-a5f2-3b60cdc71ac3.png" width="600" height="300">

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

