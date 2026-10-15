__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""
This is the principal module of the earth_osm project.
"""

import logging
import os
from datetime import datetime
from typing import Optional

import pandas as pd

# suppress pandas warning about fragmented dataframes
# TODO: do not suppress warnings
import warnings

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

from earth_osm.backends import fetch_region_backend
from earth_osm.tagdata import get_feature_list
from earth_osm.regions import (
    expand_region_to_iso_children,
    get_region_tuple,
    get_region_tuple_historical,
    view_regions,
)
from earth_osm.export import EarthOSMWriter
from earth_osm.stream import stream_region_features_multi

logger = logging.getLogger("eo.eo")
logger.setLevel(logging.INFO)


def _rows_to_dataframe(row_iter):
    rows = list(row_iter)
    df_feature = pd.DataFrame(rows)
    df_feature.dropna(axis=1, how="all", inplace=True)
    return df_feature


def _fetch_overpass_region(
    region,
    primary_name,
    feature_name,
    *,
    mp,
    update,
    data_dir,
    progress_bar,
    cache_primary,
):
    expanded_regions = expand_region_to_iso_children(region, require_iso=True)
    child_regions = [child for child in expanded_regions if child.id != region.id]

    if child_regions:
        frames = []
        for child_region in child_regions:
            result_kind, payload = fetch_region_backend(
                child_region,
                primary_name,
                feature_name,
                data_source="overpass",
                use_stream=False,
                mp=mp,
                update=update,
                data_dir=data_dir,
                progress_bar=progress_bar,
                cache_primary=cache_primary,
            )
            frame = payload if result_kind == "dataframe" else _rows_to_dataframe(payload)
            if isinstance(frame, pd.DataFrame) and not frame.empty:
                frames.append(frame)

        if not frames:
            return pd.DataFrame()

        return pd.concat(frames, ignore_index=True)

    result_kind, payload = fetch_region_backend(
        region,
        primary_name,
        feature_name,
        data_source="overpass",
        use_stream=False,
        mp=mp,
        update=update,
        data_dir=data_dir,
        progress_bar=progress_bar,
        cache_primary=cache_primary,
    )
    return payload if result_kind == "dataframe" else _rows_to_dataframe(payload)


def process_region(
    region,
    primary_name,
    feature_name,
    mp,
    update,
    data_dir,
    progress_bar=True,
    data_source="geofabrik",
    stream=False,
    cache_primary=False,
):
    """Process a single region for a feature.

    When ``stream`` is ``True`` and the geofabrik backend is used the function
    returns an iterator of flattened feature dictionaries. Otherwise it returns
    a :class:`pandas.DataFrame` to preserve the historic API.
    """

    if data_source == "overpass":
        if stream:
            raise ValueError("Streaming export is not supported for the Overpass backend.")
        return _fetch_overpass_region(
            region,
            primary_name,
            feature_name,
            mp=mp,
            update=update,
            data_dir=data_dir,
            progress_bar=progress_bar,
            cache_primary=cache_primary,
        )

    use_stream = stream and data_source == "geofabrik"
    result_kind, payload = fetch_region_backend(
        region,
        primary_name,
        feature_name,
        data_source=data_source,
        use_stream=use_stream,
        mp=mp,
        update=update,
        data_dir=data_dir,
        progress_bar=progress_bar,
        cache_primary=cache_primary,
    )

    if stream:
        if result_kind != "stream":
            raise RuntimeError("Requested streaming backend but received a dataframe payload")
        return payload

    if result_kind == "dataframe":
        return payload

    return _rows_to_dataframe(payload)


def get_osm_data(
        region_str,
        primary_name,
        feature_name,
        data_dir=None,
        cached=True,
        progress_bar=True,
        target_date: Optional[datetime] = None,
        data_source="geofabrik",
):

    if target_date:
        region_tuple = get_region_tuple_historical(region_str, target_date)
    else:
        region_tuple = get_region_tuple(region_str)

    mp = True
    update = not cached

    data_dir = os.path.join(os.getcwd(), "earth_data") if data_dir is None else data_dir

    df = process_region(
        region_tuple,
        primary_name,
        feature_name,
        mp,
        update,
        data_dir,
        progress_bar=progress_bar,
        data_source=data_source,
    )

    return df

# TODO: Plan
# Use an intermediary super efficient file format such as parquet
# save a region,feauture pair in temp files
# implement planetary file from osm (https://planet.openstreetmap.org/)
# read keys, values, tags and their frequencies from taginfo api (https://taginfo.openstreetmap.org/taginfo/apidoc)
# use **kwargs and allow for dropping of refs column
# implement post processing functions: i) create_geojson 2) filter_by_bbox


def save_osm_data(
    region_list,
    primary_name,
    feature_list=None,
    out_format="csv",  # TODO: rename out_format -> format
    out_aggregate=True,  # TODO: rename out_aggregate -> aggregate
    out_dir=os.path.join(os.getcwd(), "earth_data"),
    data_source="geofabrik",  # 'overpass'
    data_dir=os.path.join(os.getcwd(), "earth_data"),
    update=False,
    mp=True,  # TODO: remove mp arg,
    progress_bar=True,
    stream_backend=True,
    cache_primary=False,
    target_date: Optional[datetime] = None,
):
    """
    Get OSM Data for a list of regions and features
    args:
        region_list: list of regions to get data for
        primary_name: primary feature to get data for
        feature_list: list of features to get data for
        update: update data
        mp: use multiprocessing
        stream_backend: when ``True`` (default) use the streaming pipeline for
            GeoFabrik sources; set to ``False`` to revert to the legacy
            in-memory pipeline (primarily for benchmarking)
        target_date: optional target date for historical data
    returns:
        dict of dataframes
    """
    if target_date:
        region_tuple_list = [get_region_tuple_historical(r, target_date) for r in region_list]
    else:
        region_tuple_list = [get_region_tuple(r) for r in region_list]

    region_short_list = [r.short for r in region_tuple_list]

    if feature_list is None:
        feature_list = get_feature_list(primary_name)
    elif feature_list == ["ALL"]:
        # Account for wild card
        feature_list = [f"ALL_{primary_name}"]

    multi_feature_streaming = (
        data_source == "geofabrik"
        and stream_backend
        and not cache_primary
        and feature_list
        and len(feature_list) > 1
    )

    def iter_feature_rows(region_obj, feature_name_obj):
        if data_source == "geofabrik" and stream_backend:
            return process_region(
                region_obj,
                primary_name,
                feature_name_obj,
                mp,
                update,
                data_dir,
                progress_bar=progress_bar,
                data_source=data_source,
                stream=True,
                cache_primary=cache_primary,
            )

        df_feature = process_region(
            region_obj,
            primary_name,
            feature_name_obj,
            mp,
            update,
            data_dir,
            progress_bar=progress_bar,
            data_source=data_source,
            stream=False,
            cache_primary=cache_primary,
        )
        return df_feature.to_dict("records")

    with EarthOSMWriter(primary_name, out_dir, out_format) as writer:
        if out_aggregate == "region" or out_aggregate is True:
            for feature_name in feature_list:
                writer.prepare_target(region_short_list, [feature_name])

            if multi_feature_streaming:
                for region in region_tuple_list:
                    for matched_feature, row in stream_region_features_multi(
                        region,
                        primary_name,
                        feature_list,
                        data_dir,
                        update=update,
                        progress_bar=progress_bar,
                        multiprocess=mp,
                        data_source=data_source,
                    ):
                        writer.write(region_short_list, [matched_feature], [row])
            else:
                for feature_name in feature_list:
                    for region in region_tuple_list:
                        writer.write(
                            region_short_list,
                            [feature_name],
                            iter_feature_rows(region, feature_name),
                        )

        elif out_aggregate == "feature":
            for region in region_tuple_list:
                writer.prepare_target([region.short], feature_list)

            if multi_feature_streaming:
                for region in region_tuple_list:
                    for _, row in stream_region_features_multi(
                        region,
                        primary_name,
                        feature_list,
                        data_dir,
                        update=update,
                        progress_bar=progress_bar,
                        multiprocess=mp,
                        data_source=data_source,
                    ):
                        writer.write([region.short], feature_list, [row])
            else:
                for region in region_tuple_list:
                    for feature_name in feature_list:
                        writer.write(
                            [region.short],
                            feature_list,
                            iter_feature_rows(region, feature_name),
                        )

        elif out_aggregate is False:
            for region_label in region_list:
                for feature_name in feature_list:
                    writer.prepare_target([region_label], [feature_name])

            if multi_feature_streaming:
                for region, region_label in zip(region_tuple_list, region_list):
                    for matched_feature, row in stream_region_features_multi(
                        region,
                        primary_name,
                        feature_list,
                        data_dir,
                        update=update,
                        progress_bar=progress_bar,
                        multiprocess=mp,
                        data_source=data_source,
                    ):
                        writer.write([region_label], [matched_feature], [row])
            else:
                for region, region_label in zip(region_tuple_list, region_list):
                    for feature_name in feature_list:
                        writer.write(
                            [region_label],
                            [feature_name],
                            iter_feature_rows(region, feature_name),
                        )

    # combinations = ((region, feature_name) for region in region_tuple_list for feature_name in feature_list)

    # processed_data = map(lambda combo: process_region(combo[0], primary_name, combo[1], mp, update, data_dir), combinations)

    # for i, combo in enumerate(combinations):
    #     output_creation(processed_data[i], primary_name, combo[1], [combo[0]], data_dir, out_format, out_aggregate)
