__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Geofabrik Data Config

This module contains functions to set config for Geofabrik data.

"""


import os
import geopandas as gpd
import pandas as pd
import json
from collections import namedtuple

from earth_osm.gfk_download import download_sitemap

import logging
logger = logging.getLogger("osm_data_extractor")
logger.setLevel(logging.DEBUG)


pkg_data_dir = os.path.join(os.path.dirname(__file__), 'data')
sitemap = download_sitemap(False, pkg_data_dir)

with open(sitemap) as f:
    d = json.load(f)

row_list =[]
for feature in d['features']:
    row_list.append(feature['properties'])
df = pd.DataFrame(row_list)
# Add short code column
col1 = df['iso3166-1:alpha2'].apply(lambda x: '-'.join(x) if type(x) == list else x)
col2 = df['iso3166-2'].apply(lambda x: '-'.join(x) if type(x) == list else x)
df['short_code'] = col1.combine_first(col2)

def get_geom_sitemap():
    geom_sitemap = download_sitemap(True, pkg_data_dir)
    return gpd.read_file(geom_sitemap)


def get_root_list():
    """
    Returns a list of regions without parents (i.e continents)
    """
    return list(df.loc[df['parent'].isna(), 'id'])

def get_all_valid_list():
    """
    Returns a list of all valid region ids
    """
    return list(df.loc[~df['short_code'].isna(), 'short_code']) + list(df['id'])

def get_all_regions_dict(level=0):
    """
    It takes a level argument, and returns a dictionary of all regions, grouped by their parent region
    
    Args:
        level: 0 = all regions, 1 = world regions, 2 = local regions, defaults to 0
        A dictionary of dictionaries.
    """
    by_parent = df.groupby("parent", as_index=False)[["id", "short_code"]]
    parent_dict = by_parent.groups
    root = get_root_list()
    world_dict = {}
    local_dict = {}
    def dict_by_key(key): return by_parent.get_group(key).set_index('id').T.to_dict('records')[0]
    for key in parent_dict:
        if key in root:
            world_dict[key] = dict_by_key(key)
        else:
            local_dict[key] = dict_by_key(key)
    
    if level == 0:
        return {**world_dict, **local_dict}
    if level == 1:
        return world_dict
    if level == 2:
        return local_dict

def view_regions(level=0):                                                                              
    """
    Takes the `all_regions` dictionary and returns a new dictionary with the same keys, but with
    the values being the `region_id`s of the regions
    """
    all_dict = get_all_regions_dict(level)
    view_df = pd.DataFrame.from_dict({(i,j): all_dict[i][j] 
                            for i in all_dict.keys() 
                            for j in all_dict[i].keys()},
                            orient='index')
    view_df.index = pd.MultiIndex.from_tuples(view_df.index, names=['parent', 'id'])
    print(view_df.to_string())
