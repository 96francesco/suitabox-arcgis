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

def reclassify_raster(in_raster, remap_table, out_name):
      """
      Reclassify the input raster according to the remap table 
      uploaded by user.

      Parameters
      ----------
      in_raster:  Raster layer
                              The raster layer to reclassify.
      remap_table:      Remap table
                                    The remap table uploaded by 
                                    the user.
      out_name:   Raster Dataset
                        The name of the output, saved to a file
                        Geodatabase.
      
      Returns
      -------
      reclassified_raster:    Raster Dataset
                              The reclassified raster, saved 
                              in a file Geodatabase.
      """

      # make a raster layer of the average raster
      raster_layer = arcpy.MakeRasterLayer_management(in_raster, "raster_layer")

      # reclassify according to the remap table
      reclassified_raster = Reclassify(raster_layer, "Value", remap_table)
      reclassified_raster = Float(reclassified_raster)
      arcpy.CopyRaster_management(
            reclassified_raster, out_name
      )

      return reclassified_raster