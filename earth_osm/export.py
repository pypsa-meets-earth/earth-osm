
__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Export functions for earth_osm

This module contains functions for exporting OSM data to different file formats.

"""

import os
import ast
import logging
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point, Polygon

from earth_osm.utils import columns_melt, tags_explode, tags_melt
from earth_osm import logger as base_logger

logger = logging.getLogger("eo.export")
logger.setLevel(logging.INFO)


def get_list_slug(str_list):
    import hashlib
    str_list.sort()
    if len(str_list) == 1:
        return str_list[0]
    else:
        file_slug = "_".join(str_list)
        if len(file_slug)>15:
            name_string = file_slug[:15]
            name_code = hashlib.md5(file_slug[15:].encode()).hexdigest()[:8]
            file_slug = name_string + '_' + name_code
        return file_slug
    
def convert_pd_to_gdf(pd_df):
    # check if pd_df has a lonlat column
    if not 'lonlat' in pd_df.columns:
        raise KeyError("pandas dataframe does not have a lonlat column")
    if not 'Type' in pd_df.columns:
        raise KeyError("pandas dataframe does not have a Type ('node', 'way' or 'area') column")
    # unstringify lonlat column if necessary
    pd_df['lonlat'] = pd_df['lonlat'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    def create_geometry(lonlat_list, geom_type):
        if geom_type == 'node':
            return Point(lonlat_list[0])
        elif geom_type == 'way':
            return LineString(lonlat_list)
        elif geom_type == 'area':
            return Polygon(lonlat_list)
    
    geometry_col = pd_df.apply(lambda row: create_geometry(row['lonlat'], row['Type']), axis=1)
    lonlat_index = pd_df.columns.get_loc('lonlat')
    pd_df.insert(lonlat_index, "geometry", geometry_col)
    gdf = gpd.GeoDataFrame(pd_df, geometry='geometry')
    gdf.drop(columns=['lonlat'], inplace=True)
    pd_df.drop(columns=['geometry'], inplace=True)

    return gdf



class OutFileWriter:

    def __init__(self, region_list, primary_name, feature_list, data_dir, out_format):
        self.region_list = region_list
        self.primary_name = primary_name
        self.feature_list = feature_list
        self.data_dir = data_dir
        self.out_format = out_format

        if isinstance(self.out_format, str):
            self.out_format = [self.out_format]

        logger.debug(f'File writer initialized with region_list: {region_list}, primary_name: {primary_name}, feature_list: {feature_list}')

    def __enter__(self):
        # setup file name etc.
        region_slug = get_list_slug(self.region_list) # country code e.g. BJ
        feature_slug = get_list_slug(self.feature_list)
    
        out_dir = os.path.join(self.data_dir, "out")  # Output file directory
        out_slug = os.path.join(out_dir, f"{region_slug}_{feature_slug}")

        self.out_slug = out_slug

        if not os.path.exists(out_dir):
            os.makedirs(
                out_dir, exist_ok=True
            )
    
        # delete file if it already exists
        for ext in self.out_format:
            out_path = out_slug + '.' + ext
            if os.path.exists(out_path):
                logger.debug(f"Deleting existing file: {out_path}")
                os.remove(out_path)

        return self
    

    def __call__(self, df_feature):
        if df_feature.empty:
            return

        df_feature.reset_index(drop=True, inplace=True) # avoids weird index

        # Append by concating
        if os.path.exists(self.out_slug + '.csv'):
            # read the existing csv
            df_existing = pd.read_csv(self.out_slug + '.csv')

            # explode other_tags to get back original columns
            df_existing = tags_explode(df_existing)

            # concat the existing df with the new df
            df_feature = pd.concat([df_existing, df_feature], ignore_index=True)

        # melt 95% nan tags (TODO: remove hardcode)
        df_feature = tags_melt(df_feature, 0.95)
        # move refs column to other_tags
        df_feature = columns_melt(df_feature,   ['refs'])

        df_feature.to_csv(self.out_slug + '.csv', index=False)


        # Apend by writing to csv (more efficient, but problem with dynamically changing columns)
        # if os.path.exists(self.out_slug + '.csv'):
        #     # read the existing columns
        #     col_existing = pd.read_csv(self.out_slug + '.csv', nrows=1).columns.to_list()
        #     # check if the columns are the same
        #     col_incoming = df_feature.columns.to_list()
        #     if col_existing != col_incoming:
        #         # add missing columns to the end
        #         missing_cols_in_incoming = [col for col in col_existing if col not in col_incoming]
        #         new_cols_in_incoming = [col for col in col_incoming if col not in col_existing]
        #     TODO: incomplete, should melt new_cols_in_incoming, and add missing cols

        # write the new df to csv
        # df_feature.to_csv(self.out_slug + '.csv', index=False, header= not os.path.exists(self.out_slug + '.csv'), mode="a")


    def __exit__(self, exc_type, exc_value, traceback):
        if os.path.exists(self.out_slug + '.csv'):
            logger.info(f"Output file written to: {self.out_slug}.csv")
            
            if 'geojson' in self.out_format:
                # read the csv file
                df_feature = pd.read_csv(self.out_slug + '.csv')
                # convert to geodataframe
                gdf_feature = convert_pd_to_gdf(df_feature)

                gdf_feature.to_file(
                    self.out_slug + '.geojson', driver="GeoJSON", index=False, mode="w"
                )
                logger.info(f"Output file written to: {self.out_slug}.geojson")

