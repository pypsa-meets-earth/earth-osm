
__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""
This module provides functions to fetch OSM data from the Overpass API.
"""

import json
import logging
from datetime import datetime
from textwrap import dedent

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("eo.overpass")

OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"
REQUEST_TIMEOUT = 600
QUERY_TIMEOUT = 300
REQUEST_HEADERS = {
    "User-Agent": "earth-osm/overpass (+https://github.com/pypsa-meets-earth/earth-osm)",
}

def build_overpass_query(country_code, primary_name, feature_name):
    """
    Build an Overpass query for a specific feature in a country.
    Also fetches all related nodes for ways and relations.

    Args:
        country_code: ISO country code (e.g., 'BJ' for Benin)
        primary_name: Primary feature name (e.g., 'power')
        feature_name: Specific feature name (e.g., 'substation', 'line', 'generator')

    Returns:
        str: Overpass query string
    """
    # Define area query for the country
    area_query = f'area["ISO3166-1"="{country_code}"]'
    match_all = feature_name.startswith('ALL_')
    element_query = (
        f'nwr["{primary_name}"]'
        if match_all
        else f'nwr["{primary_name}"="{feature_name}"]'
    )

    # Construct the full Overpass query with recursion to get referenced nodes
    return dedent(
        f"""
        [out:json][timeout:{QUERY_TIMEOUT}];
        {area_query}->.searchArea;
        (
            {element_query}(area.searchArea);
        );
        (._;>;);
        out body;
        """
    ).strip()


_SESSION = requests.Session()
_SESSION.headers.update(REQUEST_HEADERS)
_RETRY = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=False,
    respect_retry_after_header=True,
)
_ADAPTER = HTTPAdapter(max_retries=_RETRY)
_SESSION.mount("http://", _ADAPTER)
_SESSION.mount("https://", _ADAPTER)


def fetch_overpass_data(query):
    """
    Fetch data from the Overpass API.

    Args:
        query: Overpass query string

    Returns:
        dict: Response from Overpass API
    """
    logger.debug("Fetching data from Overpass API")
    response = _SESSION.post(
        OVERPASS_ENDPOINT,
        data=query,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    logger.info("Successfully fetched data from Overpass API")
    return data


def transform_overpass_to_internal_format(overpass_data, primary_name, feature_name):
    """
    Transform Overpass API response to the internal format expected by earth-osm.

    Args:
        overpass_data: Raw response from Overpass API
        primary_name: Primary feature name
        feature_name: Feature name

    Returns:
        tuple: (primary_dict, feature_dict) in the format expected by process_region
    """
    # Initialize the data structure
    primary_data = {'Node': {}, 'Way': {}, 'Relation': {}}
    feature_data = {'Node': {}, 'Way': {}, 'Relation': {}}
    include_all = feature_name.startswith('ALL_')

    def build_payload(metadata, data):
        return {'Metadata': metadata, 'Data': data}

    def node_attrs(element):
        lon = element.get('lon')
        lat = element.get('lat')
        if lon is None or lat is None:
            return None
        return 'lonlat', [lon, lat]

    def way_attrs(element):
        return 'refs', element.get('nodes', [])

    def relation_attrs(element):
        return 'members', element.get('members', [])

    type_extractors = {
        'Node': node_attrs,
        'Way': way_attrs,
        'Relation': relation_attrs,
    }

    # Process each element from the Overpass response
    for element in overpass_data.get('elements', []):
        element_type = element['type'].capitalize()  # 'node' -> 'Node', etc.
        element_id = str(element['id'])  # Convert to string to match geofabrik format

        # Extract tags
        tags = element.get('tags', {})

        # Create the element data structure
        element_data = {
            'id': element['id'],  # Keep original ID as int
            'tags': tags
        }

        extractor = type_extractors.get(element_type)
        if extractor:
            extracted = extractor(element)
            if extracted is not None:
                key, value = extracted
                element_data[key] = value

        # Always add nodes to primary data (needed for way references)
        # Add all elements with the primary tag to primary data
        if element_type == 'Node' or primary_name in tags:
            primary_data[element_type][element_id] = element_data

        # Add to feature data (elements that match the specific feature)
        if not include_all and tags.get(primary_name) == feature_name:
            feature_data[element_type][element_id] = element_data

    # Create metadata
    timestamp = datetime.now().isoformat()

    primary_metadata = {
        'filter_date': timestamp,
        'primary_feature': primary_name,
    }
    primary_dict = build_payload(primary_metadata, primary_data)

    if include_all:
        return primary_dict, primary_dict

    feature_metadata = {
        'filter_date': timestamp,
        'filter_tuple': json.dumps((primary_name, feature_name)),
    }
    feature_dict = build_payload(feature_metadata, feature_data)

    return primary_dict, feature_dict


def get_overpass_data(region, primary_name, feature_name, data_dir):
    """
    Get OSM data from Overpass API for a specific region and feature.

    Args:
        region: Region object with short code and other information
        primary_name: Primary feature name (e.g., 'power')
        feature_name: Specific feature name (e.g., 'substation')
        data_dir: Directory for data storage

    Returns:
        tuple: (primary_dict, feature_dict) in the format expected by process_region
    """
    if feature_name.startswith('ALL_'):
        raise ValueError(
            "Overpass backend does not support wildcard features (ALL_*). "
            "Specify concrete feature values or use the geofabrik data source."
        )

    logger.debug(
        "Overpass request: region=%s, primary=%s, feature=%s",
        region.short,
        primary_name,
        feature_name,
    )

    query = build_overpass_query(region.short, primary_name, feature_name)
    logger.debug(f"Overpass query: {query}")

    overpass_response = fetch_overpass_data(query)

    primary_dict, feature_dict = transform_overpass_to_internal_format(
        overpass_response, primary_name, feature_name
    )

    logger.info(f"Retrieved {len(feature_dict['Data']['Node'])} nodes, "
                f"{len(feature_dict['Data']['Way'])} ways, "
                f"{len(feature_dict['Data']['Relation'])} relations for {feature_name}")

    return primary_dict, feature_dict
