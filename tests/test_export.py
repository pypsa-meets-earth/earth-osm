import json
import shutil
from pathlib import Path

from earth_osm.eo import save_osm_data
from earth_osm.gfk_data import get_region_tuple
from earth_osm.stream import stream_region_features
import earth_osm.stream as stream_module


primary_name = "power"
update = False
mp = True


def test_no_aggregate(shared_data_dir):
    save_osm_data(
        region_list=["nigeria", "benin"],
        primary_name=primary_name,
        feature_list=["substation", "generator", "line", "cable"],
        update=update,
        mp=mp,
        data_dir=shared_data_dir,
        out_dir=shared_data_dir,
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )
    assert True

# same as pypsa-tutorial
def test_aggregate(shared_data_dir):
    save_osm_data(
        region_list=["benin", "nigeria"],
        primary_name=primary_name,
        feature_list=["substation", "line", "cable", "generator"],
        update=update,
        mp=mp,
        data_dir=shared_data_dir,
        out_dir=shared_data_dir,
        out_format=["csv", "geojson"],
        out_aggregate=True,
    )
    assert True

def test_small_count(shared_data_dir):
    save_osm_data(
        region_list=["malta"],
        primary_name="power",
        feature_list=["plant"],
        update=update,
        mp=mp,
        data_dir=shared_data_dir,
        out_dir=shared_data_dir,
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )
    out_dir = Path(shared_data_dir) / "out"
    csv_path = out_dir / "malta_plant.csv"
    geojson_path = out_dir / "malta_plant.geojson"

    assert csv_path.exists()
    assert geojson_path.exists()

    with csv_path.open() as csv_file:
        header = csv_file.readline().strip()
    assert "lonlat" in header and "Type" in header


def test_stream_region_features(shared_data_dir):
    region = get_region_tuple("malta")
    feature_iter = stream_region_features(
        region,
        "power",
        "plant",
        shared_data_dir,
        update=False,
        progress_bar=False,
        multiprocess=False,
    )
    rows = list(feature_iter)
    assert rows, "stream produced no features"
    assert all("lonlat" in row and "Type" in row for row in rows)


def test_primary_cache_streaming(shared_data_dir, monkeypatch):
    data_dir = Path(shared_data_dir) / "primary_cache_stream"
    data_dir.mkdir(parents=True, exist_ok=True)

    call_counter = {"count": 0}
    original_stream = stream_module.stream_pbf_features

    def counting_stream(*args, **kwargs):
        call_counter["count"] += 1
        return original_stream(*args, **kwargs)

    monkeypatch.setattr(stream_module, "stream_pbf_features", counting_stream)

    cache_root = data_dir / "power"
    if cache_root.exists():
        shutil.rmtree(cache_root)

    save_osm_data(
        region_list=["malta"],
        primary_name="power",
        feature_list=["plant", "substation"],
        update=False,
        mp=False,
        data_dir=str(data_dir),
        out_dir=str(data_dir),
        out_format=["csv"],
        out_aggregate=False,
        progress_bar=False,
        stream_backend=True,
        cache_primary=True,
    )

    first_count = call_counter["count"]
    assert first_count >= 1

    assert cache_root.exists(), "primary cache directory was not created"
    cache_files = list(cache_root.glob("*.jsonl"))
    assert cache_files, "primary cache JSONL file was not created"
    cache_file = cache_files[0]

    with cache_file.open(encoding="utf-8") as fh:
        first_line = fh.readline().strip()
    assert first_line, "cache file is empty"
    record = json.loads(first_line)
    assert "Region" in record and "Type" in record

    save_osm_data(
        region_list=["malta"],
        primary_name="power",
        feature_list=["substation"],
        update=False,
        mp=False,
        data_dir=str(data_dir),
        out_dir=str(data_dir),
        out_format=["csv"],
        out_aggregate=False,
        progress_bar=False,
        stream_backend=True,
        cache_primary=True,
    )

    assert call_counter["count"] == first_count, "cache was rebuilt unexpectedly"

# test low resource feature (cable)
# test high resource feature (substation)

# test aggregation by region (benin, germany)
# test aggregation by feature (tower, line)
# test no aggregation
 
 