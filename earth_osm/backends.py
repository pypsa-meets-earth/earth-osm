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
from earth_osm.lifecycle import add_lifecycle_columns, filter_by_status


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
    allowed_statuses=None,  # NEW PARAMETER
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
    
    # ADD LIFECYCLE PROCESSING
    if not df_feature.empty and feature_name[:4] != 'ALL_':
        df_feature = add_lifecycle_columns(df_feature, feature_name)
        if allowed_statuses:
            df_feature = filter_by_status(df_feature, allowed_statuses)
    
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
    allowed_statuses=None,  # NEW PARAMETER
) -> StreamPayload:
    """Yield flattened feature dictionaries using the streaming pipeline."""
    
    from earth_osm.lifecycle import determine_type_and_status  # Import here

    pbf_url = region.urls["pbf"]
    logger.info(
        "Region %s (%s=%s): downloading %s",
        region.short,
        os.path.basename(pbf_url),
        primary_name,
        feature_name,
    )
    filename = download_region_pbf(region, update, data_dir, progress_bar=progress_bar)

    if cache_primary:
        cache_path = primary_cache_path(data_dir, region.short, primary_name, filename)
        row_iterator = stream_cached_primary_features(
            filename,
            primary_name,
            feature_name,
            region.short,
            cache_path,
            multiprocess=mp,
            rebuild_cache=update,
        )
    else:
        row_iterator = stream_pbf_features(
            filename,
            primary_name,
            feature_name,
            region.short,
            multiprocess=mp,
        )
    
    # ADD LIFECYCLE FILTERING for streaming
    # Wrap the iterator to filter and add status on-the-fly
    if feature_name[:4] != 'ALL_':
        def lifecycle_filter_stream(rows):
            for row in rows:
                # Build tags dict from row
                tags = {k[5:]: v for k, v in row.items() if k.startswith('tags.') and v is not None}
                
                # Determine actual type and status
                actual_type, status = determine_type_and_status(tags)
                
                # Skip if wrong type
                if actual_type != feature_name:
                    continue
                
                # Skip if status not allowed
                if allowed_statuses and status not in allowed_statuses:
                    continue
                
                # Add status to row
                row['status'] = status
                row['feature_type'] = actual_type
                
                yield row
        
        return lifecycle_filter_stream(row_iterator)
    
    return row_iterator


def overpass_backend(
    region,
    primary_name: str,
    feature_name: str,
    *,
    data_dir: str,
    allowed_statuses=None,  # NEW PARAMETER
) -> LegacyPayload:
    rows = list(iter_overpass_rows(region, primary_name, feature_name, data_dir))
    df_feature = pd.DataFrame(rows)
    df_feature.dropna(axis=1, how="all", inplace=True)
    
    # ADD LIFECYCLE PROCESSING
    if not df_feature.empty and feature_name[:4] != 'ALL_':
        from earth_osm.lifecycle import add_lifecycle_columns, filter_by_status
        df_feature = add_lifecycle_columns(df_feature, feature_name)
        if allowed_statuses:
            df_feature = filter_by_status(df_feature, allowed_statuses)
    
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
    allowed_statuses=None,  # NEW PARAMETER
) -> BackendResult:
    """Select the appropriate backend and return a tagged payload."""

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
                allowed_statuses=allowed_statuses,  # PASS THROUGH
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
            allowed_statuses=allowed_statuses,  # PASS THROUGH
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
            allowed_statuses=allowed_statuses,  # PASS THROUGH
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
