__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022-2024, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""CLI interface for earth_osm project.

This module provides a CLI interface for the earth_osm project.

"""

import argparse
import os
from typing import List, Set

from earth_osm.tagdata import get_feature_list, get_primary_list
from earth_osm.eo import save_osm_data
from earth_osm.gfk_data import get_all_valid_list, view_regions



BANNER = """
╔═══════════════════════════════════════╗
║             Earth-OSM                 ║
║  "Empowering Open Infrastructure      ║
║      Data for the People"             ║
║                - @mnm-matin           ║
╚═══════════════════════════════════════╝
"""

class CustomHelpFormatter(argparse.HelpFormatter):
    def _format_action(self, action):
        parts = super()._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts

def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Earth-OSM by PyPSA-meets-Earth',
        formatter_class=CustomHelpFormatter,
        add_help=False
    )
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    # parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='command', required=True, title='Commands')

    setup_extract_parser(subparsers)
    setup_view_parser(subparsers)

    return parser

def setup_extract_parser(subparsers):
    extract_parser = subparsers.add_parser('extract', help='Extract OSM Data')
    extract_parser.add_argument('primary', choices=get_primary_list(), type=str, help='Primary Feature')
    extract_parser.add_argument('--regions', nargs="+", type=str, required=True, help='Region Identifier(s)')
    extract_parser.add_argument('--features', nargs="*", type=str, help='Sub-Features')
    extract_parser.add_argument('--update', action='store_true', help='Update Data')
    extract_parser.add_argument('--no_mp', action='store_true', help='Disable Multiprocessing')
    extract_parser.add_argument('--data_dir', type=str, help='Earth Data Directory')
    extract_parser.add_argument('--out_dir', type=str, help='Earth Output Directory')
    extract_parser.add_argument('--out_format', nargs="*", type=str, choices=['csv', 'geojson'], default=['csv', 'geojson'], help='Export options')
    
    agg_group = extract_parser.add_mutually_exclusive_group()
    agg_group.add_argument('--agg_feature', action='store_true', help='Aggregate Outputs by feature')
    agg_group.add_argument('--agg_region', action='store_true', help='Aggregate Outputs by region')

def setup_view_parser(subparsers):
    view_parser = subparsers.add_parser('view', help='View OSM Data')
    view_parser.add_argument('type', choices=['regions', 'primary'], help='View Supported')

def validate_regions(regions: List[str]):
    invalid_regions = set(regions) - set(get_all_valid_list())
    if invalid_regions:
        raise ValueError(f'Invalid Region(s): {", ".join(invalid_regions)}. Run "earth_osm view regions" to view valid regions.')

def validate_features(primary: str, features: List[str]):
    if features:
        if 'ALL' in features:
            return list(get_feature_list(primary))
        invalid_features = set(features) - set(get_feature_list(primary))
        if invalid_features:
            raise ValueError(f'Invalid Feature(s): {", ".join(invalid_features)}. Run "earth_osm view features" to view valid features.')
        return features
    return list(get_feature_list(primary))

def ensure_directory(directory: str) -> str:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    if not os.path.isdir(directory):
        raise NotADirectoryError(f'Invalid directory: {directory}')
    return directory

def handle_extract(args):
    validate_regions(args.regions)
    feature_list = validate_features(args.primary, args.features)

    data_dir = ensure_directory(args.data_dir or os.path.join(os.getcwd(), 'earth_data'))
    out_dir = ensure_directory(args.out_dir or data_dir)

    out_aggregate = 'feature' if args.agg_feature else 'region' if args.agg_region else False

    print('\n'.join([
        f'Primary Feature: {args.primary}',
        f'Sub Features: {" - ".join(feature_list)}',
        f'Regions: {" - ".join(args.regions)}',
        f'Multiprocessing = {not args.no_mp}',
        f'Update Data = {args.update}',
        f'Data Directory = {data_dir}',
        f'Output Directory = {out_dir}',
        f'Output Format = {" - ".join(args.out_format)}',
        f'Aggregate Outputs = {out_aggregate}',
    ]))

    save_osm_data(
        region_list=args.regions,
        primary_name=args.primary,
        feature_list=feature_list,
        data_dir=data_dir,
        out_dir=out_dir,
        update=args.update,
        mp=not args.no_mp,
        out_format=set(args.out_format),
        out_aggregate=out_aggregate,
    )

def handle_view(args):
    if args.type == 'regions':
        print('Viewing Regions')
        view_df = view_regions(level=0)
        view_df_str = view_df.to_string(na_rep='')
        view_df_str = view_df_str.replace('       0', 'iso-code')
        print(view_df_str)
    elif args.type == 'primary':
        raise NotImplementedError('Primary Feature Viewer Not Implemented')

def main():
    print(BANNER)
    parser = setup_parser()
    args = parser.parse_args()

    if args.command == 'extract':
        handle_extract(args)
    elif args.command == 'view':
        handle_view(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()