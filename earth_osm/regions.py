"""Shared region helpers for earth-osm data sources.

This module centralises region lookup utilities so both GeoFabrik/planet-based
pipelines and Overpass-based pipelines can rely on the same access patterns.
It delegates to :mod:`earth_osm.gfk_data` for the underlying catalogue and adds
small convenience helpers that express common orchestration needs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional, Sequence

from earth_osm.gfk_data import (
    get_all_valid_list as _get_all_valid_list,
    get_children_regions as _gfk_get_children_regions,
    get_region_dict as _gfk_get_region_dict,
    get_region_tuple as _gfk_get_region_tuple,
    get_region_tuple_historical as _gfk_get_region_tuple_historical,
    get_root_list as _gfk_get_root_list,
    view_regions as _gfk_view_regions,
)
from earth_osm.planet import (
    PLANET_REGION_ID,
    PLANET_REGION_SHORT_CODE,
    get_planet_region_dict,
    download_planet_pbf,
)
from earth_osm.gfk_download import download_pbf

def get_region_tuple(region_str: str):
    """Return the GeoFabrik region tuple for ``region_str``.

    This is a thin wrapper around :func:`earth_osm.gfk_data.get_region_tuple`
    that allows callers to depend on the shared regions module instead of the
    GeoFabrik-specific implementation detail.
    """

    return _gfk_get_region_tuple(region_str)


def get_region_tuple_historical(
    region_str: str,
    target_date: Optional[datetime],
):
    """Return a region tuple with historical download metadata."""

    return _gfk_get_region_tuple_historical(region_str, target_date)


def get_region_dict(region_id: str) -> dict:
    """Return a mutable dictionary describing a region."""

    return _gfk_get_region_dict(region_id)


def get_children_regions(parent_id: str, *, require_iso: bool = True) -> List:
    """Return child regions for ``parent_id``.

    Args:
        parent_id: Region identifier.
        require_iso: When ``True`` only include children that expose an ISO short
            code, matching the historic behaviour in Overpass orchestration.
    """

    return _gfk_get_children_regions(parent_id, require_iso=require_iso)


def is_iso_region(region) -> bool:
    """Return ``True`` when ``region`` has a two-letter ISO short code."""

    short = getattr(region, "short", "")
    if not isinstance(short, str):
        return False
    normalized = short.strip()
    return len(normalized) == 2 and normalized.isalpha()


def expand_region_to_iso_children(region, *, require_iso: bool = True) -> List:
    """Return a list of regions suitable for ISO-based processing.

    If ``region`` already carries an ISO short code the list will contain only
    ``region``. Otherwise, its ISO-coded children are returned. When no children
    match the criteria the original region is yielded as a fallback so callers
    can continue processing.
    """

    if is_iso_region(region):
        return [region]

    children = get_children_regions(region.id, require_iso=require_iso)
    if children:
        return children

    return [region]


def iter_region_hierarchy(regions: Sequence) -> Iterable:
    """Yield regions from ``regions`` depth-first, expanding ISO children."""

    for region in regions:
        yield from expand_region_to_iso_children(region)


def is_planet_region(region) -> bool:
    """Return ``True`` when ``region`` represents the planet extract."""

    return getattr(region, "id", None) == PLANET_REGION_ID


def download_region_pbf(
    region,
    update: bool,
    data_dir: str,
    *,
    progress_bar: bool = True,
) -> str:
    """Download the PBF archive for ``region`` and return the local path."""

    if is_planet_region(region):
        return download_planet_pbf(update, data_dir, progress_bar=progress_bar)

    target_date = getattr(region, "target_date", None)
    region_id = getattr(region, "id", None)

    if target_date is not None:
        base_url = getattr(region, "base_url", None)
        source = base_url or region.urls.get("pbf")
        return download_pbf(
            source,
            update,
            data_dir,
            progress_bar=progress_bar,
            target_date=target_date,
            region_id=region_id,
        )

    pbf_url = region.urls["pbf"]
    return download_pbf(pbf_url, update, data_dir, progress_bar=progress_bar)


def get_all_valid_codes() -> List[str]:
    """Return all valid region identifiers and short codes."""

    return _get_all_valid_list()


def get_root_regions() -> List[str]:
    """Return the identifiers for root (continent-level) regions."""

    return _gfk_get_root_list()


def view_regions(level: int = 0):
    """Proxy to :func:`earth_osm.gfk_data.view_regions`."""

    return _gfk_view_regions(level)


__all__ = [
    "PLANET_REGION_ID",
    "PLANET_REGION_SHORT_CODE",
    "get_planet_region_dict",
    "get_region_tuple",
    "get_region_tuple_historical",
    "get_region_dict",
    "get_children_regions",
    "is_iso_region",
    "expand_region_to_iso_children",
    "iter_region_hierarchy",
    "is_planet_region",
    "download_region_pbf",
    "get_all_valid_codes",
    "get_root_regions",
    "view_regions",
]
