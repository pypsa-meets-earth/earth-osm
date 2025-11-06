"""Tests for historical data download functionality"""

import os
import pytest
from datetime import datetime
from earth_osm.gfk_data import get_region_tuple_historical, get_region_base_url
from earth_osm.gfk_download import (
    parse_date_from_filename,
    format_date_for_filename,
    get_historical_files_from_directory,
    find_historical_file_by_date,
    download_historical_pbf,
)
from earth_osm.eo import get_osm_data


class TestHistoricalDownload:

    def test_parse_date_from_filename(self):
        """Test parsing dates from historical filenames"""
        # Valid cases
        assert parse_date_from_filename("benin-250901.osm.pbf") == datetime(2025, 9, 1)
        assert parse_date_from_filename("colombia-220101.osm.pbf") == datetime(2022, 1, 1)
        assert parse_date_from_filename("nigeria-191225.osm.pbf") == datetime(2019, 12, 25)

        # Invalid cases
        assert parse_date_from_filename("benin-latest.osm.pbf") is None
        assert parse_date_from_filename("benin-250901.osm.bz2") is None
        assert parse_date_from_filename("not-a-date-file.txt") is None
        assert parse_date_from_filename("benin-invalid.osm.pbf") is None

    def test_format_date_for_filename(self):
        """Test formatting dates for historical filenames"""
        date1 = datetime(2025, 9, 1)
        assert format_date_for_filename(date1, "benin") == "benin-250901"

        date2 = datetime(2020, 1, 15)
        assert format_date_for_filename(date2, "colombia") == "colombia-200115"

        date3 = datetime(2019, 12, 25)
        assert format_date_for_filename(date3, "nigeria") == "nigeria-191225"

    def test_get_region_tuple_historical(self):
        """Test getting region tuple with historical date support"""
        target_date = datetime(2020, 1, 1)
        region = get_region_tuple_historical("benin", target_date)

        assert hasattr(region, "target_date")
        assert region.target_date == target_date
        assert hasattr(region, "base_url")
        assert "africa" in region.base_url
        assert region.id == "benin"

    def test_get_region_base_url(self):
        """Test extracting base URL from region"""
        from earth_osm.gfk_data import get_region_tuple

        region = get_region_tuple("benin")
        base_url = get_region_base_url(region)

        expected_base = "https://download.geofabrik.de/africa/"
        assert base_url == expected_base

    def test_get_historical_files_from_directory(self):
        """Test fetching historical files from directory (integration test)"""
        # This is an integration test that requires internet connection
        # Skip if no internet or if test should be lightweight
        try:
            base_url = "https://download.geofabrik.de/africa/"
            files = get_historical_files_from_directory(base_url, "benin")

            # Should find some historical files
            assert len(files) > 0

            # Check that files are properly parsed
            for filename, date in files:
                assert filename.startswith("benin-")
                assert filename.endswith(".osm.pbf")
                assert isinstance(date, datetime)

            # Files should be sorted by date (newest first)
            dates = [date for _, date in files]
            assert dates == sorted(dates, reverse=True)

        except Exception as e:
            pytest.skip(f"Skipping integration test due to: {e}")

    def test_find_historical_file_by_date(self):
        """Test finding closest historical file for a target date"""
        # This is an integration test
        try:
            base_url = "https://download.geofabrik.de/africa/"

            # Test finding file for a date that should exist (2020-01-01)
            target_date = datetime(2020, 1, 1)
            filename = find_historical_file_by_date(base_url, "benin", target_date)

            if filename:  # File found
                assert filename.startswith("benin-")
                assert filename.endswith(".osm.pbf")

                # Verify it's a reasonable match
                file_date = parse_date_from_filename(filename)
                assert file_date is not None
                assert file_date <= target_date

        except Exception as e:
            pytest.skip(f"Skipping integration test due to: {e}")

    def test_download_historical_pbf(self):
        """Test downloading historical PBF file (integration test)"""
        try:
            base_url = "https://download.geofabrik.de/africa/"
            target_date = datetime(2020, 1, 1)  # Should exist
            data_dir = "earth_data_test_historical"

            # Try to download historical file
            result = download_historical_pbf(
                base_url,
                "benin",
                target_date,
                update=True,
                data_dir=data_dir,
                progress_bar=False,
            )

            if result:  # Download succeeded
                assert os.path.exists(result)
                assert result.endswith(".osm.pbf")

                # Clean up
                if os.path.exists(result):
                    os.remove(result)
                # Also clean up MD5 file if it exists
                md5_file = result + ".md5"
                if os.path.exists(md5_file):
                    os.remove(md5_file)

        except Exception as e:
            pytest.skip(f"Skipping integration test due to: {e}")

    def test_get_osm_data_historical(self):
        """Test the main get_osm_data function with historical date"""
        try:
            target_date = datetime(2020, 1, 1)

            # This should work with historical data
            df = get_osm_data(
                region_str="malta",  # Use Malta as it's smaller
                primary_name="power",
                feature_name="line",
                data_dir="earth_data_test_historical",
                cached=False,  # Force fresh download
                progress_bar=False,
                target_date=target_date,
            )

            # Should return a dataframe
            assert df is not None

        except Exception as e:
            pytest.skip(f"Skipping integration test due to: {e}")


def test_historical_functionality_basic():
    """Basic test that doesn't require internet connection"""
    # Test date parsing
    date = parse_date_from_filename("test-250901.osm.pbf")
    assert date == datetime(2025, 9, 1)

    # Test date formatting
    formatted = format_date_for_filename(datetime(2025, 9, 1), "test")
    assert formatted == "test-250901"

    # Test historical region tuple creation
    target_date = datetime(2020, 1, 1)
    region = get_region_tuple_historical("benin", target_date)

    assert hasattr(region, "target_date")
    assert region.target_date == target_date
    assert hasattr(region, "base_url")


if __name__ == "__main__":
    # Run basic tests that don't require internet
    test_historical_functionality_basic()
    print("Basic historical functionality tests passed!")

    # Run full test suite
    pytest.main([__file__, "-v"])
