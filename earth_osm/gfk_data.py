__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Geofabrik Data Config

This module contains functions to set config for Geofabrik data.

"""


import ast
import json
import logging
import os
from collections import namedtuple
from datetime import datetime
from typing import Optional

import geopandas as gpd
import pandas as pd

from earth_osm.gfk_download import download_sitemap
from earth_osm.planet import (
    PLANET_REGION_ID,
    PLANET_REGION_SHORT_CODE,
    get_planet_region_dict,
)
logger = logging.getLogger("eo.gfk")
logger.setLevel(logging.INFO)

pkg_data_dir = os.path.join(os.path.dirname(__file__), "data")
csv_path = os.path.join(pkg_data_dir, "gfk_index.csv")

def load_geofabrik_data():
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path, keep_default_na=False, na_values=[''])
    else:
        logger.warning("CSV file not found. Please run the script as __main__ to generate it.")
        return pd.DataFrame()

df = load_geofabrik_data()


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
    codes = list(df.loc[~df['short_code'].isna(), 'short_code'])
    ids = list(df['id'])

    if PLANET_REGION_SHORT_CODE not in codes:
        codes.append(PLANET_REGION_SHORT_CODE)
    if PLANET_REGION_ID not in ids:
        ids.append(PLANET_REGION_ID)

    return codes + ids


def get_children_regions(parent_id, require_iso=True):
    """Return child regions of a parent as Region tuples.

    Args:
        parent_id: Parent region identifier (e.g. 'europe').
        require_iso: When True, only include children with a valid ISO short code.

    Returns:
        List of Region namedtuples for each child.
    """

    if parent_id == PLANET_REGION_ID:
        return []

    children = df.loc[df['parent'] == parent_id]
    if children.empty:
        return []

    if require_iso:
        children = children[
            children['short_code'].notna() & (children['short_code'].astype(str).str.strip() != '')
        ]

    return [get_region_tuple(child_id) for child_id in children['id'].tolist()]

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

    def dict_by_key(key):
        return by_parent.get_group(key).set_index("id").T.to_dict("records")[0]

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
        {(i, j): all_dict[i][j] for i in all_dict.keys() for j in all_dict[i].keys()},
        orient="index",
    )
    view_df.index = pd.MultiIndex.from_tuples(view_df.index, names=["parent", "id"])
    return view_df


def get_region_dict(id):
    """
    Takes a region id (eg. germany) and returns a ditctionary consisting of
    strings 'id', 'name', 'parent', 'short_code' and dictionary of 'urls'
    Raises error if id is not found
    """
    if str(id) == PLANET_REGION_ID:
        return get_planet_region_dict()

    region_data = (
        df.loc[df["id"] == id]
        .drop("iso3166-1:alpha2", axis=1)
        .drop("iso3166-2", axis=1)
        .to_dict("records")[0]
    )
    region_data["urls"] = ast.literal_eval(region_data["urls"])
    return region_data


def get_id_by_code(code):
    """
    Takes a region code (eg. DE) and returns its id (eg. germany)
    Supresses error if id is not found
    """
    if code is None:
        return None

    normalized = str(code).strip()
    if not normalized:
        return None

    if normalized.upper() == PLANET_REGION_SHORT_CODE or normalized.lower() == PLANET_REGION_ID:
        return PLANET_REGION_ID

    try:
        return df.loc[df["short_code"] == normalized, "id"].item()
    except (KeyError, ValueError):
        logger.debug(f"{code} not found, probably an id")
        return None


def get_code_by_id(id):
    """
    Takes a region id (eg. germany) and returns its code (eg. DE)
    Supresses error if id is not found
    """
    if str(id) == PLANET_REGION_ID:
        return PLANET_REGION_SHORT_CODE

    try:
        c_dict = get_region_dict(id)
    except (KeyError, IndexError):
        logger.debug(f"{id} not found")
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
            logger.error(
                f"{region_str} not found. Check eo.view_regions() or run 'earth_osm view regions'"
            )
            raise KeyError(
                f"{region_str} not found. Check eo.view_regions() or run 'earth_osm view regions'"
            )


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
    d["short"] = d.pop("short_code")
    if str(d["short"]) == "nan":
        logger.warning(f"code not found for {id} so using id")
        d["short"] = d["id"]

    Region = namedtuple("Region", d)
    region_tuple = Region(**d)
    return region_tuple


def get_region_base_url(region_tuple) -> str:
    """
    Extract the base directory URL from a region's PBF URL

    Args:
        region_tuple: Named tuple with region information including URLs

    Returns:
        str: Base URL for the region directory (e.g., 'https://download.geofabrik.de/africa/')
    """
    pbf_url = region_tuple.urls["pbf"]
    # Extract base URL by removing the filename
    # e.g., 'https://download.geofabrik.de/africa/benin-latest.osm.pbf' -> 'https://download.geofabrik.de/africa/'
    base_url = "/".join(pbf_url.split("/")[:-1]) + "/"
    return base_url


def get_region_tuple_historical(region_str: str, target_date: Optional[datetime] = None):
    """
    Enhanced version of get_region_tuple that supports historical date specification

    Args:
        region_str (str): Region identifier or code (e.g., 'DE', 'germany')
        target_date (datetime, optional): Target date for historical data. If None, returns latest.

    Returns:
        Named tuple with region information including historical URL support
    """
    region_tuple = get_region_tuple(region_str)

    # Add historical support fields
    region_dict = region_tuple._asdict()
    region_dict["target_date"] = target_date
    region_dict["base_url"] = get_region_base_url(region_tuple)

    # Create new named tuple type with additional fields
    RegionHistorical = namedtuple("RegionHistorical", region_dict.keys())
    return RegionHistorical(**region_dict)


def generate_markdown_table(output_md):
    """
    Generates a markdown table of regions and saves it to a file.
    """
    md_table = "| Parent | ID | ISO Code |\n|---|---|---|\n"

    for parent, children in get_all_regions_dict().items():
        md_table += f"| **{parent}** | | |\n" if parent else ""
        for id, short_code in children.items():
            short_code = "" if str(short_code) == "nan" else short_code
            md_table += f"| | {id} | {short_code} |\n"

    with open(output_md, "w") as f:
        f.write(md_table)

    logger.info(f"Markdown table saved to {output_md}")


if __name__ == "__main__":
    sitemap = download_sitemap(False, pkg_data_dir)

    with open(sitemap, encoding="utf8") as f:
        d = json.load(f)

    df = pd.DataFrame(feature["properties"] for feature in d["features"])

    # Add short code column
    def join_func(x):
        return "-".join(x) if isinstance(x, list) else x

    col1 = df["iso3166-1:alpha2"].apply(join_func)
    col2 = df["iso3166-2"].apply(join_func)
    df["short_code"] = col1.combine_first(col2)

    # Save the DataFrame as CSV
    df.to_csv(csv_path, index=False)
    print(f"DataFrame saved to {csv_path}")

    # Generate markdown table
    output_md = "docs/generated-docs/regions_table.md"
    generate_markdown_table(output_md)
