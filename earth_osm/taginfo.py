__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""

This module provides functions to fetch and process data from the OpenStreetMap Taginfo API.
The resulting file is stored in the internal data directory as `earth_data.json`.

"""

import json
import os
import pandas as pd
import requests

WIKI_PRIMARY_LIST = [
    'aerialway',
    'aeroway',
    'amenity',
    'barrier',
    'boundary',
    'building',
    'craft',
    'emergency',
    'geological',
    'highway',
    'historic',
    # 'landuse', # high in relations
    'leisure',
    'man_made',
    'military',
    # 'natural',
    'office',
    'place',
    'power',
    'public_transport',
    'railway',
    # 'route', # high in relations
    'shop',
    'sport',
    'tourism',
    # 'water',
    'waterway'
]

BASE_URL = 'https://taginfo.openstreetmap.org/api/4'


def fetch_data_from_api(path: str, params: dict) -> dict:
    url = BASE_URL + path
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_key_overview(key: str) -> dict:
    key_data = fetch_data_from_api('/key/overview', {'key': key})['data']
    return {key: {'en_description': key_data['description']['en']['text']}}


def get_wiki_features_df(key: str) -> pd.DataFrame:
    tags_list = fetch_data_from_api('/tags/list', {'key': key})['data']

    # Convert to DataFrame for easier manipulation
    tags_df = pd.DataFrame(tags_list)

    # Sort values
    tags_df.sort_values(by=['count_all'], ascending=False, inplace=True)

    # Add en_description column at position 2 and drop None
    tags_df['en_description'] = tags_df.apply(lambda row: row['wiki']['en']['description'] if 'wiki' in row and 'en' in row['wiki'] and 'description' in row['wiki']['en'] else None, axis=1)
    tags_df = tags_df[~tags_df['en_description'].isna()] 
    tags_df.insert(2, 'en_description', tags_df.pop('en_description'))

    # Drop unwanted columns
    drop_columns = ['in_wiki', 'wiki', 'count_all_fraction', 'count_nodes_fraction', 'count_ways_fraction', 'count_relations_fraction']
    tags_df.drop(columns=drop_columns, inplace=True, errors='ignore')

    return tags_df

def get_wiki_features(key: str) -> dict:
    tags_df = get_wiki_features_df(key)

    # Convert DataFrame to list of dictionaries
    tags_list = tags_df.to_dict(orient='records')
    
    # Convert list of dictionaries to nested dictionary
    tags_dict = {tag["value"]: tag for tag in tags_list}
    
    return {key: tags_dict}


def fetch_all_data():
    primary_keys_data = {key: get_key_overview(key)[key] for key in WIKI_PRIMARY_LIST}
    features_data = {key: get_wiki_features(key)[key] for key in WIKI_PRIMARY_LIST}

    # Combining the dictionaries
    all_data = primary_keys_data.copy()
    for key in WIKI_PRIMARY_LIST:
        all_data[key]['features'] = features_data[key]

    return primary_keys_data

def save_data(all_data: dict, save_path: str):
    with open(save_path, 'w') as fp:
        json.dump(all_data, fp, indent=4)

def get_data(data_filepath: str, update: bool = False) -> dict:
    if not os.path.exists(data_filepath) or update:
        save_data(fetch_all_data(), data_filepath)

    with open(data_filepath, 'r') as fp:
        return json.load(fp)

def get_tag_data():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    json_filepath = os.path.join(data_dir, 'earth_data.json')

    if not os.path.exists(json_filepath):
        raise FileNotFoundError(f'File {json_filepath} not found. Please run `python -m earth_osm.taginfo` to create the file.')
    
    return get_data(json_filepath)

if __name__ == '__main__':
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    json_filepath = os.path.join(data_dir, 'earth_data.json')

    data = get_data(json_filepath, update=True)
    print(data)


