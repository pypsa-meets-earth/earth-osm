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

