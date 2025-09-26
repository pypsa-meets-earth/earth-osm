import pandas as pd
import pytest

from earth_osm.eo import get_osm_data
from earth_osm.gfk_data import get_region_tuple


TEST_CASES = [
    pytest.param('benin', 'power', 'substation', id='benin-power-substation'),
    pytest.param('ghana', 'power', 'substation', id='ghana-power-substation'),
    pytest.param('nigeria', 'power', 'substation', id='nigeria-power-substation'),
    pytest.param('burkina-faso', 'power', 'substation', id='burkina-faso-power-substation'),
    pytest.param('benin', 'power', 'line', id='benin-power-line'),
    pytest.param('ghana', 'power', 'line', id='ghana-power-line'),
]


@pytest.mark.integration
@pytest.mark.parametrize('region_id, primary_name, feature_name', TEST_CASES)
def test_geofabrik_and_overpass_produce_comparable_results(
    tmp_path, region_id, primary_name, feature_name
):
    region = get_region_tuple(region_id)

    geofabrik_dir = tmp_path / f'geofabrik_{region_id}'
    overpass_dir = tmp_path / f'overpass_{region_id}'

    geofabrik_df = get_osm_data(
        region_id,
        primary_name,
        feature_name,
        data_dir=str(geofabrik_dir),
        cached=False,
        progress_bar=False,
        data_source='geofabrik',
    )

    overpass_df = get_osm_data(
        region_id,
        primary_name,
        feature_name,
        data_dir=str(overpass_dir),
        cached=False,
        progress_bar=False,
        data_source='overpass',
    )

    required_columns = {'id', 'Region'}
    for df in (geofabrik_df, overpass_df):
        assert not df.empty, 'Expected data from both sources'
        assert required_columns.issubset(df.columns)
        assert set(df['Region']) == {region.short}

    geofabrik_sorted = geofabrik_df.sort_values('id').set_index('id')
    overpass_sorted = overpass_df.sort_values('id').set_index('id')

    assert list(geofabrik_sorted.index) == list(overpass_sorted.index)
    assert list(geofabrik_sorted.columns) == list(overpass_sorted.columns)

    pd.testing.assert_frame_equal(
        geofabrik_sorted.drop(columns=['lonlat']),
        overpass_sorted.drop(columns=['lonlat']),
        check_like=True,
    )

    for idx, (geo_coords, over_coords) in enumerate(
        zip(geofabrik_sorted['lonlat'], overpass_sorted['lonlat'])
    ):
        assert len(geo_coords) == len(over_coords), (
            f'Mismatched coordinate lengths for id {geofabrik_sorted.index[idx]}'
        )
        for (geo_lon, geo_lat), (over_lon, over_lat) in zip(geo_coords, over_coords):
            assert geo_lon == pytest.approx(over_lon, abs=1e-9)
            assert geo_lat == pytest.approx(over_lat, abs=1e-9)
