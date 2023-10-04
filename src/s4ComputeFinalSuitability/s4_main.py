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

## USER INPUTS
parameters = arcpy.GetParameterAsText(0).split(';')
output_name = arcpy.GetParameterAsText(1) 

## CONSTANTS
## they are still treated as variable, i.e., named with lower-case lettersm
## since their value can change according to user necessities. 

arcpy.env.overwriteOutput = True  # tool will overwrite the output dataset
arcpy.env.qualifiedFieldNames =  False  # output field name won't include the table name
                                        # this setting is crucial for the correct reading 
                                        # of the the feature attribute tables
arcpy.env.workspace = "memory"  # set workspace in memory


## EXECUTION

if __name__ == "__main__":
      # check if the user has provided at least one raster
      if not parameters:
            arcpy.AddError("No rasters provided")
            exit()
      
      parameters = [arcpy.Raster(raster) for raster in parameters]
      sum_raster = CellStatistics(parameters, "SUM", "DATA")

      # get minimum and maximum values
      min_result = arcpy.GetRasterProperties_management(sum_raster, "MINIMUM")
      min_value = float(min_result.getOutput(0))

      max_result = arcpy.GetRasterProperties_management(sum_raster, "MAXIMUM")
      max_value = float(max_result.getOutput(0))

      # normalise the raster between 0 and 3
      normalised_raster = (sum_raster - min_value) / (max_value - min_value) * 3

      # round the values to the nearest integer
      rounded_raster = Con(normalised_raster < 0.5, 0, 
                        Con(normalised_raster < 1.5, 1, 
                         Con(normalised_raster < 2.5, 2, 3)))

      # save the raster to a file geodatabase
      arcpy.CopyRaster_management(rounded_raster, output_name)