import pandas as pd
import pytest

from earth_osm.eo import get_osm_data
from earth_osm.gfk_data import get_region_tuple


TEST_CASES = [
    pytest.param('benin', 'power', 'substation', id='benin-power-substation'),
    pytest.param('benin', 'power', 'line', id='benin-power-line'),
]

def test_overpass_disallows_all_wildcard(tmp_path):
    with pytest.raises(ValueError, match="Overpass backend does not support wildcard"):
        get_osm_data(
            'benin',
            'power',
            'ALL_power',
            data_dir=str(tmp_path / 'overpass_all'),
            cached=False,
            progress_bar=False,
            data_source='overpass',
        )


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

    # Compare overlapping non-null values to stay resilient to upstream tag churn.
    for column in geofabrik_sorted.columns:
        if column == 'lonlat':
            continue

        geofabrik_series = geofabrik_sorted[column]
        overpass_series = overpass_sorted[column]

        overlap = geofabrik_series.notna() & overpass_series.notna()
        if not overlap.any():
            continue

        pd.testing.assert_series_equal(
            geofabrik_series[overlap],
            overpass_series[overlap],
            check_names=False,
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
