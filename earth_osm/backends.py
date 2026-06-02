"""Backend adapters for region data extraction.

This module centralises the logic for selecting and executing the
available data pipelines (streaming vs. legacy extract) for each data
source (currently Geofabrik and Overpass).
"""

from __future__ import annotations

import logging
import os
from typing import Dict, Iterator, Tuple, Union

import pandas as pd

from earth_osm.filter import get_filtered_data
from earth_osm.overpass import iter_overpass_rows, rows_from_feature_dict
from earth_osm.regions import download_region_pbf
from earth_osm.stream import (
    primary_cache_path,
    stream_cached_primary_features,
    stream_pbf_features,
)

logger = logging.getLogger("eo.backends")
logger.setLevel(logging.INFO)


LegacyPayload = pd.DataFrame
StreamPayload = Iterator[Dict[str, object]]
BackendResult = Tuple[str, Union[LegacyPayload, StreamPayload]]

def geofabrik_legacy_backend(
    region,
    primary_name: str,
    feature_name: str,
    *,
    mp: bool,
    update: bool,
    data_dir: str,
    progress_bar: bool = True,
) -> LegacyPayload:
    """Return a pandas DataFrame using the legacy extract pipeline."""

    primary_dict, feature_dict = get_filtered_data(
        region,
        primary_name,
        feature_name,
        mp,
        update,
        data_dir,
        progress_bar=progress_bar,
    )

    rows = list(
        rows_from_feature_dict(
            feature_dict,
            region.short,
            primary_dict,
        )
    )

    df_feature = pd.DataFrame(rows)
    df_feature.dropna(axis=1, how="all", inplace=True)
    return df_feature


def geofabrik_stream_backend(
    region,
    primary_name: str,
    feature_name: str,
    *,
    mp: bool,
    update: bool,
    data_dir: str,
    progress_bar: bool = True,
    cache_primary: bool = False,
) -> StreamPayload:
    """Yield flattened feature dictionaries using the streaming pipeline."""

    pbf_url = region.urls["pbf"]
    logger.info(
        "Region %s (%s=%s): downloading %s",
        region.short,
        primary_name,
        feature_name,
        os.path.basename(pbf_url),
    )
    filename = download_region_pbf(region, update, data_dir, progress_bar=progress_bar)

    if cache_primary:
        cache_path = primary_cache_path(data_dir, region.short, primary_name, filename)
        return stream_cached_primary_features(
            filename,
            primary_name,
            feature_name,
            region.short,
            cache_path,
            multiprocess=mp,
            rebuild_cache=update,
        )

    return stream_pbf_features(
        filename,
        primary_name,
        feature_name,
        region.short,
        multiprocess=mp,
    )


def overpass_backend(
    region,
    primary_name: str,
    feature_name: str,
    *,
    data_dir: str,
) -> LegacyPayload:
    rows = list(iter_overpass_rows(region, primary_name, feature_name, data_dir))
    df_feature = pd.DataFrame(rows)
    df_feature.dropna(axis=1, how="all", inplace=True)
    return df_feature


def fetch_region_backend(
    region,
    primary_name: str,
    feature_name: str,
    *,
    data_source: str,
    use_stream: bool,
    mp: bool,
    update: bool,
    data_dir: str,
    progress_bar: bool = True,
    cache_primary: bool = False,
) -> BackendResult:
    """Select the appropriate backend and return a tagged payload.

    Returns:
        A tuple where the first element is either ``"stream"`` or
        ``"dataframe"`` indicating the payload type, and the second element is
        the payload itself.
    """

    if data_source == "geofabrik":
        if use_stream:
            iterator = geofabrik_stream_backend(
                region,
                primary_name,
                feature_name,
                mp=mp,
                update=update,
                data_dir=data_dir,
                progress_bar=progress_bar,
                cache_primary=cache_primary,
            )
            return "stream", iterator
        dataframe = geofabrik_legacy_backend(
            region,
            primary_name,
            feature_name,
            mp=mp,
            update=update,
            data_dir=data_dir,
            progress_bar=progress_bar,
        )
        return "dataframe", dataframe

    if data_source == "overpass":
        if use_stream:
            raise ValueError(
                "Streaming export is not supported for the Overpass backend."
            )
        dataframe = overpass_backend(
            region,
            primary_name,
            feature_name,
            data_dir=data_dir,
        )
        return "dataframe", dataframe

    raise ValueError(f"Unsupported data source: {data_source}")


__all__ = [
    "BackendResult",
    "fetch_region_backend",
    "geofabrik_legacy_backend",
    "geofabrik_stream_backend",
    "overpass_backend",
]
