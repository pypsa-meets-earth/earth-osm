__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Geofabrik Data Config

This module contains functions to set config for Geofabrik data.

"""


import json
import logging
import os
from collections import namedtuple

import geopandas as gpd
import pandas as pd

from earth_osm.gfk_download import download_sitemap
from earth_osm import logger as base_logger

logger = logging.getLogger("eo.gfk")
logger.setLevel(logging.INFO)


pkg_data_dir = os.path.join(os.path.dirname(__file__), "data")
sitemap = download_sitemap(False, pkg_data_dir)

with open(sitemap, encoding='utf8') as f:
    d = json.load(f)

df = pd.DataFrame(feature['properties'] for feature in d['features'])
# Add short code column
join_func = lambda x: '-'.join(x) if isinstance(x, list) else x
col1 = df['iso3166-1:alpha2'].apply(join_func)
col2 = df['iso3166-2'].apply(join_func)
df['short_code'] = col1.combine_first(col2)

def get_geom_sitemap(progress_bar=True):
    geom_sitemap = download_sitemap(True, pkg_data_dir, progress_bar=progress_bar)
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
    view_df = pd.DataFrame.from_dict(
        {
            (i, j): all_dict[i][j]
                            for i in all_dict.keys() 
            for j in all_dict[i].keys()
        },
        orient='index',
    )
    view_df.index = pd.MultiIndex.from_tuples(view_df.index, names=['parent', 'id'])
    return view_df


def get_region_dict(id):
    """
    Takes a region id (eg. germany) and returns a ditctionary consisting of
    strings 'id', 'name', 'parent', 'short_code' and dictionary of 'urls'
    Raises error if id is not found
    """
    return (
        df.loc[df['id'] == id]
        .drop('iso3166-1:alpha2', axis=1)
        .drop('iso3166-2', axis=1)
        .to_dict('records')[0]
    )


def get_id_by_code(code):
    """
    Takes a region code (eg. DE) and returns its id (eg. germany)
    Supresses error if id is not found
    """
    try:
        return df.loc[df['short_code']== code, 'id'].item()
    except (KeyError, ValueError):
        logger.debug(f'{code} not found, probably an id')
        return None


def get_code_by_id(id):
    """
    Takes a region id (eg. germany) and returns its code (eg. DE)
    Supresses error if id is not found
    """
    try:
        c_dict = get_region_dict(id)
    except (KeyError, IndexError):
        logger.debug(f'{id} not found')
        return None

    code = str(c_dict["short_code"])
    return code


def get_id_by_str(region_str):
    """
    Takes a region id or code (eg. DE, germany) and returns its id (eg. germany)
    Raises error if the string is not a valid id or code
    """
    # if region_str is region code
    id = get_id_by_code(region_str) 
    if id is not None: 
        return id
    else:
    # if region_str is region id
        code = get_code_by_id(region_str)
        if code is not None:
            return region_str
        else:
            logger.error(f"{region_str} not found. Check eo.view_regions() or run 'earth_osm view regions'")
            raise KeyError(f"{region_str} not found. Check eo.view_regions() or run 'earth_osm view regions'")


def get_region_tuple(region_str):
    """
    Takes a region id or code (eg. DE, germany) and returns a named tuple with 
    'id', 'name', 'short', 'parent', 'short_code' and dictionary of 'urls'
    The 'short' field is an iso code if found otherwise the id is used.
    iso3166-1:alpha2 is used for countries, iso3166-2 is used for sub-divisions
    Raises error if the string is not a valid id or code
    """
    id = get_id_by_str(region_str)
    d = get_region_dict(id)
    d['short'] = d.pop('short_code')
    if str(d['short']) == 'nan':
        logger.warning(f'code not found for {id} so using id')
        d['short'] = d['id']

    Region = namedtuple('Region', d)
    region_tuple = Region(**d)
    return region_tuple

if __name__ == "__main__":
    df = view_regions(level=1)
    print(df.head())
    print(df.to_string())
    print(list(df.index.levels[0]))
    # view_regions(level=1)