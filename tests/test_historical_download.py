"""Tests for historical data download functionality"""

import os
import pytest
from unittest.mock import Mock
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

    @pytest.mark.integration
    def test_get_historical_files_from_directory(self):
        """Test fetching historical files from directory (integration test)"""
        # This is an integration test that requires internet connection
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

    @pytest.mark.integration
    def test_find_historical_file_by_date(self):
        """Test finding closest historical file for a target date"""
        # This is an integration test
        base_url = "https://download.geofabrik.de/africa/"

        # Test finding file for a date that should exist (2020-01-01)
        target_date = datetime(2020, 1, 1)
        filename = find_historical_file_by_date(base_url, "benin", target_date)

        assert filename.startswith("benin-")
        assert filename.endswith(".osm.pbf")

        # Verify it's a reasonable match
        file_date = parse_date_from_filename(filename)
        assert file_date is not None
        assert file_date <= target_date

    @pytest.mark.integration
    def test_download_historical_pbf(self):
        """Test downloading historical PBF file (integration test)"""
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

        assert os.path.exists(result)
        assert result.endswith(".osm.pbf")

        # Clean up
        if os.path.exists(result):
            os.remove(result)
        # Also clean up MD5 file if it exists
        md5_file = result + ".md5"
        if os.path.exists(md5_file):
            os.remove(md5_file)

    @pytest.mark.integration
    def test_get_osm_data_historical(self):
        """Test the main get_osm_data function with historical date"""
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


class TestHistoricalUrlConstruction:
    """Parametrized mocked tests for URL construction and filename parsing.

    Covers: continent-level (benin), nested (europe/germany/bayern),
    path-separator (us/california), with/without trailing slashes.
    """

    @pytest.fixture
    def mock_requests_get(self, monkeypatch):
        """Fixture to mock requests.get using monkeypatch"""
        def _mock_get(*args, **kwargs):
            mock_response = Mock()
            mock_response.text = ""
            mock_response.raise_for_status = Mock()
            return mock_response
        monkeypatch.setattr("earth_osm.gfk_download.requests.get", _mock_get)
        return _mock_get

    @pytest.mark.parametrize("region_base_url,region_id,expected_html_url,html_content,expected_filenames", [
        # Continent-level region: benin
        (
            "https://download.geofabrik.de/africa/",
            "benin",
            "https://download.geofabrik.de/africa/benin.html",
            '<a href="benin-250101.osm.pbf">benin-250101.osm.pbf</a>',
            ["benin-250101.osm.pbf"],
        ),
        # Continent-level region without trailing slash
        (
            "https://download.geofabrik.de/africa",
            "benin",
            "https://download.geofabrik.de/africa/benin.html",
            '<a href="benin-250101.osm.pbf">benin-250101.osm.pbf</a>',
            ["benin-250101.osm.pbf"],
        ),
        # Nested region: europe/germany/bayern
        (
            "https://download.geofabrik.de/europe/germany/",
            "europe/germany/bayern",
            "https://download.geofabrik.de/europe/germany/bayern.html",
            '<a href="bayern-250101.osm.pbf">bayern-250101.osm.pbf</a>',
            ["bayern-250101.osm.pbf"],
        ),
        # Nested region without trailing slash
        (
            "https://download.geofabrik.de/europe/germany",
            "europe/germany/bayern",
            "https://download.geofabrik.de/europe/germany/bayern.html",
            '<a href="bayern-250101.osm.pbf">bayern-250101.osm.pbf</a>',
            ["bayern-250101.osm.pbf"],
        ),
        # Path-separator region: us/california (key test case from mnm-matin)
        (
            "https://download.geofabrik.de/north-america/us/",
            "us/california",
            "https://download.geofabrik.de/north-america/us/california.html",
            '<a href="california-250101.osm.pbf">california-250101.osm.pbf</a>',
            ["california-250101.osm.pbf"],
        ),
        # Path-separator region without trailing slash
        (
            "https://download.geofabrik.de/north-america/us",
            "us/california",
            "https://download.geofabrik.de/north-america/us/california.html",
            '<a href="california-250101.osm.pbf">california-250101.osm.pbf</a>',
            ["california-250101.osm.pbf"],
        ),
        # Multiple files case
        (
            "https://download.geofabrik.de/africa/",
            "benin",
            "https://download.geofabrik.de/africa/benin.html",
            '<a href="benin-250101.osm.pbf">benin-250101.osm.pbf</a>\n'
            '<a href="benin-240901.osm.pbf">benin-240901.osm.pbf</a>\n'
            '<a href="benin-230801.osm.pbf">benin-230801.osm.pbf</a>',
            ["benin-250101.osm.pbf", "benin-240901.osm.pbf", "benin-230801.osm.pbf"],
        ),
    ], ids=[
        "benin-continent-slash",
        "benin-continent-no-slash",
        "bayern-nested-slash",
        "bayern-nested-no-slash",
        "us-california-slash",
        "us-california-no-slash",
        "benin-multiple-files",
    ])
    def test_url_construction_and_filename_parsing(
        self, monkeypatch, region_base_url, region_id, expected_html_url, html_content, expected_filenames
    ):
        """Test that HTML URL is constructed correctly and filenames are parsed."""
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status = Mock()
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("earth_osm.gfk_download.requests.get", mock_get)

        files = get_historical_files_from_directory(region_base_url, region_id)

        # Verify the correct URL was called
        mock_get.assert_called_once_with(expected_html_url, timeout=30)

        # Verify filenames are extracted
        actual_filenames = [f for f, _ in files]
        assert actual_filenames == expected_filenames

        # Verify dates are parsed correctly
        for filename, date in files:
            assert parse_date_from_filename(filename) is not None
            assert isinstance(date, datetime)


class TestFormatDateForFilenameBasename:
    """Test that format_date_for_filename uses os.path.basename for region_id."""

    @pytest.mark.parametrize("region_id,expected_prefix", [
        ("benin", "benin"),
        ("colombia", "colombia"),
        ("europe/germany/bayern", "bayern"),
        ("us/california", "california"),       # Key test: path separator → basename
        ("north-america/us/virginia", "virginia"),
    ])
    def test_format_date_uses_basename(self, region_id, expected_prefix):
        """format_date_for_filename should use os.path.basename(region_id)."""
        date = datetime(2025, 9, 1)
        result = format_date_for_filename(date, region_id)
        assert result == f"{expected_prefix}-250901"


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
