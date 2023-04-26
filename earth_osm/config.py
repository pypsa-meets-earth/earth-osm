__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""
This module contains the config for osm features.

"""

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
# %%
# import json
# from pprint import pprint
# import pandas as pd
# TODO: Add taginfo.json to package data, 
# can be used to get the primary keys and values
# TODO: Implement view features simialr to gfk_data
# taginfo_url='https://raw.githubusercontent.com/openstreetmap/id-tagging-schema/main/dist/taginfo.min.json'
# taginfo = '/home/matin/Projects/earth-osm/earth_osm/data/taginfo.min.json'
# with open(taginfo, encoding='utf8') as f:
#     d = json.load(f)
# tag_dict = d['tags']
# pprint(tag_dict)
# tag_df = pd.DataFrame(tag_dict)

