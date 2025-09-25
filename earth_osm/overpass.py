
__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""
This module provides functions to fetch OSM data from the Overpass API.
"""

import json
import logging
import time
from datetime import datetime

import requests

logger = logging.getLogger("eo.overpass")
logger.setLevel(logging.INFO)


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

    # Build the specific query based on primary and feature name
    if primary_name == 'power':
        if feature_name == 'substation':
            element_query = 'nwr["power"="substation"]'
        elif feature_name == 'line':
            element_query = 'way["power"="line"]'
        elif feature_name == 'generator':
            element_query = 'nwr["power"="generator"]'
        elif feature_name == 'tower':
            element_query = 'node["power"="tower"]'
        elif feature_name == 'pole':
            element_query = 'node["power"="pole"]'
        elif feature_name == 'transformer':
            element_query = 'nwr["power"="transformer"]'
        else:
            # Generic query for any power feature
            element_query = f'nwr["power"="{feature_name}"]'
    else:
        # Generic query for other primary features
        element_query = f'nwr["{primary_name}"="{feature_name}"]'

    # Construct the full Overpass query with recursion to get referenced nodes
    query = f"""
        [out:json][timeout:300];
        {area_query}->.searchArea;
        (
            {element_query}(area.searchArea);
        );
        (._;>;);
        out body geom;
    """

    return query


def fetch_overpass_data(query, retries=3, wait_time=5):
    """
    Fetch data from the Overpass API.

    Args:
        query: Overpass query string
        retries: Number of retry attempts
        wait_time: Initial wait time between retries (will increase with each retry)

    Returns:
        dict: Response from Overpass API
    """
    overpass_url = "https://overpass-api.de/api/interpreter"

    for attempt in range(retries):
        try:
            logger.info(f"Fetching data from Overpass API (Attempt {attempt + 1})...")

            response = requests.post(overpass_url, data=query, timeout=600)
            response.raise_for_status()  # Raise HTTPError for bad responses

            data = response.json()
            logger.info("Successfully fetched data from Overpass API")
            return data

        except (json.JSONDecodeError, requests.exceptions.RequestException) as e:
            logger.error(f"Error fetching data from Overpass API: {e}")
            if attempt < retries - 1:
                wait_time += 15
                logger.info(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to retrieve data after {retries} attempts")
                raise e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if attempt < retries - 1:
                wait_time += 10
                logger.info(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to retrieve data after {retries} attempts")
                raise e


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

        # Add coordinates for nodes
        if element_type == 'Node':
            element_data['lonlat'] = [element.get('lon', 0), element.get('lat', 0)]

        # Add refs for ways
        elif element_type == 'Way':
            element_data['refs'] = element.get('nodes', [])

        # Add members for relations
        elif element_type == 'Relation':
            element_data['members'] = element.get('members', [])

        # Always add nodes to primary data (needed for way references)
        # Add all elements with the primary tag to primary data
        if element_type == 'Node' or primary_name in tags:
            primary_data[element_type][element_id] = element_data

        # Add to feature data (elements that match the specific feature)
        if tags.get(primary_name) == feature_name:
            feature_data[element_type][element_id] = element_data

    # Create metadata
    primary_metadata = {
        'filter_date': datetime.now().isoformat(),
        'primary_feature': primary_name,
    }

    feature_metadata = {
        'filter_date': datetime.now().isoformat(),
        'filter_tuple': json.dumps((primary_name, feature_name)),
    }

    # Create the dictionaries in the expected format
    primary_dict = {
        'Metadata': primary_metadata,
        'Data': primary_data
    }

    feature_dict = {
        'Metadata': feature_metadata,
        'Data': feature_data
    }

    return primary_dict, feature_dict


def get_overpass_data(region, primary_name, feature_name, data_dir, progress_bar):
    """
    Get OSM data from Overpass API for a specific region and feature.

    Args:
        region: Region object with short code and other information
        primary_name: Primary feature name (e.g., 'power')
        feature_name: Specific feature name (e.g., 'substation')
        data_dir: Directory for data storage
        progress_bar: Whether to show progress (currently not used)

    Returns:
        tuple: (primary_dict, feature_dict) in the format expected by process_region
    """
    logger.info('\n'.join(['',
                           '-------- Overpass Function------- ',
                           f'Primary Feature: {primary_name}',
                           f'Feature Name: {feature_name}',
                           f'Region Short: {region.short}',
                           f'Region Name: {region.name}',
                           f'Data Directory = {data_dir}',
                           f'Progress Bar = {progress_bar}'
                           ]))

    # Build the Overpass query
    query = build_overpass_query(region.short, primary_name, feature_name)
    logger.debug(f"Overpass query: {query}")

    # Fetch data from Overpass API
    overpass_response = fetch_overpass_data(query)

    # Transform to internal format
    primary_dict, feature_dict = transform_overpass_to_internal_format(
        overpass_response, primary_name, feature_name
    )

    logger.info(f"Retrieved {len(feature_dict['Data']['Node'])} nodes, "
                f"{len(feature_dict['Data']['Way'])} ways, "
                f"{len(feature_dict['Data']['Relation'])} relations for {feature_name}")

    return primary_dict, feature_dict
