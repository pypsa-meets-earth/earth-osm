import os
import osmium
import pandas as pd
from earth_osm.eo import get_osm_data

class PowerLineHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.power_lines = []
        
    def way(self, w):
        if 'power' in w.tags and w.tags['power'] == 'line':
            for node in w.nodes:
                location = osmium.osm.Location(node.lon, node.lat)
                self.power_lines.append({
                    'id': w.id,
                    'version': w.version,
                    'visible': w.visible,
                    'timestamp': w.timestamp,
                    'uid': w.uid,
                    'user': w.user,
                    'changeset': w.changeset,
                    'latitude': location.lat if location else None,
                    'longitude': location.lon if location else None,
                })

    def get_dataframe(self):
        return pd.DataFrame(self.power_lines)


def test_osmium(shared_data_dir):
    region = "nigeria"
    primary_name = "power"
    feature_name = "line"
    mp = True
    update = False
    data_dir = shared_data_dir

    df = get_osm_data(
        region, 
        primary_name, 
        feature_name,
        data_dir=data_dir
        )
    
    pbf_fp = os.path.join(shared_data_dir, "pbf", f"{region}-latest.osm.pbf")
    
    omsium_handler = PowerLineHandler()
    omsium_handler.apply_file(pbf_fp, locations=True)



    df2 = omsium_handler.get_dataframe()

    df2.drop_duplicates(subset='id', inplace=True)

    assert len(df) == len(df2), f"Lengths are not equal: {len(df)} != {len(df2)}"


if __name__ == "__main__":
    test_osmium('earth_data_test')