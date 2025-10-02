import gzip
import hashlib
import io
import timeit
import pytest
from earth_osm.gfk_data import get_region_tuple
from earth_osm.gfk_download import download_file, download_pbf, verify_pbf
import signal
import os


pytestmark = pytest.mark.integration


def test_download_file_enables_decode_content(tmp_path, monkeypatch):
    data = b"1234567890abcdef"
    responses = []

    class DummyRaw(io.BytesIO):
        def __init__(self, payload):
            super().__init__(payload)
            self.decode_content = False

    class DummyResponse:
        def __init__(self, payload):
            self.status_code = 200
            self.headers = {"Content-Length": str(len(payload))}
            self.raw = DummyRaw(payload)
            self._content = payload

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def close(self):
            self.raw.close()

        @property
        def content(self):
            return self._content

    def fake_get(url, stream=None, verify=None):
        resp = DummyResponse(data)
        responses.append(resp)
        return resp

    monkeypatch.setattr("earth_osm.gfk_download.requests.get", fake_get)

    download_dir = tmp_path / "downloads"
    result = download_file("https://example.com/test.md5", str(download_dir), progress_bar=True)

    assert responses, "Expected mocked response to be captured"
    assert responses[0].raw.decode_content is True
    assert os.path.exists(result)
    with open(result, "rb") as downloaded:
        assert downloaded.read() == data


def test_verify_pbf_handles_gzipped_md5(tmp_path):
    payload = b"sample pbf contents"
    pbf_path = tmp_path / "sample.osm.pbf"
    pbf_path.write_bytes(payload)

    checksum = hashlib.md5(payload).hexdigest()
    md5_path = tmp_path / "sample.osm.pbf.md5"
    with gzip.open(md5_path, "wb") as gz:
        gz.write(f"{checksum} sample.osm.pbf\n".encode("ascii"))

    assert verify_pbf(str(pbf_path), str(md5_path))


def test_verify_pbf_handles_real_cd_md5(tmp_path, monkeypatch):
    region = get_region_tuple("congo-democratic-republic")
    md5_url = region.urls["pbf"] + ".md5"

    md5_path = download_file(md5_url, str(tmp_path), progress_bar=False)
    assert md5_path is not None

    with open(md5_path, "rb") as fh:
        payload = fh.read()
    if payload.startswith(b"\x1f\x8b"):
        remote_md5 = gzip.decompress(payload).decode("ascii").split()[0]
    else:
        remote_md5 = payload.decode("ascii").split()[0]

    fake_pbf = tmp_path / "fake.osm.pbf"
    fake_pbf.write_bytes(b"earth-osm-test")

    monkeypatch.setattr(
        "earth_osm.gfk_download.calculate_md5",
        lambda _: remote_md5,
    )

    assert verify_pbf(str(fake_pbf), md5_path)

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
    