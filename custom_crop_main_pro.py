"""
This file is part of Suitabox.

Suitabox is free software: you can redistribute it and/or modify it under the terms of 
the GNU General Public License as published by the Free Software Foundation, either 
version 3 of the License, or (at your option) any later version.

Suitabox is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Suitabox. 
If not, see <https://www.gnu.org/licenses/>.
"""

# imports
import arcpy
from arcpy.sa import *
import pandas as pd
import os
import locale

# settings
arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False
separator = locale.localeconv()["decimal_point"]
pathname = os.path.realpath(__file__)
pathname = pathname.split("custom")[0]

# user inputs
param = arcpy.GetParameter(0)
record_set = arcpy.RecordSet(param)
record_set.save("{}\\record_set".format(pathname))

# define function for table to pd.DataFrame object conversion
def read_arcpy_table(table, fields='*', null_value=None):
    """
    table : Path the table
    fields : Fields to load - '*' loads all fields
    null_value : choose a value to replace null values
    """
    fields_type = {f.name: f.type for f in arcpy.ListFields(table)}
    if fields == '*':
        fields = fields_type.keys()
    fields = [f.name for f in arcpy.ListFields(table) if f.name in fields]
    fields = [f for f in fields if f in fields_type and fields_type[f] != 'Geometry'] # Remove Geometry field if FeatureClass to avoid bug

    # Transform in pd.Dataframe
    np_array = arcpy.da.FeatureClassToNumPyArray(in_table=table,
                                                 field_names=fields,
                                                 skip_nulls=False,
                                                 null_value=null_value)
    df = pd.DataFrame(np_array)
    return df

# calle the functio
df = read_arcpy_table(table=pathname + "\\record_set.dbf")

# fix and export csv file
df = df.drop(["OID", "OBJECTID"], 1)
df = pd.DataFrame(df)
df.to_csv("{}\\custom_params.csv".format(pathname), index=False)

# remove table from directory
os.remove("{}\\record_set.dbf".format(pathname))
os.remove("{}\\record_set.cpg".format(pathname))