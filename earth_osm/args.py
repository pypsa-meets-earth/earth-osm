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

    extract_parser.add_argument('--regions',nargs="+", type=str, help='Region Identifier') # TODO: replace with region group
    extract_parser.add_argument('--features', nargs="*", type=str, help='Sub-Features')
    extract_parser.add_argument('--update', action='store_true', default=False, help='Update Data')
    extract_parser.add_argument('--mp',  action='store_true', default=True, help='Use Multiprocessing')
    extract_parser.add_argument('--data_dir', nargs="?", type=str, help='Earth Data Directory')

    
    view_parser = subparser.add_parser('view', help='View OSM Data')
    view_parser.add_argument('type', help='View Supported', choices=['regions', 'primary'])
    
    args = parser.parse_args()

    if args.command == 'view':
        print('Viewing OSM Data')
        view_regions(level=0)
    elif args.command == 'extract':
        if args.regions:
            region_list = list(args.regions)
            if not set(region_list) <= set(get_all_valid_list()):
                raise KeyError(f'Invalid Region {" ".join(set(region_list) - set(get_all_valid_list()))} , run earth_osm view regions to view valid regions')
        # elif args.coords:
        #     # TODO: change coords to shapely polygon, implement geom=True, get regions that way
        #     raise NotImplementedError('Bounding Box Region Identifier Not Implemented')
