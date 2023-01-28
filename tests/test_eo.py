from earth_osm.eo import get_osm_data


def test_base():
    get_osm_data(
        region_list=["benin"],
        primary_name="power",
        feature_list=["substation", "line", "generator", "tower"],
        update=True,
        mp=True,
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )


if __name__ == 'main':
    test_base()