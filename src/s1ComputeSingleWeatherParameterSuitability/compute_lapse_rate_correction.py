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

from arcpy.sa import *

def compute_lapse_rate_correction(
    interpolated_weather_param, stat, points, alt_field, cell_size, power, search_radius, dem
):
      """
      Create a raster layer to perform the lapse rate correction of the
      interpolated raster (relative to the considered weather parameter)
      obtained with this tool. 

      Parameters
      ----------
      interpolated_weather_param:         list
                                                The list of raster layers obtained
                                                through interpolation of the 
                                                considered weather parameter 
                                                (for each dataset/year uploaded by 
                                                the user).
      stat:       str
                        The statistics to compute.
      points:     Feature class
                              The feature class containing the weather stations'
                              points.
      alt_field:  str
                        The altitude field of the points feature class.
      cell_size:  int
                        The desired pixel size of the final output.
      power:      str
                        The power to use to compute IDW.
      search_radius:    str
                              The search radius for the IDW.
      dem:  str
                  Directory to a DEM raster layer
      """

      def create_lapse_rate_layer():
            """
            Create the necessary lapse rate layer. This layer is computed interpolating
            the weather stations's points using the altitude field, subtracting the
            actual DEM from this raster layer, and multiplying it by 0.0065 (the factor
            to implement the lapse rate correcton of air temperature).
            """
            interpolated_dem = Idw(points, alt_field, cell_size, power, search_radius)
            dem_difference = interpolated_dem - dem
            lapse_rate_correction = dem_difference * 0.0065

            return (dem_difference, lapse_rate_correction)

      dem_difference, lapse_rate_layer = [
            create_lapse_rate_layer()[0],
            create_lapse_rate_layer()[1],
      ]

      for i, f in enumerate(interpolated_weather_param):
            if stat != "chilling hours":
                  interpolated_weather_param[i] = f + lapse_rate_layer
            else:
                  interpolated_weather_param[i] = Con(
                  (dem_difference >= -400), f - (-0.0032 * (dem_difference) ** 2), f
                  )

      return interpolated_weather_param