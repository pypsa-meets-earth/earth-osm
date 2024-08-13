__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Filter the Extracted OSM Data

This module filters the extracted OSM data.

"""

import json
import logging
import os
from datetime import datetime

from earth_osm.tagdata import get_feature_list
from earth_osm.extract import filter_pbf
from earth_osm.gfk_download import download_pbf
from earth_osm.osmpbf import Node, Relation, Way
from earth_osm import logger as base_logger

logger=logging.getLogger("eo.filter")
logger.setLevel(logging.WARNING)


def feature_filter(primary_data, filter_tuple = ('power', 'line')):

    if set(primary_data.keys()) != set(['Node', 'Way', 'Relation']):
        logger.error('malformed primary_data')

    feature_data = {'Node': {}, 'Way': {}, 'Relation': {}}
    for element in list(feature_data.keys()):
        for id in primary_data[element]:
            if filter_tuple in primary_data[element][id]["tags"].items():
                feature_data[element][id] = primary_data[element][id]
    return feature_data


def run_feature_filter(primary_dict, feature_name):
    if feature_name[:4] == 'ALL_':
        logger.info('Using ALL wildcard, so feature filter is skipped')
        return primary_dict
    
    primary_name = primary_dict['Metadata']['primary_feature']
    filter_tuple = (primary_name, feature_name)
    primary_data = primary_dict['Data']

    feature_data = feature_filter(primary_data, filter_tuple)

    metadata = {
        'filter_date': str(datetime.now().isoformat()),
        'filter_tuple': json.dumps(filter_tuple),
    }

    feature_dict = {
        'Metadata': metadata,
        'Data':feature_data
        }

    return feature_dict

def run_primary_filter(PBF_inputfile, primary_file, primary_name, multiprocess):
    logger.info('New Pre-Filter Data')
    logger.info('Load OSM data from '+ PBF_inputfile+'\n')

    feature_list = get_feature_list(primary_name)
    pre_filter = {
        Node: {primary_name: feature_list},
        Way: {primary_name: feature_list},
        Relation: {primary_name: feature_list},
    }

    primary_data = filter_pbf(PBF_inputfile, pre_filter, multiprocess)

    metadata = {
        'filter_date': str(datetime.now().isoformat()),
        'primary_feature': primary_name,
    }
    primary_dict = {
        'Metadata': metadata,
        'Data': primary_data
    }
    # Save primary_dict
    with open(primary_file, "w", encoding="utf-8") as target:
        json.dump(
            primary_dict,
            target,
            ensure_ascii=False,
            indent=4,
            separators=(",", ":"),
        )

    return primary_dict


def get_filtered_data(region, primary_name, feature_name, mp, update, data_dir, progress_bar=True):
    geofabrik_pbf_url = region.urls['pbf']
    PBF_inputfile = download_pbf(geofabrik_pbf_url, update, data_dir, progress_bar=progress_bar)
    country_code = region.short

    # ------- primary file -------
    primary_file_exists = False
    primary_file = os.path.join(data_dir, primary_name, f"{country_code}_{primary_name}.json"
    )
    if os.path.exists(primary_file):
        primary_file_exists = True
        with open(primary_file, encoding="utf-8") as f:
            primary_dict = json.load(f)
    else:
        os.makedirs(os.path.dirname(primary_file), exist_ok=True)

    # TODO: compare update time using metadata in primary_dict
    if not primary_file_exists or update is True:
        primary_dict = run_primary_filter(PBF_inputfile, primary_file, primary_name, mp)

    # ------- feature file -------
    feature_dict = run_feature_filter(primary_dict, feature_name)

    return primary_dict, feature_dict


