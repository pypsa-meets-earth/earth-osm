import gzip
import hashlib
import os
import time
from pathlib import Path

import pytest

from earth_osm.gfk_data import get_region_tuple
from earth_osm.gfk_download import download_file, download_pbf, verify_pbf
from earth_osm import gfk_download


pytestmark = pytest.mark.integration

SMALL_REGION_ID = "monaco"


def _prepare_region_pbf_url():
    region = get_region_tuple(SMALL_REGION_ID)
    return region.urls["pbf"]


def _download_dir(tmp_path: Path) -> str:
    data_dir = tmp_path / "earth_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir)


def test_download_small_region_pbf(tmp_path):
    pbf_url = _prepare_region_pbf_url()
    data_dir = _download_dir(tmp_path)

    pbf_path_str = download_pbf(pbf_url, update=True, data_dir=data_dir, progress_bar=False)
    pbf_path = Path(pbf_path_str)
    md5_path = Path(f"{pbf_path_str}.md5")

    assert pbf_path.exists()
    assert md5_path.exists()
    assert verify_pbf(str(pbf_path), str(md5_path))
    assert pbf_path.name == Path(pbf_url).name
    assert md5_path.name.endswith(".md5")

def test_download_pbf_update_cycle(tmp_path):
    pbf_url = _prepare_region_pbf_url()
    data_dir = _download_dir(tmp_path)

    pbf_path = Path(download_pbf(pbf_url, update=True, data_dir=data_dir, progress_bar=False))
    first_mtime = pbf_path.stat().st_mtime

    time.sleep(1)
    download_pbf(pbf_url, update=False, data_dir=data_dir, progress_bar=False)
    second_mtime = pbf_path.stat().st_mtime
    assert second_mtime == first_mtime

    time.sleep(1)
    download_pbf(pbf_url, update=True, data_dir=data_dir, progress_bar=False)
    third_mtime = pbf_path.stat().st_mtime
    assert third_mtime > second_mtime


def test_download_pbf_recovers_from_corruption(tmp_path):
    pbf_url = _prepare_region_pbf_url()
    data_dir = _download_dir(tmp_path)

    pbf_path = Path(download_pbf(pbf_url, update=True, data_dir=data_dir, progress_bar=False))
    original_size = pbf_path.stat().st_size

    # Corrupt the file locally and ensure a subsequent download repairs it
    pbf_path.write_bytes(b"0")
    assert pbf_path.stat().st_size < original_size

    download_pbf(pbf_url, update=False, data_dir=data_dir, progress_bar=False)
    repaired_size = pbf_path.stat().st_size
    assert repaired_size >= original_size

    md5_path = Path(f"{pbf_path}.md5")
    assert verify_pbf(str(pbf_path), str(md5_path))


def test_download_md5_metadata(tmp_path):
    pbf_url = _prepare_region_pbf_url()
    md5_url = f"{pbf_url}.md5"

    md5_dir = tmp_path / "md5"
    md5_dir.mkdir(parents=True, exist_ok=True)

    md5_path = Path(download_file(md5_url, str(md5_dir), progress_bar=False))

    assert md5_path.exists()
    contents = md5_path.read_text(encoding="ascii").strip()
    assert contents
    assert md5_path.name.endswith(".md5")
    assert Path(pbf_url).name in contents


def test_verify_pbf_handles_gzipped_md5(tmp_path):
    payload = b"sample pbf contents"
    pbf_path = tmp_path / "sample.osm.pbf"
    pbf_path.write_bytes(payload)

    checksum = hashlib.md5(payload).hexdigest()
    md5_path = tmp_path / "sample.osm.pbf.md5"
    with gzip.open(md5_path, "wb") as gz:
        gz.write(f"{checksum} sample.osm.pbf\n".encode("ascii"))

    assert verify_pbf(str(pbf_path), str(md5_path))


def test_download_pbf_refreshes_md5_when_pbf_downloaded(monkeypatch, tmp_path):
    url = "https://example.com/sample.osm.pbf"
    data_dir = tmp_path / "earth_data"
    data_dir.mkdir(parents=True, exist_ok=True)

    pbf_dir = data_dir / "pbf"
    pbf_dir.mkdir(parents=True, exist_ok=True)

    md5_path = pbf_dir / "sample.osm.pbf.md5"
    md5_path.write_text("old-checksum sample.osm.pbf\n", encoding="ascii")

    call_args = []

    def fake_download_file(
        call_url,
        directory,
        exists_ok=False,
        progress_bar=True,
        *,
        target_filename=None,
    ):
        filename = target_filename or os.path.basename(call_url)
        path = Path(directory) / filename
        call_args.append((call_url, exists_ok, target_filename))
        if not exists_ok or not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            if filename.endswith(".md5"):
                path.write_text("new-checksum sample-20240101.osm.pbf\n", encoding="ascii")
            else:
                path.write_bytes(b"data")
        return str(path)

    monkeypatch.setattr(gfk_download, "download_file", fake_download_file)
    monkeypatch.setattr(gfk_download, "verify_pbf", lambda *_: True)

    result = download_pbf(url, update=False, data_dir=str(data_dir), progress_bar=False)

    assert result == str(pbf_dir / "sample.osm.pbf")
    assert call_args[0] == (f"{url}.md5", False, None)
    assert call_args[1] == ("https://example.com/sample-20240101.osm.pbf", False, "sample.osm.pbf")
    assert "sample-20240101.osm.pbf" in md5_path.read_text(encoding="ascii")
