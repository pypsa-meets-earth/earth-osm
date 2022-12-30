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

logger = logging.getLogger("osm_geo")
logger.setLevel(logging.INFO)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def earth_downloader(url, dir):
    """
    Download file from url to dir

    Args:
        url (str): url to download
        dir (str): directory to download to

    Returns:
        str: filepath of downloaded file
    """
    filename = os.path.basename(url)
    filepath = os.path.join(dir, filename)
    logger.info(f"{filename} downloading to {filepath}")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)  #  create download dir
    with requests.get(url, stream=True, verify=False) as r:
        if r.status_code == 200:
            # url properly found, thus execute as expected
            file_size = int(r.headers.get("Content-Length", 0))
            desc = "(Unknown total file size)" if file_size == 0 else ""
            with tqdm.wrapattr(r.raw, "read", total=file_size, desc=desc, leave=False) as raw:
                with open(filepath, "wb") as f:
                    shutil.copyfileobj(raw, f)
        else:
            # error status code: file not found
            logger.error(
                f"Error code: {r.status_code}. File {filename} not downloaded from {url}"
            )
            filepath = None
    return filepath


def download_pbf(url, update, data_dir):

    dir = os.path.join(data_dir, "pbf")
    pbf_filename = os.path.basename(url)
    pbf_filepath = os.path.join(dir, pbf_filename)

    # TODO: multi-part download each file for parallel downloading... (pip install pySmartDL)
    if not os.path.exists(pbf_filepath):
        # download file
        d_filepath = earth_downloader(url, dir)
        assert d_filepath == pbf_filepath
    else:
        logger.debug(f"{pbf_filename} already exists in {pbf_filepath}")

    return pbf_filepath


# TODO: fix update param
def download_sitemap(geom, pkg_data_dir):
    geofabrik_geo = "https://download.geofabrik.de/index-v1.json"
    geofabrik_nogeo = "https://download.geofabrik.de/index-v1-nogeom.json"
    geofabrik_sitemap_url = geofabrik_geo if geom else geofabrik_nogeo
    logger.info("Downloading Sitemap")
    sitemap_file = earth_downloader(geofabrik_sitemap_url, pkg_data_dir)

    return sitemap_file


# def download_pbf(country_code, update, verify):
# if verify is True:
#     if verify_pbf(PBF_inputfile, geofabrik_url, update) is False:
#         logger.warning(f"md5 mismatch, deleting {geofabrik_filename}")
#         if os.path.exists(PBF_inputfile):
#             os.remove(PBF_inputfile)

#         download_pbf(country_code, update=False, verify=False)  # Only try downloading once

# return PBF_inputfile


# verified_pbf = []


# def verify_pbf(PBF_inputfile, geofabrik_url, update):
#     if PBF_inputfile in verified_pbf:
#         return True

#     geofabrik_md5_url = geofabrik_url + ".md5"
#     PBF_md5file = PBF_inputfile + ".md5"

#     def calculate_md5(fname):
#         hash_md5 = hashlib.md5()
#         with open(fname, "rb") as f:
#             for chunk in iter(lambda: f.read(4096), b""):
#                 hash_md5.update(chunk)
#         return hash_md5.hexdigest()

#     if update is True or not os.path.exists(PBF_md5file):
#         with requests.get(geofabrik_md5_url, stream=True, verify=False) as r:
#             with open(PBF_md5file, "wb") as f:
#                 shutil.copyfileobj(r.raw, f)

#     local_md5 = calculate_md5(PBF_inputfile)

#     with open(PBF_md5file) as f:
#         contents = f.read()
#         remote_md5 = contents.split()[0]

#     if local_md5 == remote_md5:
#         verified_pbf.append(PBF_inputfile)
#         return True
#     else:
#         return False
