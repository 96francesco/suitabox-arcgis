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
import sys

sys.path.insert(1, 'src')


## USER INPUTS
soil_data = arcpy.GetParameterAsText(0)
reclass_table = arcpy.GetParameter(1)
output_name = arcpy.GetParameterAsText(2) 


## CONSTANTS
## they are still treated as variable, i.e., named with lower-case lettersm
## since their value can change according to user necessities. 

arcpy.env.overwriteOutput = True  # tool will overwrite the output dataset
arcpy.env.qualifiedFieldNames =  False  # output field name won't include the table name
                                        # this setting is crucial for the correct reading 
                                        # of the the feature attribute tables
arcpy.env.workspace = "memory"  # set workspace in memory


## EXECUTION

if __name__ == '__main__':

      # import required functions
      from reclassify_raster import reclassify_raster
      
      reclassified_raster = reclassify_raster(
            soil_data, reclass_table, output_name
      )