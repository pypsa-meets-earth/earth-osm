import os
from earth_osm.eo import save_osm_data

def test_pypsa_tutorial():
    save_osm_data(
        region_list=["benin", "nigeria"],
        primary_name="power",
        feature_list=["substation", "line", "cable", "generator"],
        update=False,
        mp=True,
        data_dir=os.path.join(os.getcwd(), "earth_data_test"),
        out_dir=os.path.join(os.getcwd(), "earth_data_test"),
        out_format=["csv", "geojson"],
        out_aggregate=True,
    )

def test_pypsa_landlock():
    save_osm_data(
        region_list=["BW"],
        primary_name="power",
        feature_list=["substation", "line", "cable", "generator"],
        update=False,
        mp=True,
        data_dir=os.path.join(os.getcwd(), "earth_data_test"),
        out_dir=os.path.join(os.getcwd(), "earth_data_test"),
        out_format=["csv", "geojson"],
        out_aggregate=True,
    )

if __name__ == '__main__':
    # test_pypsa_tutorial()
    test_pypsa_landlock()