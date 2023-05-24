from earth_osm.eo import save_osm_data

def test_base():
    save_osm_data(
        region_list=["germany", "benin", "gcc-states", "SN-GM", "slovenia"],
        primary_name="power",
        feature_list=["substation", "generator", "line", "tower", "cable"],
        update=False,
        mp=True,
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )

if __name__ == '__main__':
    test_base()