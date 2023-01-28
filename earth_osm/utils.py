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
        logger.warning("refs column not found")
    
    def check_closed(ref):
        if (ref[0] == ref[-1]) and (len(ref) >= 3):
            return "area"
        elif len(ref) >= 3:
            return "way"
        else:
            logger.debug(f"Length of ref {len(ref)}")
            return pd.nan


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


    df_way.insert(0, "Area", area_column)

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

def convert_ways(df_way, primary_data):
    lonlat_list = lonlat_lookup(df_way, primary_data)



# Combine convert_pd_to_gdf_nodes and convert_pd_to_gdf_lines int0
# convert_pd_to_gdf
def convert_pd_to_gdf_nodes(df):

    # TODO: Ensure Type = node
    gdf = gpd.GeoDataFrame(
        df, geometry=[Point(x, y) for x, y in df.lonlat], crs="EPSG:4326"
    )
    gdf.drop(columns=["lonlat"], inplace=True)
    return gdf

def convert_pd_to_gdf_lines(df_way):
    # TODO: Ensure Type = way
    gdf = gpd.GeoDataFrame(
        df_way, geometry=[LineString(x) for x in df_way.lonlat], crs="EPSG:4326"
    )
    gdf.drop(columns=["lonlat"], inplace=True)
    return gdf

def get_region_slug(region_list):
    if len(region_list) == 1:
        region_slug = str(region_list[0].short)
    else:
        # TODO: Implement filenamer for multiple regions
        raise NotImplementedError

    return region_slug



def output_creation(df_feature, region_list, feature_name, data_dir, out_format):
    """
    Save Dataframe to disk
    Currently supports 
        CSV: Comma Separated Values
        GeoJSON: Seperate files for Nodes and Ways

    Args:
        df_feature:
    """

    region_slug = get_region_slug(region_list) # country code e.g. BJ
    out_dir = os.path.join(data_dir, "out")  # Output file directory
    out_slug = os.path.join(out_dir, f"{region_slug}_{feature_name}")
    

    if not os.path.exists(out_dir):
        os.makedirs(
            out_dir, exist_ok=True
        )  # create raw directory

    df_feature.reset_index(drop=True, inplace=True)

    # Generate Files
    if df_feature.empty:
        logger.warning(f"All feature data frame empty for {feature_name}")
        return None

    if "csv" in out_format:
        logger.debug("Writing CSV file")
        df_feature.to_csv(out_slug + '.csv')

    if "geojson" in out_format:
        logger.debug("Writing GeoJSON file")
        # if primary_feature_element[primary_name][feature_name] == "way":
        #     gdf_feature = convert_pd_to_gdf_lines(df_feature)
        # else:
        #     gdf_feature = convert_pd_to_gdf_nodes(df_feature)

        # try:
        #     gdf_feature.drop(columns=["refs"], inplace=True)
        # except:
        #     pass

        gdf_feature.to_file(out_slug + '.geojson', driver='GeoJSON')

