import os
import json
import osmium
import pandas as pd
import pytest
from earth_osm import extract, stream
from earth_osm.eo import get_osm_data
from earth_osm.osmpbf import Node, Relation, Way


@pytest.mark.parametrize("setting, workers", [(True, 3), (False, 1), (1, 1), (2, 2)])
def test_extraction_worker_limits(monkeypatch, tmp_path, setting, workers):
    path = str(tmp_path / "tiny.osm.pbf")
    with osmium.SimpleWriter(path) as writer:
        writer.add_node(osmium.osm.mutable.Node(id=1, location=(1, 2)))
        writer.add_node(osmium.osm.mutable.Node(id=2, location=(3, 4)))
        for identifier, feature in [(10, "line"), (11, "cable")]:
            writer.add_way(
                osmium.osm.mutable.Way(id=identifier, nodes=[1, 2], tags={"power": feature})
            )

    counts = []
    original_pool = extract.mp.Pool

    def recording_pool(processes=None, **kwargs):
        counts.append(processes)
        return original_pool(processes=processes, **kwargs)

    monkeypatch.setattr(extract.mp, "cpu_count", lambda: 4)
    monkeypatch.setattr(extract.mp, "Pool", recording_pool)
    for function, selection in [
        (stream.stream_pbf_features, "line"),
        (stream.stream_pbf_features_multi, ["line", "cable"]),
    ]:
        expected = list(function(path, "power", selection, "MT", multiprocess=False))
        counts.clear()
        actual = list(function(path, "power", selection, "MT", multiprocess=setting))
        assert len(actual) == (1 if selection == "line" else 2)
        assert sorted(json.dumps(row, sort_keys=True) for row in actual) == sorted(
            json.dumps(row, sort_keys=True) for row in expected
        )
        assert counts == ([] if setting is False else [workers, workers])

    prefilter = {kind: {"power": ["line"]} for kind in (Node, Way, Relation)}
    expected = extract.filter_pbf(path, prefilter, multiprocess=False)
    counts.clear()
    assert extract.filter_pbf(path, prefilter, multiprocess=setting) == expected
    assert counts == [workers]


@pytest.mark.parametrize("setting", [0, -1])
def test_invalid_worker_count(setting):
    with pytest.raises(ValueError):
        extract.resolve_worker_count(setting)


class PowerLineHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.power_features = set()  # Store unique IDs instead of multiple records

    def node(self, n):
        if "power" in n.tags and n.tags["power"] == "line":
            self.power_features.add(n.id)

    def way(self, w):
        if "power" in w.tags and w.tags["power"] == "line":
            self.power_features.add(w.id)

    def area(self, a):
        if "power" in a.tags and a.tags["power"] == "line":
            self.power_features.add(a.id)

    def get_unique_count(self):
        return len(self.power_features)


def test_osmium(shared_data_dir):
    region = "benin"  # Use Benin instead of Nigeria for faster testing
    primary_name = "power"
    feature_name = "line"
    mp = True
    update = False
    data_dir = shared_data_dir

    df = get_osm_data(region, primary_name, feature_name, data_dir=data_dir)

    pbf_fp = os.path.join(shared_data_dir, "pbf", f"{region}-latest.osm.pbf")

    osmium_handler = PowerLineHandler()
    osmium_handler.apply_file(pbf_fp, locations=True)

    # Compare unique feature counts instead of record counts
    # Our implementation returns one record per unique feature
    our_count = len(df)
    osmium_count = osmium_handler.get_unique_count()

    assert our_count == osmium_count, f"Unique feature counts are not equal: {our_count} != {osmium_count}"


if __name__ == "__main__":
    test_osmium("earth_data_test")
