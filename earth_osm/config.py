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

primary_feature_element = {
    "power": {
        "substation": "node",
        "generator": "node",
        "line": "way",
        "tower": "node",
        "cable": "way",
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
