from earth_osm.eo import save_osm_data
import os


def test_building():
    save_osm_data(
        region_list=["malta"],
        primary_name="building",
        feature_list=['ALL'],
        update=False,
        mp=True,
        data_dir=os.path.join(os.getcwd(), "earth_data_test"),
        out_dir=os.path.join(os.getcwd(), "earth_data_test"),
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )


if __name__ == '__main__':
    test_building()
