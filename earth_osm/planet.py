"""Utilities for working with the OpenStreetMap planet extracts.

This module centralizes the metadata required to treat the global planet file
as a first-class region within the earth-osm pipelines. The download helper
wraps the existing GeoFabrik downloader so callers can fetch the weekly
planetary snapshot without duplicating verification logic.
"""

from __future__ import annotations

from copy import deepcopy

from earth_osm.gfk_download import download_pbf

PLANET_REGION_ID = "earth"
PLANET_REGION_SHORT_CODE = "EARTH"

PLANET_PBF_URL = "https://osm-pds.s3.amazonaws.com/planet-latest.osm.pbf"
PLANET_MD5_URL = f"{PLANET_PBF_URL}.md5"
PLANET_TORRENT_URL = "https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf.torrent"
PLANET_BZ2_URL = "https://planet.openstreetmap.org/planet/planet-latest.osm.bz2"
PLANET_HISTORY_PBF_URL = (
    "https://planet.openstreetmap.org/planet/full-history/full-history-latest.osm.pbf"
)
PLANET_CHANGESETS_URL = "https://planet.openstreetmap.org/planet/changesets-latest.osm.bz2"
PLANET_UPDATES_BASE_URL = "https://planet.openstreetmap.org/replication/"

PLANET_REGION = {
    "id": PLANET_REGION_ID,
    "parent": None,
    "name": "Planet Earth",
    "urls": {
        "pbf": PLANET_PBF_URL,
        "bz2": PLANET_BZ2_URL,
        "history": PLANET_HISTORY_PBF_URL,
        "changesets": PLANET_CHANGESETS_URL,
        "updates": PLANET_UPDATES_BASE_URL,
        "md5": PLANET_MD5_URL,
        "torrent": PLANET_TORRENT_URL,
    },
    "short_code": PLANET_REGION_SHORT_CODE,
}


def get_planet_region_dict() -> dict[str, object]:
    """Return a mutable deepcopy of the planet region metadata."""

    region = deepcopy(PLANET_REGION)
    return region


def download_planet_pbf(
    update: bool,
    data_dir: str,
    *,
    progress_bar: bool = True,
) -> str:
    """Download the latest planet PBF file into the shared data directory."""

    return download_pbf(PLANET_PBF_URL, update, data_dir, progress_bar=progress_bar)


__all__ = [
    "PLANET_REGION",
    "PLANET_REGION_ID",
    "PLANET_REGION_SHORT_CODE",
    "PLANET_PBF_URL",
    "PLANET_MD5_URL",
    "PLANET_TORRENT_URL",
    "PLANET_BZ2_URL",
    "PLANET_HISTORY_PBF_URL",
    "PLANET_CHANGESETS_URL",
    "PLANET_UPDATES_BASE_URL",
    "get_planet_region_dict",
    "download_planet_pbf",
]
