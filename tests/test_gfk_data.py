import pytest

from earth_osm.gfk_data import (
    get_root_list,
    get_all_regions_dict,
    view_regions,
    get_id_by_code,
    get_code_by_id,
    get_region_dict,
    get_id_by_str,
    get_region_tuple,
    get_all_valid_list
)
from earth_osm.planet import PLANET_PBF_URL, PLANET_REGION_ID, PLANET_REGION_SHORT_CODE


def test_view():
    from pprint import pprint
    print(get_root_list())
    # visual inspection
    pprint(get_all_regions_dict(level=2))
    view_regions()

def test_regions():
    # pprint(get_region_dict('germany')) #Raises KeyError
    assert set(get_region_dict("germany").keys()) == set(
        ["id", "name", "parent", "short_code", "urls"]
    )

    earth_region = get_region_dict("earth")
    assert earth_region["id"] == PLANET_REGION_ID
    assert earth_region["short_code"] == PLANET_REGION_SHORT_CODE
    assert earth_region["urls"]["pbf"] == PLANET_PBF_URL

    # print(get_id_by_code('DE')) #Supresses KeyError
    assert get_id_by_code("DE") == "germany"

    assert get_id_by_code(PLANET_REGION_SHORT_CODE) == PLANET_REGION_ID
    assert get_id_by_code("earth") == PLANET_REGION_ID

    # print(get_code_by_id('germany')) #Supresses KeyError
    assert get_code_by_id("germany") == "DE"
    assert get_code_by_id(PLANET_REGION_ID) == PLANET_REGION_SHORT_CODE

    # print(get_id_by_str('germany')) #Raises KeyError
    assert get_id_by_str("germany") == "germany"
    assert get_id_by_str("DE") == "germany"
    assert get_id_by_str("DE") == "germany"
    assert get_id_by_str("earth") == PLANET_REGION_ID
    assert get_id_by_str(PLANET_REGION_SHORT_CODE) == PLANET_REGION_ID


def test_get_id_by_str_keyerror():
    with pytest.raises(KeyError):
        get_id_by_str("unknown country")


def test_region_tuple():
    print(get_region_tuple("germany"))
    print(get_region_tuple("germany").short)
    print(get_all_valid_list())

    planet = get_region_tuple("earth")
    assert planet.id == PLANET_REGION_ID
    assert planet.short == PLANET_REGION_SHORT_CODE
    assert planet.urls["pbf"] == PLANET_PBF_URL

    valid = get_all_valid_list()
    assert PLANET_REGION_SHORT_CODE in valid
    assert PLANET_REGION_ID in valid

def test_others():
    for o in ["gcc-states", "SN-GM"]:
        r = get_region_tuple(o)
        s = r.short


def test_namibia_na_code():
    """Test that Namibia's 'NA' ISO code is properly handled (issue #59)"""
    # Test that 'NA' is recognized as Namibia's code
    assert get_id_by_code("NA") == "namibia"
    
    # Test that get_region_tuple works with 'NA'
    region = get_region_tuple("NA")
    assert region.id == "namibia"
    assert region.short == "NA"
    
    # Test that both 'NA' and 'namibia' resolve to the same region
    region_by_code = get_region_tuple("NA")
    region_by_name = get_region_tuple("namibia")
    assert region_by_code.id == region_by_name.id
    assert region_by_code.short == region_by_name.short


