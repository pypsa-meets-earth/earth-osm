__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Geofabrik Data Download

This module contains functions to download Geofabrik data.

"""


import hashlib
import logging
import os
import shutil

import requests
import urllib3
from tqdm.auto import tqdm

from earth_osm import logger as base_logger

logger = logging.getLogger("eo.gfk")
logger.setLevel(logging.INFO)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_file(url, dir, exists_ok=False, progress_bar=True):
    """
    Download file from url to dir

    Args:
        url (str): url to download
        dir (str): directory to download to
        exists_ok (bool): Flag to allow skipping download if file exists.

    Returns:
        str: filepath of downloaded file
    """
    filename = os.path.basename(url)
    filepath = os.path.join(dir, filename)
    if os.path.exists(filepath) and exists_ok:
        logger.debug(f'{filepath} already exists')
        return filepath
    logger.info(f"{filename} downloading to {filepath}")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)  #  create download dir
    with requests.get(url, stream=progress_bar, verify=False) as r:
        if r.status_code == 200:
            # url properly found, thus execute as expected
            if progress_bar:
                file_size = int(r.headers.get('Content-Length', 0))
                desc = "(Unknown total file size)" if file_size == 0 else ""
                with tqdm.wrapattr(r.raw, "read", total=file_size, desc=desc, leave=False) as raw:
                    with open(filepath, "wb") as f:
                        shutil.copyfileobj(raw, f)
            else:
                with open(filepath, "wb") as f:
                    f.write(r.content)
        else:
            # error status code: file not found
            logger.error(
                f"Error code: {r.status_code}. File {filename} not downloaded from {url}"
            )
            filepath = None
    return filepath

def download_sitemap(geom, pkg_data_dir, progress_bar=True):
    geofabrik_geo = "https://download.geofabrik.de/index-v1.json"
    geofabrik_nogeo = "https://download.geofabrik.de/index-v1-nogeom.json"
    geofabrik_sitemap_url = geofabrik_geo if geom else geofabrik_nogeo

    sitemap_file = download_file(geofabrik_sitemap_url, pkg_data_dir, exists_ok=True, progress_bar=progress_bar)

    return sitemap_file


def download_pbf(url, update, data_dir, progress_bar=True):

    pbf_dir = os.path.join(data_dir, "pbf")
    pbf_fn = os.path.basename(url)
    pbf_fp = os.path.join(pbf_dir, pbf_fn)

    # download file
    down_pbf_fp = download_file(url, pbf_dir, exists_ok=not update, progress_bar=progress_bar)
    down_md5_fp = download_file(url + ".md5", pbf_dir, exists_ok=not update, progress_bar=progress_bar)
    
    assert down_pbf_fp == pbf_fp

    if not verify_pbf(down_pbf_fp, down_md5_fp):
        logger.info(f"PBF Md5 mismatch, retrying download for {pbf_fn}")
        down_pbf_fp = download_file(url, pbf_dir, progress_bar=progress_bar)
        down_md5_fp = download_file(url + ".md5", pbf_dir, exists_ok=not update, progress_bar=progress_bar)
        if not verify_pbf(down_pbf_fp, down_md5_fp):
            os.remove(down_pbf_fp)
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

    # Read remote MD5
    with open(pbf_md5file, 'r') as f:
        remote_md5 = f.read().split()[0]

    return local_md5 == remote_md5
