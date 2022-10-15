__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Filter the Extracted OSM Data

This module filters the extracted OSM data.

"""

from datetime import datetime
from earth_osm.gfk_download import download_pbf
from earth_osm.extract import filter_pbf
from earth_osm.osmpbf import Node, Relation, Way
from earth_osm.config import primary_feature_element

import os
import json
import logging


logging.basicConfig()
logger=logging.getLogger(__name__)
#logger.setLevel(logging.INFO)
logger.setLevel(logging.WARNING)


def feature_filter(primary_data, filter_tuple = ('power', 'line')):

    if set(primary_data.keys()) != set(['Node', 'Way', 'Relation']):
        logger.error('malformed primary_data')
    
    feature_data={'Node':{},'Way':{},'Relation':{}}
    for element in list(feature_data.keys()):
        for id in primary_data[element]:
            if filter_tuple in primary_data[element][id]["tags"].items():
                feature_data[element][id] = primary_data[element][id]
    return feature_data
