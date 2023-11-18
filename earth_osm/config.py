__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""
DEPRECATED MODULE (see tagdata.py and taginfo.py)

"""

primary_feature_element = {
    "power": {
        "substation": ("node", "area"), 
        "generator": ("node", "way", "area"),
        "line": ("way"),
        "tower": ("node"),
        "cable": ("way"),
        },
    "building": {
        'allotment_house': ('area',),
        'apartments': ('area',),
        'barn': ('area',),
        'boathouse': ('area',),
        'bungalow': ('area',),
        'bunker': ('area',),
        'cabin': ('area',),
        'carport': ('area',),
        'cathedral': ('area',),
        'chapel': ('area',),
        'church': ('area',),
        'civic': ('area',),
        'college': ('area',),
        'commercial': ('area',),
        'construction': ('area',),
        'cowshed': ('area',),
        'detached': ('area',),
        'dormitory': ('area',),
        'entrance': ('node',),
        'farm': ('area',),
        'farm_auxiliary': ('area',),
        'fire_station': ('area',),
        'garage': ('area',),
        'garages': ('area',),
        'ger': ('area',),
        'grandstand': ('area',),
        'greenhouse': ('area',),
        'hangar': ('area',),
        'hospital': ('area',),
        'hotel': ('area',),
        'house': ('area',),
        'houseboat': ('area',),
        'hut': ('area',),
        'industrial': ('area',),
        'kindergarten': ('area',),
        'manufacture': ('area',),
        'mosque': ('area',),
        'office': ('area',),
        'outbuilding': ('area',),
        'pavilion': ('area',),
        'public': ('area',),
        'residential': ('area',),
        'retail': ('area',),
        'roof': ('area', 'node'),
        'ruins': ('area',),
        'school': ('area',),
        'semidetached_house': ('area',),
        'service': ('area',),
        'shed': ('area',),
        'stable': ('area',),
        'stadium': ('area',),
        'static_caravan': ('area',),
        'sty': ('area',),
        'synagogue': ('area',),
        'temple': ('area',),
        'terrace': ('area',),
        'train_station': ('node', 'area'),
        'transportation': ('area',),
        'university': ('area',),
        'warehouse': ('area',)
        }
    # add more primary features here
}
# %%
# import json
# from pprint import pprint
# import pandas as pd
# TODO: Add taginfo.json to package data, 
# can be used to get the primary keys and values
# TODO: Implement view features simialr to gfk_data
# taginfo_url='https://raw.githubusercontent.com/openstreetmap/id-tagging-schema/main/dist/taginfo.min.json'
# taginfo = '/home/matin/Projects/earth-osm/earth_osm/data/taginfo.min.json'
# with open(taginfo, encoding='utf8') as f:
#     d = json.load(f)
# tag_dict = d['tags']
# pprint(tag_dict)
# tag_df = pd.DataFrame(tag_dict)

