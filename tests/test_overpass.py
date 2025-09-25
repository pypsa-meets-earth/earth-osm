import pytest
import os
from unittest.mock import patch, MagicMock
import pandas as pd

from earth_osm.eo import get_osm_data
from earth_osm.overpass import (
    build_overpass_query,
    fetch_overpass_data,
    transform_overpass_to_internal_format,
    get_overpass_data
)
from earth_osm.gfk_data import get_region_tuple


def test_build_overpass_query():
    """Test Overpass query building for different feature types."""

    # Test power substation query
    query = build_overpass_query('BJ', 'power', 'substation')
    assert 'area["ISO3166-1"="BJ"]' in query
    assert 'nwr["power"="substation"]' in query
    assert '[out:json]' in query
    assert 'out body geom' in query

    # Test power line query
    query = build_overpass_query('TG', 'power', 'line')
    assert 'area["ISO3166-1"="TG"]' in query
    assert 'way["power"="line"]' in query

    # Test power generator query
    query = build_overpass_query('GH', 'power', 'generator')
    assert 'area["ISO3166-1"="GH"]' in query
    assert 'nwr["power"="generator"]' in query

    # Test generic power feature
    query = build_overpass_query('NG', 'power', 'tower')
    assert 'area["ISO3166-1"="NG"]' in query
    assert 'node["power"="tower"]' in query

    # Test non-power feature
    query = build_overpass_query('SN', 'amenity', 'school')
    assert 'area["ISO3166-1"="SN"]' in query
    assert 'nwr["amenity"="school"]' in query


def test_transform_overpass_to_internal_format():
    """Test transformation of Overpass API response to internal format."""

    # Mock Overpass API response
    mock_response = {
        'elements': [
            {
                'type': 'node',
                'id': 12345,
                'lat': 10.0,
                'lon': 2.0,
                'tags': {'power': 'tower'}
            },
            {
                'type': 'way',
                'id': 67890,
                'nodes': [12345, 54321],
                'tags': {'power': 'line', 'voltage': '33000'}
            },
            {
                'type': 'node',
                'id': 54321,
                'lat': 11.0,
                'lon': 3.0,
                'tags': {}
            },
            {
                'type': 'relation',
                'id': 99999,
                'members': [{'type': 'way', 'ref': 67890, 'role': ''}],
                'tags': {'power': 'substation', 'name': 'Test Substation'}
            }
        ]
    }

    primary_dict, feature_dict = transform_overpass_to_internal_format(
        mock_response, 'power', 'line'
    )

    # Check structure
    assert 'Metadata' in primary_dict
    assert 'Data' in primary_dict
    assert 'Node' in primary_dict['Data']
    assert 'Way' in primary_dict['Data']
    assert 'Relation' in primary_dict['Data']

    # Check metadata
    assert primary_dict['Metadata']['primary_feature'] == 'power'
    assert 'filter_date' in primary_dict['Metadata']

    # Check that all nodes are in primary data (needed for way references)
    assert '12345' in primary_dict['Data']['Node']
    assert '54321' in primary_dict['Data']['Node']

    # Check that power elements are in primary data
    assert '67890' in primary_dict['Data']['Way']  # power=line
    assert '12345' in primary_dict['Data']['Node']  # power=tower
    assert '99999' in primary_dict['Data']['Relation']  # power=substation

    # Check that only line elements are in feature data
    assert '67890' in feature_dict['Data']['Way']  # power=line matches
    assert '12345' not in feature_dict['Data']['Node']  # power=tower, not line
    assert '99999' not in feature_dict['Data']['Relation']  # power=substation, not line

    # Check coordinate structure
    node_data = primary_dict['Data']['Node']['12345']
    assert node_data['lonlat'] == [2.0, 10.0]
    assert node_data['id'] == 12345
    assert node_data['tags'] == {'power': 'tower'}

    # Check way refs
    way_data = primary_dict['Data']['Way']['67890']
    assert way_data['refs'] == [12345, 54321]
    assert way_data['tags'] == {'power': 'line', 'voltage': '33000'}

    # Check relation members
    relation_data = primary_dict['Data']['Relation']['99999']
    assert relation_data['members'] == [{'type': 'way', 'ref': 67890, 'role': ''}]
    assert relation_data['tags'] == {'power': 'substation', 'name': 'Test Substation'}


@patch('earth_osm.overpass.fetch_overpass_data')
def test_get_overpass_data_integration(mock_fetch):
    """Test the complete get_overpass_data function with mocked API response."""

    # Mock Overpass API response
    mock_response = {
        'elements': [
            {
                'type': 'node',
                'id': 1001,
                'lat': 6.5,
                'lon': 2.6,
                'tags': {'power': 'substation', 'name': 'Test Substation'}
            },
            {
                'type': 'way',
                'id': 2001,
                'nodes': [1001, 1002],
                'tags': {'power': 'substation', 'substation': 'transmission'}
            },
            {
                'type': 'node',
                'id': 1002,
                'lat': 6.6,
                'lon': 2.7,
                'tags': {}
            }
        ]
    }

    mock_fetch.return_value = mock_response

    # Get region
    region = get_region_tuple('benin')

    # Call get_overpass_data
    primary_dict, feature_dict = get_overpass_data(
        region, 'power', 'substation', '/tmp/test_data', True
    )

    # Verify mock was called
    mock_fetch.assert_called_once()

    # Check results
    assert len(feature_dict['Data']['Node']) == 1  # 1 power=substation node
    assert len(feature_dict['Data']['Way']) == 1   # 1 power=substation way
    assert len(primary_dict['Data']['Node']) == 2  # All nodes (including references)

    # Check specific data
    assert '1001' in feature_dict['Data']['Node']
    assert '2001' in feature_dict['Data']['Way']
    assert primary_dict['Data']['Node']['1001']['tags']['name'] == 'Test Substation'


@patch('earth_osm.overpass.requests.post')
def test_fetch_overpass_data_success(mock_post):
    """Test successful data fetching from Overpass API."""

    mock_response = MagicMock()
    mock_response.json.return_value = {'elements': []}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    query = "test query"
    result = fetch_overpass_data(query, retries=1)

    mock_post.assert_called_once_with(
        "https://overpass-api.de/api/interpreter",
        data=query,
        timeout=600
    )
    assert result == {'elements': []}


@patch('earth_osm.overpass.requests.post')
def test_fetch_overpass_data_retry_on_error(mock_post):
    """Test retry mechanism on API errors."""

    # First call fails, second succeeds
    mock_response_fail = MagicMock()
    mock_response_fail.raise_for_status.side_effect = Exception("Server Error")

    mock_response_success = MagicMock()
    mock_response_success.json.return_value = {'elements': []}
    mock_response_success.raise_for_status.return_value = None

    mock_post.side_effect = [mock_response_fail, mock_response_success]

    query = "test query"
    result = fetch_overpass_data(query, retries=2, wait_time=0)  # No wait for test speed

    assert mock_post.call_count == 2
    assert result == {'elements': []}


@patch('earth_osm.overpass.get_overpass_data')
def test_get_osm_data_with_overpass_source(mock_get_overpass_data):
    """Test get_osm_data function with overpass data source."""

    # Mock the process_region call chain
    with patch('earth_osm.eo.process_region') as mock_process:
        mock_df = pd.DataFrame({'id': [1], 'tags': [{}]})
        mock_process.return_value = mock_df

        # Test with overpass data source
        result = get_osm_data(
            'benin',
            'power',
            'substation',
            data_dir='/tmp/test',
            data_source='overpass'
        )

        # Verify process_region was called with overpass data source
        mock_process.assert_called_once()
        call_args = mock_process.call_args
        assert call_args[1]['data_source'] == 'overpass'

        # Check result is a DataFrame
        assert isinstance(result, pd.DataFrame)


def test_region_support():
    """Test that different regions work with Overpass queries."""

    test_regions = ['benin', 'togo', 'nigeria', 'ghana']

    for region_str in test_regions:
        region = get_region_tuple(region_str)
        query = build_overpass_query(region.short, 'power', 'substation')

        # Check that the region's ISO code is in the query
        assert f'area["ISO3166-1"="{region.short}"]' in query
        assert '[out:json]' in query
        assert 'out body geom' in query


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv('SKIP_INTEGRATION_TESTS', 'true').lower() == 'true',
    reason="Integration test skipped (set SKIP_INTEGRATION_TESTS=false to run)"
)
def test_actual_overpass_api_call(shared_data_dir):
    """
    Integration test that makes an actual call to the Overpass API.
    This test is skipped by default to avoid API calls in CI.
    Run with: pytest tests/test_overpass.py::test_actual_overpass_api_call -m integration -s
    """

    # Use a small region and specific feature to minimize API load
    result_df = get_osm_data(
        'togo',  # Small country to minimize data
        'power',
        'substation',
        data_dir=shared_data_dir,
        data_source='overpass'
    )

    # Basic assertions
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) > 0, "Should have found at least some power substations in Togo"

    # Check expected columns exist
    expected_columns = ['id', 'lonlat', 'Type', 'Region']
    for col in expected_columns:
        assert col in result_df.columns, f"Column {col} missing from result"

    # Check that all results are from Togo
    assert all(result_df['Region'] == 'TG'), "All results should be from Togo (TG)"

    print(f"Successfully retrieved {len(result_df)} power substations "
          f"from Togo via Overpass API")


if __name__ == '__main__':
    # Run specific tests for quick verification
    test_build_overpass_query()
    test_transform_overpass_to_internal_format()
    print("All basic tests passed!")
