from pathlib import Path

import pytest
import requests

import earth_osm.planet as planet_module
from earth_osm.eo import save_osm_data
from earth_osm.gfk_data import get_region_tuple
from earth_osm.planet import (
    PLANET_MD5_URL,
    PLANET_PBF_URL,
    PLANET_REGION_ID,
    PLANET_REGION_SHORT_CODE,
)


def test_planet_region_tuple_metadata():
    region = get_region_tuple("earth")

    assert region.id == PLANET_REGION_ID
    assert region.short == PLANET_REGION_SHORT_CODE
    assert region.urls["pbf"] == PLANET_PBF_URL
    assert PLANET_PBF_URL.startswith("https://osm-pds.s3.amazonaws.com/")
    assert region.urls["md5"] == PLANET_MD5_URL


def test_save_osm_data_streams_planet(monkeypatch, tmp_path):

    # swap planet download to use the lightweight Malta extract
    malta_pbf_url = "https://download.geofabrik.de/europe/malta-latest.osm.pbf"
    malta_md5_url = f"{malta_pbf_url}.md5"

    monkeypatch.setattr(planet_module, "PLANET_PBF_URL", malta_pbf_url)
    monkeypatch.setattr(planet_module, "PLANET_MD5_URL", malta_md5_url)
    monkeypatch.setitem(planet_module.PLANET_REGION["urls"], "pbf", malta_pbf_url)
    monkeypatch.setitem(planet_module.PLANET_REGION["urls"], "md5", malta_md5_url)

    try:
        save_osm_data(
            region_list=["earth"],
            primary_name="power",
            feature_list=["line"],
            out_format=["csv"],
            out_aggregate=True,
            out_dir=str(tmp_path / "out"),
            data_dir=str(tmp_path),
            update=False,
            mp=False,
            progress_bar=False,
            stream_backend=True,
            cache_primary=False,
        )
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"Malta PBF download unavailable: {exc}")

    downloaded_name = Path(malta_pbf_url).name
    planet_file = Path(tmp_path) / "pbf" / downloaded_name
    assert planet_file.exists(), "planet download was not materialised"

    csv_path = Path(tmp_path) / "out" / "out" / "EARTH_line.csv"
    assert csv_path.exists(), "CSV output for planet extraction missing"
    with csv_path.open(encoding="utf-8") as fh:
        header = fh.readline().strip()
        data_line = fh.readline().strip()
    assert header, "CSV header missing"
    assert data_line, "CSV content missing"