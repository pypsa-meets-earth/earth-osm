import os
import osmium
import pandas as pd
from earth_osm.eo import get_osm_data


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
