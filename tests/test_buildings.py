from earth_osm.eo import save_osm_data


def test_building(shared_data_dir):
    save_osm_data(
        region_list=["malta"],
        primary_name="building",
        feature_list=['ALL'],
        update=False,
        mp=True,
        data_dir=shared_data_dir,
        out_dir=shared_data_dir,
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )


if __name__ == '__main__':
    test_building()
