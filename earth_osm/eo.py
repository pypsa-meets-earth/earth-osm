__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""
This is the principal module of the earth_osm project.
"""

import os
import pandas as pd
import logging

from earth_osm.gfk_data import get_region_tuple
from earth_osm.utils import convert_ways_lines, convert_ways_points, output_csv_geojson
from earth_osm.filter import get_filtered_data
from earth_osm.config import primary_feature_element

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
    df_feature["Country"] = region.name

    return df_feature
