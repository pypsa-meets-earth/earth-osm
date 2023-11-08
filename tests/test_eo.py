import os
from earth_osm.eo import save_osm_data

def test_base():
    save_osm_data(
        region_list=["denmark", "benin"],
        primary_name="power",
        feature_list=["substation", "generator", "line", "cable"],
        update=False,
        mp=True,
        data_dir=os.path.join(os.getcwd(), "earth_data_test"),
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )

if __name__ == '__main__':
    test_base()