__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""
This is the principal module of the earth_osm project.
"""

import logging
import os

import pandas as pd

from earth_osm.config import primary_feature_element, feature_columns
from earth_osm.filter import get_filtered_data
from earth_osm.gfk_data import get_region_tuple
from earth_osm.utils import convert_ways_lines, convert_ways_points, output_creation


logger = logging.getLogger("osm_data_extractor")
logger.setLevel(logging.INFO)

# TODO: Rename to process_region
def process_country(region, primary_name, feature_name, mp, update, data_dir):
    """
    Process Country

    Args:
        region: Region object
        primary_name: Primary Feature Name
        feature_name: Feature Name
        mp: Multiprocessing object
        update: Update flag

    Returns:
        None
    """
    primary_dict, feature_dict = get_filtered_data(region, primary_name, feature_name, mp, update, data_dir)

    primary_data = primary_dict['Data']
    feature_data = feature_dict['Data']

    df_node = pd.json_normalize(feature_data["Node"].values())
    df_way = pd.json_normalize(feature_data["Way"].values())

    element_type = primary_feature_element[primary_name][feature_name]

    if element_type == "way":
        convert_ways_lines(
            df_way, primary_data
        ) if not df_way.empty else logger.warning(
            f"Empty Way Dataframe for {feature_name} in {region.short}"
        )
        if not df_node.empty:
            logger.warning(
                f"Node dataframe not empty for {feature_name} in {region.short}"
            )

    if element_type == "node":
        convert_ways_points(df_way, primary_data) if not df_way.empty else None

    # Add Original Type Column
    df_node["Type"] = "Node"
    df_way["Type"] = "Way"

    # Concatinate Nodes and Ways
    df_feature = pd.concat([df_node, df_way], axis=0)

    # Add Country Column
    # TODO: rename Country to Region
    df_feature["Country"] = region.short

    return df_feature


def get_osm_data(
    region_list=['germany'],
    primary_name='power',
    feature_list=['tower'],
    update=False,
    mp=True,
    data_dir=os.path.join(os.getcwd(), 'earth_data'),
    out_format="csv",
    out_aggregate=False,
):
    """
    Get OSM Data for a list of regions and features
    args:
        region_list: list of regions to get data for
        primary_name: primary feature to get data for
        feature_list: list of features to get data for
        update: update data
        mp: use multiprocessing
    returns:
        dict of dataframes
    """
    region_tuple_list = [get_region_tuple(rs) for rs in region_list]

    for region in region_tuple_list:
        for feature_name in feature_list:
            df_feature = process_country(region, primary_name, feature_name, mp, update, data_dir)
            df_feature = df_feature.reindex(columns=feature_columns[feature_name])
            output_creation(df_feature, primary_name, feature_name, [region], data_dir, out_format, out_aggregate)
