"""
This file is part of Suitabox.

Suitabox is free software: you can redistribute it and/or modify it under the terms of 
the GNU General Public License as published by the Free Software Foundation, either 
version 3 of the License, or (at your option) any later version.

Suitabox is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Foobar. 
If not, see <https://www.gnu.org/licenses/>.
"""

import arcpy
from arcpy.sa import *

def compute_average_raster(single_year_rasters, study_area):
      """
      Take all the interpolated rasters (related to each single weather
      dataset uploaded by the user) and calculate the average result.

      Parameters
      ----------
      single_year_rasters:      list
                                          List of raster layers
      study_area:       Feature class
                                    The borders of the study area,
                                    used to clip the average raster 
      """
      
      average_raster = CellStatistics(single_year_rasters, "MEAN")
      average_raster = ExtractByMask(average_raster, study_area)

      return average_raster


def reclassify_raster(in_raster, remap_table, out_name):
      """
      Reclassify the average raster according to the remap table 
      uploaded by user.

      Parameters
      ----------
      in_raster:  Raster layer
                              The average raster layer.
      remap_table:      Remap table
                                    The remap table uploaded by 
                                    the user.
      out_name:   Raster Dataset
                        The name of the output, saved to a file
                        Geodatabase
      """

      # make a raster layer of the average raster
      raster_layer = arcpy.MakeRasterLayer_management(in_raster, "raster_layer")

      # reclassify according to the remap table
      reclassified_raster = Reclassify(raster_layer, "Value", remap_table)

      # save the reclassified raster to a file geodatabase
      arcpy.CopyRaster_management(
            reclassified_raster, out_name
      )

      return reclassified_raster