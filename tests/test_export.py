import os
from earth_osm.eo import save_osm_data


primary_name = "power"
update = False
mp = True
data_dir = os.path.join(os.getcwd(), "earth_data_test")
out_dir = os.path.join(os.getcwd(), "earth_data_test")


def test_no_aggregate(shared_data_dir):
    save_osm_data(
        region_list=["nigeria", "benin"],
        primary_name=primary_name,
        feature_list=["substation", "generator", "line", "cable"],
        update=update,
        mp=mp,
        data_dir=shared_data_dir,
        out_dir=out_dir,
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )
    assert True

# same as pypsa-tutorial
def test_aggregate(shared_data_dir):
    save_osm_data(
        region_list=["benin", "nigeria"],
        primary_name=primary_name,
        feature_list=["substation", "line", "cable", "generator"],
        update=update,
        mp=mp,
        data_dir=data_dir,
        out_dir=out_dir,
        out_format=["csv", "geojson"],
        out_aggregate=True,
    )
    assert True

def test_small_count(shared_data_dir):
    save_osm_data(
        region_list=["malta"],
        primary_name="power",
        feature_list=["plant"],
        update=update,
        mp=mp,
        data_dir=data_dir,
        out_dir=out_dir,
        out_format=["csv", "geojson"],
        out_aggregate=False,
    )
    assert True

# test low resource feature (cable)
# test high resource feature (substation)

# test aggregation by region (benin, germany)
# test aggregation by feature (tower, line)
# test no aggregation
 
 