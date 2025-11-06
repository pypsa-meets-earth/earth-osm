__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Geofabrik Data Download

This module contains functions to download Geofabrik data.

"""


import gzip
import hashlib
import logging
import os
import re
import shutil
import subprocess
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import urljoin

import requests
import urllib3
from tqdm.auto import tqdm

logger = logging.getLogger("eo.gfk")
logger.setLevel(logging.INFO)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PARALLEL_DOWNLOADS_ENV = "EO_PARALLEL_DOWNLOADS"
ARIA2C_EXECUTABLE = "aria2c"


def _resolve_parallel_downloads():
    raw = os.environ.get(PARALLEL_DOWNLOADS_ENV)
    if raw is None:
        return 1

    try:
        value = int(raw)
    except ValueError:
        return 1

    return value if value > 1 else 1


def _download_with_aria2c(
    aria2c_path,
    url,
    output_dir,
    output_filename,
    connections,
    progress_bar,
):
    os.makedirs(output_dir, exist_ok=True)

    command = [
        aria2c_path,
        "--continue=true",
        "--allow-overwrite=true",
        "--auto-file-renaming=false",
        f"--max-connection-per-server={connections}",
        f"--split={connections}",
        "--min-split-size=1M",
        "--max-tries=5",
        "--console-log-level=warn",
        f"--dir={output_dir}",
        f"--out={output_filename}",
    ]

    if not progress_bar:
        command.append("--summary-interval=0")

    command.append(url)

    subprocess.run(command, check=True)

    expected_path = os.path.join(output_dir, output_filename)
    if not os.path.exists(expected_path):
        raise RuntimeError(
            f"aria2c reported success but {expected_path!r} was not created"
        )
 

def download_file(url, dir, exists_ok=False, progress_bar=True, *, target_filename=None):
    """
    Download file from url to dir

    Args:
        url (str): url to download
        dir (str): directory to download to
        exists_ok (bool): Flag to allow skipping download if file exists.
        target_filename (str, optional): Explicit filename for the local copy.

    Returns:
        str: filepath of downloaded file
    """
    filename = target_filename or os.path.basename(url)
    filepath = os.path.join(dir, filename)
    if os.path.exists(filepath) and exists_ok:
        logger.debug(f'{filepath} already exists')
        return filepath

    parallel_downloads = _resolve_parallel_downloads()
    if parallel_downloads > 1 and url.endswith(".osm.pbf"):
        aria2c_path = shutil.which(ARIA2C_EXECUTABLE)
        if aria2c_path:
            try:
                _download_with_aria2c(
                    aria2c_path,
                    url,
                    dir,
                    filename,
                    parallel_downloads,
                    progress_bar,
                )
                return filepath
            except (subprocess.CalledProcessError, RuntimeError):
                logger.info("aria2c failed for %s, falling back to single connection download", filename)

    logger.info(f"{filename} downloading to {filepath}")
    os.makedirs(os.path.dirname(filepath),
                exist_ok=True)  # create download dir
    with requests.get(url, stream=True, verify=False) as r:
        if r.status_code == 200:
            # url properly found, thus execute as expected
            r.raw.decode_content = True
            if progress_bar:
                file_size = int(r.headers.get('Content-Length', 0))
                desc = "(Unknown total file size)" if file_size == 0 else ""
                with tqdm.wrapattr(r.raw, "read", total=file_size, desc=desc, leave=False) as raw:
                    with open(filepath, "wb") as f:
                        shutil.copyfileobj(raw, f)
            else:
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 20):  # 1 MiB chunks
                        if chunk:
                            f.write(chunk)
        else:
            # error status code: file not found
            logger.error(
                f"Error code: {r.status_code}. File {filename} not downloaded "
                f"from {url}"
            )
            filepath = None
    return filepath


def download_sitemap(geom, pkg_data_dir, progress_bar=True):
    geofabrik_geo = "https://download.geofabrik.de/index-v1.json"
    geofabrik_nogeo = "https://download.geofabrik.de/index-v1-nogeom.json"
    geofabrik_sitemap_url = geofabrik_geo if geom else geofabrik_nogeo
    sitemap_file = download_file(geofabrik_sitemap_url, pkg_data_dir, exists_ok=True, progress_bar=progress_bar)

    return sitemap_file


def _parse_md5_file(md5_path: str):
    with open(md5_path, "rb") as f:
        payload = f.read()

    if payload.startswith(b"\x1f\x8b"):
        payload = gzip.decompress(payload)

    text = payload.decode("ascii").strip()
    if not text:
        raise ValueError(f"MD5 file {md5_path} is empty")

    parts = text.split()
    checksum = parts[0].lower()
    remote_name = None

    for candidate in parts[1:]:
        cleaned = candidate.lstrip("*")
        if cleaned.endswith(".osm.pbf"):
            remote_name = cleaned
            break

    return checksum, remote_name


def _build_versioned_url(base_url: str, remote_filename: Optional[str]) -> str:
    if not remote_filename:
        return base_url
    return urljoin(base_url, remote_filename)
def download_pbf(
    url,
    update,
    data_dir,
    progress_bar=True,
    *,
    target_date: Optional[datetime] = None,
    region_id: Optional[str] = None,
):
    """
    Download a PBF archive supporting latest and historical endpoints.

    Args:
        url: URL to download (for latest) or base URL (for historical).
        update: Whether to force re-download if the file exists.
        data_dir: Directory to download to.
        progress_bar: Whether to show the progress bar.
        target_date: Optional target date to fetch a historical snapshot.
        region_id: Region identifier, required for historical downloads.

    Returns:
        Path to the downloaded file.

    Raises:
        FileNotFoundError: When the requested historical file cannot be located.
        ValueError: When ``region_id`` is omitted for historical downloads.
    """
    # If target_date is specified, download historical file
    if target_date is not None:
        if region_id is None:
            raise ValueError("region_id is required for historical downloads")

        # Extract base URL from the provided URL
        if url.endswith("-latest.osm.pbf"):
            region_base_url = "/".join(url.split("/")[:-1]) + "/"
        else:
            region_base_url = url

        return download_historical_pbf(
            region_base_url, region_id, target_date, update, data_dir, progress_bar
        )

    # Original logic for latest files
    pbf_dir = os.path.join(data_dir, "pbf")
    pbf_fn = os.path.basename(url)
    pbf_fp = os.path.join(pbf_dir, pbf_fn)
    md5_fp = pbf_fp + ".md5"

    # Track existing files before download attempts
    pbf_existed = os.path.exists(pbf_fp)
    md5_existed = os.path.exists(md5_fp)

    def _download_md5(force: bool) -> str:
        exists_ok = (not force) and os.path.exists(md5_fp)
        return download_file(
            url + ".md5",
            pbf_dir,
            exists_ok=exists_ok,
            progress_bar=progress_bar,
        )

    def _download_versioned_pbf(force_md5: bool = True) -> tuple[str, str]:
        md5_path = _download_md5(force=force_md5)
        _, remote_name = _parse_md5_file(md5_path)
        source_url = _build_versioned_url(url, remote_name)

        if os.path.exists(pbf_fp):
            os.remove(pbf_fp)

        downloaded_path = download_file(
            source_url,
            pbf_dir,
            exists_ok=False,
            progress_bar=progress_bar,
            target_filename=pbf_fn,
        )
        return downloaded_path, md5_path

    if update or not pbf_existed:
        down_pbf_fp, down_md5_fp = _download_versioned_pbf(force_md5=True)
    else:
        down_pbf_fp = download_file(url, pbf_dir, exists_ok=True, progress_bar=progress_bar)
        down_md5_fp = md5_fp if md5_existed else _download_md5(force=True)

    assert down_pbf_fp == pbf_fp

    if not verify_pbf(down_pbf_fp, down_md5_fp):
        logger.info(f"PBF Md5 mismatch, retrying download for {pbf_fn}")
        down_pbf_fp, down_md5_fp = _download_versioned_pbf(force_md5=True)
        if not verify_pbf(down_pbf_fp, down_md5_fp):
            if os.path.exists(down_pbf_fp):
                os.remove(down_pbf_fp)
            if os.path.exists(down_md5_fp):
                os.remove(down_md5_fp)
            raise ValueError(f"File verification failed after retry for {pbf_fn}")

    return pbf_fp


def calculate_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def verify_pbf(pbf_inputfile, pbf_md5file):
    # Calculate local MD5
    local_md5 = calculate_md5(pbf_inputfile)

    remote_md5, _ = _parse_md5_file(pbf_md5file)

    return local_md5 == remote_md5


def parse_date_from_filename(filename: str) -> Optional[datetime]:
    """
    Parse date from historical filename format like 'benin-250901.osm.pbf'

    Args:
        filename (str): Filename in format {region}-{YYMMDD}.osm.pbf

    Returns:
        datetime or None: Parsed date or None if format doesn't match
    """
    # Match pattern like 'benin-250901.osm.pbf'
    pattern = r"^([a-zA-Z0-9\-]+)-(\d{6})\.osm\.pbf$"
    match = re.match(pattern, filename)

    if not match:
        return None

    date_str = match.group(2)  # Extract YYMMDD part

    try:
        # Convert YYMMDD to full date
        year = int("20" + date_str[:2])  # Assume 20XX for YY
        month = int(date_str[2:4])
        day = int(date_str[4:6])

        return datetime(year, month, day)
    except ValueError:
        return None


def format_date_for_filename(date: datetime, region_id: str) -> str:
    """
    Format a date to the historical filename format

    Args:
        date (datetime): Date to format
        region_id (str): Region identifier (e.g., 'benin')

    Returns:
        str: Filename without extension (e.g., 'benin-250901')
    """
    year_short = str(date.year)[2:]  # Get last 2 digits of year
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"

    return f"{region_id}-{year_short}{month}{day}"


def get_historical_files_from_directory(
    region_base_url: str, region_id: str
) -> List[Tuple[str, datetime]]:
    """
    Fetch and parse historical files from Geofabrik directory listing

    Args:
        region_base_url (str): Base URL for the region directory (e.g., 'https://download.geofabrik.de/africa/')
        region_id (str): Region identifier (e.g., 'benin')

    Returns:
        List[Tuple[str, datetime]]: List of (filename, date) tuples for historical files
    """
    try:
        response = requests.get(region_base_url, timeout=30)
        response.raise_for_status()

        html_content = response.text

        # Find all .osm.pbf files for this region that match historical pattern
        pattern = rf'href="({region_id}-\d{{6}}\.osm\.pbf)"'
        matches = re.findall(pattern, html_content)

        historical_files = []
        for filename in matches:
            date = parse_date_from_filename(filename)
            if date:
                historical_files.append((filename, date))

        # Sort by date (newest first)
        historical_files.sort(key=lambda x: x[1], reverse=True)

        return historical_files

    except requests.RequestException as e:
        logger.error(
            f"Failed to fetch directory listing from {region_base_url}: {e}")
        return []


def find_historical_file_by_date(
    region_base_url: str, region_id: str, target_date: datetime
) -> Optional[str]:
    """
    Find the closest historical file for a given date

    Args:
        region_base_url (str): Base URL for the region directory
        region_id (str): Region identifier
        target_date (datetime): Target date to find closest file for

    Returns:
        str or None: Filename of the closest historical file, or None if not found
    """
    historical_files = get_historical_files_from_directory(
        region_base_url, region_id)

    if not historical_files:
        logger.warning(f"No historical files found for region {region_id}")
        return None

    # Find the file with date closest to but not after the target date
    best_file = None
    best_date = None

    for filename, file_date in historical_files:
        if file_date <= target_date:
            if best_date is None or file_date > best_date:
                best_file = filename
                best_date = file_date

    if best_file:
        logger.info(
            f"Found historical file {best_file} for date "
            f"{target_date.strftime('%Y-%m-%d')} (file date: "
            f"{best_date.strftime('%Y-%m-%d')})"
        )
        return best_file
    else:
        logger.warning(
            f"No historical file found for date {target_date.strftime('%Y-%m-%d')} "
            f"for region {region_id}"
        )
        return None


def download_historical_pbf(
    region_base_url: str,
    region_id: str,
    target_date: datetime,
    update: bool,
    data_dir: str,
    progress_bar: bool = True,
) -> str:
    """
    Download historical PBF file for a specific date

    Args:
        region_base_url (str): Base URL for the region directory
        region_id (str): Region identifier
        target_date (datetime): Target date for historical data
        update (bool): Whether to force re-download if file exists
        data_dir (str): Directory to download to
        progress_bar (bool): Whether to show progress bar

    Returns:
        str: Path to downloaded file

    Raises:
        FileNotFoundError: When no historical PBF file is available for the target date
    """
    historical_filename = find_historical_file_by_date(
        region_base_url, region_id, target_date)

    if not historical_filename:
        raise FileNotFoundError(
            f"No historical PBF file found for {region_id} on/before {target_date.strftime('%Y-%m-%d')} "
            f"at {region_base_url}. Check available dates or try a more recent target date."
        )

    # Construct full URL
    historical_url = region_base_url.rstrip("/") + "/" + historical_filename

    pbf_dir = os.path.join(data_dir, "pbf")
    pbf_fp = os.path.join(pbf_dir, historical_filename)

    # Download file
    down_pbf_fp = download_file(
        historical_url, pbf_dir, exists_ok=not update, progress_bar=progress_bar
    )

    if down_pbf_fp is None:
        raise FileNotFoundError(
            f"Failed to download historical PBF file {historical_filename} from {historical_url}. "
            f"The file may have been moved or is temporarily unavailable."
        )

    # Try to download MD5 file (may not exist for all historical files)
    md5_url = historical_url + ".md5"
    down_md5_fp = download_file(
        md5_url, pbf_dir, exists_ok=not update, progress_bar=progress_bar
    )

    # Verify if MD5 file exists
    if down_md5_fp and os.path.exists(down_md5_fp):
        if not verify_pbf(down_pbf_fp, down_md5_fp):
            logger.warning(
                f"MD5 verification failed for {historical_filename}, but keeping file "
                f"as historical data may not always have MD5"
            )
    else:
        logger.info(
            f"No MD5 file available for historical file {historical_filename}"
        )

    return pbf_fp
