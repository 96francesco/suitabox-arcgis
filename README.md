<a href="https://www.repostatus.org/#active"><img src="https://www.repostatus.org/badges/latest/active.svg" alt="Project Status: Active – The project has reached a stable, usable state and is being actively developed." /></a>
[![License: GPL-3.0](https://img.shields.io/github/license/96francesco/suitabox-arcgis)](https://opensource.org/licenses/GPL-3.0)

# Suitabox
This is the repository of Suitabox, an ArcGIS Pro custom toolbox written in Python (using ArcPy).

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


# **Tools**
### 1. **s1ComputeWeatherParameterSuitability**
This tool is used to create a suitability raster layer based on a chosen weather parameter. 

### 2. s2ComputeSoilParameterSuitability
This tool is used to create a suitability raster layer based on a soil parameter (for instance, pH, EC, texture).

### 3. FinalSuitabilityModel
This tool, built on the ModelBuilder, is useful to combine the results of the previous tools into a an expression in the Raster Calculator, in order to obtain a final, global suitability raster layer. To use it properly, double-click on the tool icon and click **Edit**. This way, users can copy/paste the previous tools more times inside the model diagram in order to reiterate the computation over more parameters, and then connecting the output of each iteration to the Raster Calculator as **Precondition**. Users can implement their own final suitability score calculation (for instance, a weighted calculation). 

# **Contributions**
If you'd want to contribute as a developer to the project, take these steps to get started:

  1. Fork the toolbox repository (https://github.com/96francesco/suitabox-arcgis)
  2. Create your feature branch (git checkout -b my-new-feature)
  3. Commit your changes (git commit -m 'Add new feature')
  4. Push to the branch (git push origin my-new-feature)
  5. Create a new Pull Request

# **License**
The ArcGIS Toolbox for Suitabox is distributed under the [GPL 3.0 license](https://opensource.org/licenses/GPL-3.0), a copyleft open-source license.

# **Troubleshooting**
Suitabox is distributed as is and without any kind of warranty. If you encounter software errors or bugs please report the issue. Providing a thorough account of the circumstances in which the problem occurred will aid in the bug's identification. Use the [Issues tracker](https://github.com/96francesco/suitabox/issues) on GitHub to report bugs in the software and ask for feature enhancements

