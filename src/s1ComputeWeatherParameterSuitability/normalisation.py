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

def normalise_raster(in_raster, out_name):
      """
      Normalise the raster values to 0 to 1 scale, using 
      values 0, 0.33, 0.66 and 1.
      """
      normalised_raster = Con(in_raster == 0, 0,
                              Con(in_raster == 1, 0.33,
                                    Con(in_raster == 2, 0.66,
                                          Con(in_raster == 3, 1, 0))))
      arcpy.CopyRaster_management(
            normalised_raster, 
            "{}_normalised".format(out_name),
      )

      return normalised_raster