__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Utilities functions for earth_osm

This module contains utilities functions for handling OSM data.

"""


import logging
import os

import geopandas as gpd
import pandas as pd
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
                gpd.GeoSeries(way_polygon).set_crs("EPSG:4326").to_crs("ESRI:54009").area,
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
        gpd.GeoSeries(way_linestring).set_crs("EPSG:4326").to_crs("EPSG:3857").length
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


def write_csv(df_feature, outputfile_partial, feature_name, out_aggregate, fn_name):
    """Create csv file. Optimized for large files as write on disk in chunks"""
    if out_aggregate:
        output_path = os.path.join(outputfile_partial, f"all_{feature_name}s" + ".csv")
        df_feature.to_csv(
            output_path,
            index=False,
            header=not os.path.exists(output_path),
            mode="a",
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
            output_path,
            driver="GeoJSON",
            index=False,
            mode="a" if os.path.exists(output_path) else "w",
        )  # Generate GeoJson
    else:
        output_path = os.path.join(
            outputfile_partial, f"{fn_name}_{feature_name}s" + ".geojson"
        )
        gdf_feature.to_file(output_path, driver="GeoJSON")  # Generate GeoJson


def output_creation(
    df_feature, primary_name, feature_name, region_list, data_dir, out_format, out_aggregate
):
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

    outputfile_partial = os.path.join(data_dir, "out")  # Output file directory
    fn_name = filenamer(region_list)  # country code e.g. BJ

    if not os.path.exists(outputfile_partial):
        os.makedirs(outputfile_partial, exist_ok=True)  # create raw directory

    df_feature.reset_index(drop=True, inplace=True)

    # Generate Files

    if df_feature.empty:
        logger.warning(f"All feature data frame empty for {feature_name}")
        return None

    if "csv" in out_format:
        write_csv(df_feature, outputfile_partial, feature_name, out_aggregate, fn_name)

    if "geojson" in out_format:
        if primary_feature_element[primary_name][feature_name] == "way":
            gdf_feature = convert_pd_to_gdf_lines(df_feature)
        else:
            gdf_feature = convert_pd_to_gdf_nodes(df_feature)

        try:
            gdf_feature.drop(columns=["refs"], inplace=True)
        except:
            pass

        logger.info("Writing GeoJSON file")
        write_geojson(gdf_feature, outputfile_partial, feature_name, out_aggregate, fn_name)
