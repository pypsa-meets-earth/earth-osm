import timeit
import pytest
from earth_osm.gfk_data import get_region_tuple
from earth_osm.gfk_download import download_pbf, verify_pbf
import signal
import os


pytestmark = pytest.mark.integration

def test_download_pbf_update():
    region = get_region_tuple("malta")
    geofabrik_pbf_url = region.urls['pbf']

    data_dir = "earth_data_test"
    fp = os.path.join(data_dir, "pbf", "malta-latest.osm.pbf")
    fp_hash = os.path.join(data_dir, "pbf", "malta-latest.osm.pbf.md5")

    download_pbf(geofabrik_pbf_url, update=True, data_dir=data_dir)

    # check file last modified time
    lm1 = os.path.getmtime(fp)
    print(f"Last modified: {lm1}")

    assert os.path.exists(fp)
    assert verify_pbf(fp, fp_hash)

    download_pbf(geofabrik_pbf_url, update=False, data_dir=data_dir)
    lm2 = os.path.getmtime(fp)
    print(f"Last modified: {lm2}")

    assert lm2 == lm1

    download_pbf(geofabrik_pbf_url, update=True, data_dir=data_dir)
    lm3 = os.path.getmtime(fp)
    print(f"Last modified: {lm3}")

    assert lm3 > lm2


def test_download_pbf_no_progressbar():
    region = get_region_tuple("malta")
    geofabrik_pbf_url = region.urls['pbf']

    data_dir = "earth_data_test"
    fp = os.path.join(data_dir, "pbf", "malta-latest.osm.pbf")
    fp_hash = os.path.join(data_dir, "pbf", "malta-latest.osm.pbf.md5")

    download_pbf(geofabrik_pbf_url, update=True, data_dir=data_dir, progress_bar=False)

    # check file last modified time
    lm1 = os.path.getmtime(fp)
    print(f"Last modified: {lm1}")

    assert os.path.exists(fp)
    assert verify_pbf(fp, fp_hash)


def test_download_corrupted_file():
    data_dir = "earth_data_test"
    region = get_region_tuple("benin")
    geofabrik_pbf_url = region.urls['pbf']
    
    def cancel_download(signal, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGALRM, cancel_download)
    signal.alarm(2)

    try:
        download_pbf(geofabrik_pbf_url, update=True, data_dir=data_dir)
    except KeyboardInterrupt:
        print("Download cancelled.")

    
    # check file size of file in human readable format
    fp = os.path.join(data_dir, "pbf", "benin-latest.osm.pbf")
    corrupt_file_size = os.path.getsize(fp)
    print(f"Corrupt File size: {corrupt_file_size / (1024 * 1024)} MB")
    
    download_pbf(geofabrik_pbf_url, update=False, data_dir=data_dir)
    file_size = os.path.getsize(fp)
    print(f"New File size: {file_size / (1024 * 1024)} MB")

    assert file_size > corrupt_file_size


def test_md5_retry_logic():
    """Test that MD5 file is re-downloaded on retry when verification fails."""
    import tempfile
    
    data_dir = "earth_data_test"
    region = get_region_tuple("malta")
    geofabrik_pbf_url = region.urls['pbf']
    
    # First download to get valid files
    download_pbf(geofabrik_pbf_url, update=True, data_dir=data_dir)
    
    pbf_file = os.path.join(data_dir, "pbf", "malta-latest.osm.pbf")
    md5_file = os.path.join(data_dir, "pbf", "malta-latest.osm.pbf.md5")
    
    assert os.path.exists(pbf_file)
    assert os.path.exists(md5_file)
    
    # Corrupt the MD5 file to force a retry
    with open(md5_file, 'w') as f:
        f.write("corrupted_md5_hash  malta-latest.osm.pbf\n")
    
    # This should succeed by re-downloading both files
    result_fp = download_pbf(geofabrik_pbf_url, update=False, data_dir=data_dir)
    
    assert result_fp == pbf_file
    assert verify_pbf(pbf_file, md5_file)
    
    # Verify the MD5 file was actually re-downloaded
    with open(md5_file, 'r') as f:
        md5_content = f.read().strip()
    
    assert md5_content != "corrupted_md5_hash  malta-latest.osm.pbf"
    assert len(md5_content.split()[0]) == 32  # MD5 hash should be 32 chars


if __name__ == '__main__':
    test_download_pbf_update()
    test_download_corrupted_file()
    test_md5_retry_logic()
    