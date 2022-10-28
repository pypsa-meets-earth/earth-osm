__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Utilities functions for earth_osm

This module contains utilities functions for handling OSM data.

"""


import logging
import os

import geopandas as gpd
from shapely.geometry import LineString, Point, Polygon

from earth_osm.config import primary_feature_element

logger = logging.getLogger("osm_data_extractor")
logger.setLevel(logging.INFO)


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
                .to_crs("EPSG:3857")
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


def convert_pd_to_gdf_nodes(df_way):
    """
    Convert Nodes Pandas Dataframe to GeoPandas Dataframe

    Args:
        df_way: Pandas Dataframe

    Returns:
        GeoPandas Dataframe
    """
    gdf = gpd.GeoDataFrame(
        df_way, geometry=[Point(x, y) for x, y in df_way.lonlat], crs="EPSG:4326"
    )
    gdf.drop(columns=["lonlat"], inplace=True)
    return gdf


def convert_pd_to_gdf_lines(df_way):
    """
    Convert Lines Pandas Dataframe to GeoPandas Dataframe

    Args:
        df_way: Pandas Dataframe

    Returns:
        GeoPandas Dataframe
    """

    gdf = gpd.GeoDataFrame(
        df_way, geometry=[LineString(x) for x in df_way.lonlat], crs="EPSG:4326"
    )
    gdf.drop(columns=["lonlat"], inplace=True)
    return gdf

def output_csv_geojson(df_feature, primary_name, feature_name, region_list, data_dir):
    """
    Output CSV and GeoJSON files for each region

    Args:
        df_feature: _description_
        primary_name: _description_
        feature_name: _description_
        region_list: _description_
    """

    def filenamer(cc_list):
        if len(cc_list) == 1:
            return str(cc_list[0].short)
        else:
            # TODO: Fix filenamer
            raise NotImplementedError

    fn_name = filenamer(region_list)
    outputfile_partial = os.path.join(data_dir, "out", fn_name + "_raw"
    )  # Output file directory

    if not os.path.exists(outputfile_partial):
        os.makedirs(
            os.path.dirname(outputfile_partial), exist_ok=True
        )  # create raw directory

    df_feature.reset_index(drop=True, inplace=True)

    # Generate Files

    if df_feature.empty:
        logger.warning(f"All feature data frame empty for {feature_name}")
        return None

    df_feature.to_csv(
        outputfile_partial + f"_{feature_name}s" + ".csv"
    )  # Generate CSV

    if primary_feature_element[primary_name][feature_name] == "way":
        gdf_feature = convert_pd_to_gdf_lines(df_feature)
    else:
        gdf_feature = convert_pd_to_gdf_nodes(df_feature)

    try:
        gdf_feature.drop(columns=["refs"], inplace=True)
    except:
        pass

    logger.info("Writing GeoJSON file")
    gdf_feature.to_file(
        outputfile_partial + f"_{feature_name}s" + ".geojson", driver="GeoJSON"
    )  # Generate GeoJson
