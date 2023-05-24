from earth_osm.eo import save_osm_data


def test_tower():
    save_osm_data(
        region_list=["germany"],
        primary_name="power",
        feature_list=["tower"],
        update=False,
        mp=True,
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )

def test_substation():
    save_osm_data(
        region_list=["germany"],
        primary_name="power",
        feature_list=["substation"],
        update=False,
        mp=True,
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )

def test_generator():
    save_osm_data(
        region_list=["germany"],
        primary_name="power",
        feature_list=["generator"],
        update=False,
        mp=True,
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )

def test_line():
    save_osm_data(
        region_list=["germany"],
        primary_name="power",
        feature_list=["line"],
        update=False,
        mp=True,
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )

def test_empty_cable():
    save_osm_data(
        region_list=["benin"],
        primary_name="power",
        feature_list=["cable"],
        update=False,
        mp=True,
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )


if __name__ == '__main__':
    test_tower()
    test_substation()
    test_generator()
    test_line()
    test_empty_cable()