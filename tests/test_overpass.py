import pandas as pd
import pytest

import earth_osm.overpass as overpass_module
from earth_osm.eo import get_osm_data
from earth_osm.gfk_data import get_region_tuple


TEST_CASES = [
    pytest.param('benin', 'power', 'substation', id='benin-power-substation'),
    pytest.param('benin', 'power', 'line', id='benin-power-line'),
]


def test_overpass_reads_endpoint_and_timeouts_from_env(monkeypatch, tmp_path):
    captured_request = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                'elements': [
                    {
                        'type': 'node',
                        'id': 1,
                        'lat': 6.3677,
                        'lon': 2.4253,
                        'tags': {'power': 'substation'},
                    }
                ]
            }

    def fake_post(url, data, timeout):
        captured_request['url'] = url
        captured_request['data'] = data
        captured_request['timeout'] = timeout
        return FakeResponse()

    monkeypatch.setenv(
        'EO_OVERPASS_ENDPOINT',
        'https://overpass.private.coffee/api/interpreter',
    )
    monkeypatch.setenv('EO_OVERPASS_REQUEST_TIMEOUT', '120')
    monkeypatch.setenv('EO_OVERPASS_QUERY_TIMEOUT', '60')
    monkeypatch.setattr(overpass_module._SESSION, 'post', fake_post)

    df = get_osm_data(
        'benin',
        'power',
        'substation',
        data_dir=str(tmp_path),
        cached=False,
        progress_bar=False,
        data_source='overpass',
    )

    assert captured_request['url'] == 'https://overpass.private.coffee/api/interpreter'
    assert captured_request['timeout'] == 120
    assert '[timeout:60]' in captured_request['data']
    assert not df.empty
    assert 'id' in df.columns


@pytest.mark.parametrize(
    'env_name',
    ['EO_OVERPASS_REQUEST_TIMEOUT', 'EO_OVERPASS_QUERY_TIMEOUT'],
)
@pytest.mark.parametrize('value', ['not-an-int', '0'])
def test_overpass_timeout_env_values_must_be_positive_integers(
    monkeypatch,
    env_name,
    value,
):
    monkeypatch.setenv(env_name, value)

    with pytest.raises(ValueError, match=f'{env_name} must be a positive integer'):
        if env_name == 'EO_OVERPASS_QUERY_TIMEOUT':
            overpass_module.build_overpass_query('BJ', 'power', 'substation')
        else:
            overpass_module.fetch_overpass_data('query')


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
