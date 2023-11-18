#%%
import pandas as pd
from pprint import pprint

from earth_osm.taginfo import get_tag_data
import pandas as pd


tag_data = get_tag_data()

#%%
def get_feature_list(primary_name):
    return list(tag_data[primary_name]['features'].keys())

def get_primary_list():
    return list(tag_data.keys())

def load_tag_data():
    # load tag_data into a dataframe
    dataframes = []
    json_dict = tag_data
    for primary_key, values in json_dict.items():
        features = values['features']
        for feature_key, feature_values in features.items():
            df = pd.json_normalize(feature_values)
            dataframes.append(df)

    tag_df = pd.concat(dataframes, ignore_index=True)
    return tag_df

#%%
def get_popular_features(primary_name):
    # TODO: check count_all and only return
    # - features that are significant
    # - features that are non-relation
    return get_feature_list(primary_name)
    
