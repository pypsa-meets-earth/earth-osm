__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""
This module contains the config for osm features.

"""

# The primary_feature_element represents the final representation of the feature
# For node features: ways are converted to nodes
# For way features: only ways are used

# TODO: Add 'keep' to keep the original feature representation
#%%
# import json
from pprint import pprint
import pandas as pd
# Node (Towers)
# Way (Lines and Cables)
# Area (Substations and Generators)

#%%
# TODO: Add taginfo.json to package data
# TODO: Can be used to get the primary keys and values
# TODO: Implement view features simialr to gfk_data
# taginfo_url='https://raw.githubusercontent.com/openstreetmap/id-tagging-schema/main/dist/taginfo.min.json'
# taginfo = '/home/matin/earth-osm/taginfo.min.json'
# with open(taginfo, encoding='utf8') as f:
#     d = json.load(f)
# tag_dict = d['tags']
# pprint(tag_dict)
# tag_df = pd.DataFrame(tag_dict)

# #%%
# power_df = tag_df.loc[tag_df['key'] == 'power']

# #%%
# power_df.to_dict('records')

# #%%
# by_parent = tag_df.groupby("key")[["value"]].count()

# #%%
# tag_df.drop(['object_types', 'icon_url'], axis=1).value_counts()
# by_parent
# parent_dict = by_parent.groups


#%%
# primary_feature_element = {
#     "power": {
#         "substation": "node", #(node, area)
#         "generator": "node", # (node, way, area)
#         "line": "way", #(way)
#         "tower": "node", #(node)
#         "cable": "way", #(way)
#     }
#     # add more primary features here
# }


primary_feature_element = {
    "power": {
        "substation": ("node", "area"), 
        "generator": ("node", "way", "area"),
        "line": ("way"),
        "tower": ("node"),
        "cable": ("way"),
        }
    # add more primary features here
}


# ===============================
# OSM FEATURE COLUMNS
# ===============================
# These configurations are used to specify which OSM tags are kept as columns in DataFrame.
# Follows the OSM Wiki: https://wiki.openstreetmap.org/wiki/Power


# "Length" is added for way features
# "Area" is added for node features

# ========================
# BASIC INFO TAGS
# ========================
# A list of tags that are relevant for most OSM keys

columns_basic = [
    "id",
    "lonlat",
    "tags.power",
    "Type",
    "Country",
    #"refs"
]

# ========================
# SUBSTATION TAGS
# ========================

# Default tags to keep as columns with substation
# Based on: https://wiki.openstreetmap.org/wiki/Key:substation
columns_substation = [
    "Area",
    "tags.substation",
    "tags.voltage",
    # Other tags which are not kept by default
    # =====================================
    # "TODO:ADD Tags not kept here",
]

# ========================
# GENERATOR TAGS
# ========================

# Default tags to keep as columns with generator
# Based on: https://wiki.openstreetmap.org/wiki/Key:generator

columns_generator = [
    "Area",
    "tags.name",
    "tags.generator:type",
    "tags.generator:method",
    "tags.generator:source",
    "tags.generator:output:electricity",
    # Other tags which are not kept by default
    # =====================================
    # "TODO:ADD Tags not kept here",
]

# ========================
# LINE TAGS
# ========================

# Default tags to keep as columns with line
# Based on: https://wiki.openstreetmap.org/wiki/Key:line

columns_line = [
    "Length",
    "tags.cables",
    "tags.voltage",
    "tags.circuits",
    "tags.frequency",
    # Other tags which are not kept by default
    # =====================================
    # "TODO:ADD Tags not kept here",
]

# ========================
# CABLE TAGS
# ========================

# Default tags to keep as columns with substation
# Based on: https://wiki.openstreetmap.org/wiki/Key:cable

columns_cable = [
    "Length",
    "tags.cables",
    "tags.voltage",
    "tags.circuits",
    "tags.frequency",
    "tags.location",
    # Other tags which are not kept by default
    # =====================================
    # "TODO:ADD Tags not kept here",
]

# ========================
# TOWER TAGS
# ========================

# Default tags to keep as columns with tower
# Based on: https://wiki.openstreetmap.org/wiki/Key:tower

columns_tower = [
    "Area",
    "tags.tower",
    "tags.material",
    "tags.structure",
    "tags.operator",
    "tags.line_attachment",
    "tags.line_management",
    "tags.ref",
    "tags.height",
    # Other tags which are not kept by default
    # =====================================
    # "TODO:ADD Tags not kept here",
]

## FINAL DICTIONARY
feature_columns = {
    "substation": columns_basic + columns_substation,
    "generator": columns_basic + columns_generator,
    "line": columns_basic + columns_line,
    "cable": columns_basic + columns_cable,
    "tower": columns_basic + columns_tower,
}
