__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Utilities functions for earth_osm

This module contains utilities functions for handling OSM data.

"""


import logging
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point, Polygon

from earth_osm.config import primary_feature_element

logger = logging.getLogger("osm_data_extractor")
logger.setLevel(logging.INFO)

# geo_crs: EPSG:4326  # general geographic projection, not used for metric measures. "EPSG:4326" is the standard used by OSM and google maps
# distance_crs: EPSG:3857  # projection for distance measurements only. Possible recommended values are "EPSG:3857" (used by OSM and Google Maps)
# area_crs: ESRI:54009  # projection for area measurements only. Possible recommended values are Global Mollweide "ESRI:54009"

def lonlat_lookup(df_way, primary_data):
    """
    Lookup refs and convert to list of longlats
    """
    if "refs" not in df_way.columns:
        logger.warning("refs column not found")

    def look(ref):
        lonlat_row = list(map(lambda r: tuple(primary_data["Node"][str(r)]["lonlat"]), ref))
        return lonlat_row

    lonlat_list = df_way["refs"].apply(look)

    return lonlat_list

def way_or_area(df_way):
    if "refs" not in df_way.columns:
        raise IndexError("refs column not found")
    
    def check_closed(refs):
        if (refs[0] == refs[-1]) and (len(refs) >= 3):
            return "area"
        elif len(refs) >= 3:
            return "way"
        else:
            # TODO: improve error handling
            logger.debug(f"Way with less than 3 refs: {refs}")
            return None

    type_list = df_way["refs"].apply(check_closed)

    return type_list

def convert_ways_points(df_way, primary_data):
    """
    Convert Ways to Point Coordinates
    """
    lonlat_list = lonlat_lookup(df_way, primary_data)
    way_polygon = list(
        map(
            lambda lonlat: Polygon(lonlat) if len(lonlat) >= 3 else Point(lonlat[0]),
            lonlat_list,
        )
    )
    area_column = list(
        map(
            int,
            round(
                gpd.GeoSeries(way_polygon)
                .set_crs("EPSG:4326")
                .to_crs("ESRI:54009")
                .area,
                -1,
            ),
        )
    )  # TODO: Rounding should be done in cleaning scripts

    def find_center_point(p):
        if p.geom_type == "Polygon":
            center_point = p.centroid
        else:
            center_point = p
        return list((center_point.x, center_point.y))

    lonlat_column = list(map(find_center_point, way_polygon))

    # df_way.drop("refs", axis=1, inplace=True, errors="ignore")
    df_way.insert(0, "Area", area_column)
    df_way.insert(0, "lonlat", lonlat_column)


def convert_ways_polygons(df_way, primary_data):
    """
    Convert Ways to Polygon and Point Coordinates
    """
    lonlat_list = lonlat_lookup(df_way, primary_data)
    way_polygon = list(
        map(
            lambda lonlat: Polygon(lonlat) if len(lonlat) >= 3 else Point(lonlat[0]),
            lonlat_list,
        )
    )


    # df_way.insert(0, "Area", way_polygon)
    return way_polygon

def convert_ways_lines(df_way, primary_data):
    """
    Convert Ways to Line Coordinates

    Args:

    """
    lonlat_list = lonlat_lookup(df_way, primary_data)
    lonlat_column = lonlat_list
    df_way.insert(0, "lonlat", lonlat_column)

    way_linestring = map(lambda lonlats: LineString(lonlats), lonlat_list)
    length_column = (
        gpd.GeoSeries(way_linestring)
        .set_crs("EPSG:4326")
        .to_crs("EPSG:3857")
        .length
    )

    df_way.insert(0, "Length", length_column)
    return df_way

def tags_melt(df_exp, nan_threshold=0.75):
    # Find columns with high percentage of NaN values
    high_nan_cols = df_exp.columns[df_exp.isnull().mean() > nan_threshold]
    df_high_nan = df_exp[high_nan_cols]

    df_exp['other_tags'] = df_high_nan.apply(lambda x: x.dropna().to_dict(), axis=1)
    df_exp.drop(columns=high_nan_cols, inplace=True)
    return df_exp

def columns_melt(df_exp, columns_to_move):
    # Check if other_tags already exists, create it if it doesn't
    if 'other_tags' not in df_exp.columns:
        df_exp['other_tags'] = df_exp.apply(lambda x: {}, axis=1)

    # Move specified columns to other_tags
    for col in columns_to_move:
        if col in df_exp.columns:
            df_exp['other_tags'] = df_exp.apply(lambda x: {**x['other_tags'], col: x[col]}, axis=1)
            df_exp.drop(columns=col, inplace=True)
        else:
            logger.warning(f"Column '{col}' not found in dataframe.")

    return df_exp

def tags_explode(df_melt):
    for index, row in df_melt.iterrows():
        other_tags = row['other_tags']
        if not other_tags:
            continue
        # check if other tags is dict
        if not isinstance(other_tags, dict):
            logger.warning(f"other_tags is not dict: {other_tags}")
            continue
        for col, val in other_tags.items():
            df_melt.at[index, col] = val
        df_melt.at[index, 'other_tags'] = ''
    df_melt.drop(columns=['other_tags'], inplace=True)
    return df_melt


def convert_pd_to_gdf(pd_df):
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
    
def write_csv(df_feature, outputfile_partial, feature_name, out_aggregate, fn_name):
    """Create csv file. Optimized for large files as write on disk in chunks"""
    if out_aggregate:
        output_path = os.path.join(outputfile_partial, f"all_{feature_name}s" + ".csv")
        df_feature.to_csv(
            output_path, index=False, header= not os.path.exists(output_path), mode="a",
        )  # Generate CSV
    else:
        output_path = os.path.join(outputfile_partial, f"{fn_name}_{feature_name}s" + ".csv")
        df_feature.to_csv(
            output_path,
        )  # Generate CSV


def write_geojson(gdf_feature, outputfile_partial, feature_name, out_aggregate, fn_name):
    """Create geojson file. Optimized for large files as write on disk in chunks"""
    if out_aggregate:
        output_path = os.path.join(outputfile_partial, f"all_{feature_name}s" + ".geojson")
        gdf_feature.to_file(
            output_path, driver="GeoJSON", index=False, mode="a" if os.path.exists(output_path) else "w"
        )  # Generate GeoJson
    else:
        output_path = os.path.join(outputfile_partial, f"{fn_name}_{feature_name}s" + ".geojson")
        gdf_feature.to_file(
            output_path, driver="GeoJSON"
        )  # Generate GeoJson


def get_region_slug(region_list):
    if len(region_list) == 1:
        region_slug = str(region_list[0].short)
    else:
        # TODO: Implement filenamer for multiple regions
        raise NotImplementedError

    return region_slug


def output_creation(df_feature, primary_name, feature_name, region_list, data_dir, out_format):
    """
    Save Dataframe to disk
    Currently supports 
        CSV: Comma Separated Values
        GeoJSON: GeoJSON format (including geometry)

    Args:
        df_feature
    """

    region_slug = get_region_slug(region_list) # country code e.g. BJ
    out_dir = os.path.join(data_dir, "out")  # Output file directory
    out_slug = os.path.join(out_dir, f"{region_slug}_{feature_name}")
    

    if not os.path.exists(out_dir):
        os.makedirs(
            out_dir, exist_ok=True
        )  # create raw directory

    # df_feature.reset_index(drop=True, inplace=True)

    # Generate Files
    if df_feature.empty:
        logger.warning(f"feature data frame empty for {feature_name}")
        return None

    if "csv" in out_format:
        logger.debug("Writing CSV file")
        df_feature.to_csv(out_slug + '.csv')

    if "geojson" in out_format:
        logger.debug("Writing GeoJSON file")
        gdf_feature = convert_pd_to_gdf(df_feature)
        gdf_feature.to_file(out_slug + '.geojson', driver="GeoJSON")


        try:
            gdf_feature.drop(columns=["refs"], inplace=True)
        except:
            pass

        logger.info("Writing GeoJSON file")
        write_geojson(gdf_feature, outputfile_partial, feature_name, out_aggregate, fn_name)

