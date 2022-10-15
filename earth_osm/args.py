__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""CLI interface for earth_osm project.

This module provides a CLI interface for the earth_osm project.

"""

import argparse
import os

from earth_osm.gfk_data import get_all_valid_list, view_regions
from earth_osm.eo import get_osm_data
from earth_osm.config import primary_feature_element

def main():  # pragma: no cover
    """
    The main function executes on commands:
    `python -m earth_osm` and `$ earth_osm `. 
    It parses the command line and executes the appropriate function.
    """

    parser = argparse.ArgumentParser(
        description='Earth-OSM by PyPSA-meets-Earth',
        # epilog='''Example:''',
        add_help=False) # hide default help
    subparser = parser.add_subparsers(dest='command', required=True, title='Sub Parser', description='''View Supported Regions or Extract OSM Data''')

    extract_parser = subparser.add_parser('extract', help='Extract OSM Data')

    extract_parser.add_argument('primary', choices=primary_feature_element.keys(), type=str, help='Primary Feature')

