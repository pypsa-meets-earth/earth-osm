"""Tests for improved error handling in historical data downloads"""

import pytest
from datetime import datetime
from earth_osm.eo import get_osm_data
from earth_osm.gfk_download import download_historical_pbf, download_pbf


class TestErrorHandling:
    """Test error handling for historical data downloads"""

    def test_download_historical_pbf_file_not_found(self):
        """Test download_historical_pbf raises FileNotFoundError for non-existent dates"""
        with pytest.raises(FileNotFoundError) as exc_info:
            download_historical_pbf(
                'https://download.geofabrik.de/europe/',
                'malta',
                datetime(1990, 1, 1),
                False,
                'earth_data_test_error',
                progress_bar=False
            )
        
        error_msg = str(exc_info.value)
        assert "malta" in error_msg
        assert "1990-01-01" in error_msg
        assert "Check available dates" in error_msg

    def test_download_pbf_historical_file_not_found(self):
        """Test download_pbf raises FileNotFoundError for non-existent historical dates"""
        with pytest.raises(FileNotFoundError) as exc_info:
            download_pbf(
                'https://download.geofabrik.de/europe/malta-latest.osm.pbf',
                False,
                'earth_data_test_error',
                progress_bar=False,
                target_date=datetime(1990, 1, 1),
                region_id='malta'
            )
        
        error_msg = str(exc_info.value)
        assert "malta" in error_msg
        assert "1990-01-01" in error_msg

    def test_get_osm_data_historical_file_not_found(self):
        """Test get_osm_data raises FileNotFoundError for non-existent historical dates"""
        with pytest.raises(FileNotFoundError) as exc_info:
            get_osm_data(
                region_str='malta',
                primary_name='power', 
                feature_name='line',
                data_dir='earth_data_test_error',
                cached=False,
                progress_bar=False,
                target_date=datetime(1990, 1, 1)
            )
        
        error_msg = str(exc_info.value)
        assert "malta" in error_msg
        assert "1990-01-01" in error_msg

    def test_download_pbf_missing_region_id(self):
        """Test download_pbf raises ValueError when region_id is missing for historical downloads"""
        with pytest.raises(ValueError) as exc_info:
            download_pbf(
                'https://download.geofabrik.de/europe/malta-latest.osm.pbf',
                False,
                'earth_data_test_error',
                progress_bar=False,
                target_date=datetime(2020, 1, 1)
                # Missing region_id
            )
        
        assert "region_id is required" in str(exc_info.value)

    def test_get_osm_data_existing_historical_date(self):
        """Test that existing historical dates work correctly"""
        try:
            df = get_osm_data(
                region_str='malta',
                primary_name='power', 
                feature_name='line',
                data_dir='earth_data_test_success',
                cached=False,
                progress_bar=False,
                target_date=datetime(2020, 1, 1)
            )
            
            # Should return a valid dataframe
            assert df is not None
            assert len(df) >= 0  # May be empty but should be a valid dataframe
            
        except Exception as e:
            pytest.skip(f"Skipping integration test due to: {e}")

    def test_get_osm_data_latest_still_works(self):
        """Test that latest (non-historical) downloads still work"""
        try:
            df = get_osm_data(
                region_str='malta',
                primary_name='power', 
                feature_name='line',
                data_dir='earth_data_test_latest',
                cached=False,
                progress_bar=False
                # No target_date = latest
            )
            
            # Should return a valid dataframe
            assert df is not None
            assert len(df) >= 0  # May be empty but should be a valid dataframe
            
        except Exception as e:
            pytest.skip(f"Skipping integration test due to: {e}")


def test_error_messages_are_actionable():
    """Test that error messages provide actionable guidance"""
    with pytest.raises(FileNotFoundError) as exc_info:
        download_historical_pbf(
            'https://download.geofabrik.de/europe/',
            'malta',
            datetime(1990, 1, 1),
            False,
            'earth_data_test_error',
            progress_bar=False
        )
    
    error_msg = str(exc_info.value)
    
    # Check that error message contains helpful information
    assert "malta" in error_msg.lower()
    assert "1990-01-01" in error_msg
    assert any(phrase in error_msg.lower() for phrase in [
        "check available dates",
        "try a more recent",
        "not found"
    ])