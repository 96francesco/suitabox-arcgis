<a href="https://www.repostatus.org/#active"><img src="https://www.repostatus.org/badges/latest/active.svg" alt="Project Status: Active – The project has reached a stable, usable state and is being actively developed." /></a>
[![License: GPL-3.0](https://img.shields.io/github/license/96francesco/suitabox)](https://opensource.org/licenses/GPL-3.0)

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

  ![image](https://user-images.githubusercontent.com/88101466/171162778-f837c111-34aa-4053-b9ae-2cbb2a710eea.png)

# **Usage**
Double-click on a tool within the toolbox to open it and start using it. Please see the tool metadata/help documentation for more information on how to use each tool.

## Tools
At the moment, Suitabox only has two tools. Updates with new tools will be made available soon. **Crop Suitability tool** is the core instrument of this toolbox, while **Custom Crop Pre-Processing** serves as a support for the *Custom Crop* option in the former tool.

<img src="https://user-images.githubusercontent.com/88101466/171174916-9a98799d-f278-4030-9fa8-c46d68f39dcd.jpg" width="700" height="600">

<img src="https://user-images.githubusercontent.com/88101466/171177297-a5c7398b-7f74-4853-abb2-6241bf789bb0.png" width="900" height="300">

## Contributions
If you'd want to contribute as a developer to the project, take these steps to get started:

  1. Fork the toolbox repository (https://github.com/96francesco/suitabox)
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

