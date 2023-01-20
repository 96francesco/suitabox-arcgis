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
from join_data_to_stations import join_data_to_stations




def interpolate_weather_parameter(power, search_radius, cell_size):
    """
    Do the IDW of the computed statistics using the weather stations'
    points. The function will produce an interpolated raster layer of 
    the desired statistics for each weather dataset uploaded by the 
    user. Each interpolated raster will be appended to a list, which
    is returned as output of this function

    Parameters
    ----------
    power:      str
                    The power to use to compute IDW.
    search_radius:    str
                            The search radius for the IDW.
    cell_size:  int
                    The desired pixel size of the final output.
    """

    def compute_interpolation(stations_with_data):
        """
        Helper function to execute the actual interpolation.
        
        Parameters
        ----------
        stations_with_data:     Feature class
                                            The stations' points feature class obtained
                                            after the join with the statistics dataframe.
        """
        
        # do the actual interpolation
        interpolated_raster = Idw(
            stations_with_data, "STAT", cell_size, power, search_radius
        )

        # return each interpolated raster for each weather dataset
        return interpolated_raster

    # loop to iterate over the list of dataframes created
    for table in arcpy.ListTables():
        table_index = table.split("_")[2]
        joined_ws = join_data_to_stations(table_index)
        interpolated_raster = compute_interpolation(
            joined_ws, cell_size, power, search_radius
        )
        interpolated_raster.save("memory/idw_raster_{}".format(table_index))
    
    # create the list of all the interpolated rasters
    interpolated_param_layers = [f for f in arcpy.ListRasters() if f.startswith("idw")]
    
    return interpolated_param_layers