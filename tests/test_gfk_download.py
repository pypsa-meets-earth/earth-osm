import timeit
from earth_osm.gfk_data import get_region_tuple
from earth_osm.gfk_download import download_pbf, verify_pbf
import signal
import os

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


if __name__ == '__main__':
    test_download_pbf_update()
    test_download_corrupted_file()
    