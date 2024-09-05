Changelog
=========


(unreleased)
------------
- Return view_df. [Matin Mahmood]
- Refactor arg parser. [Matin Mahmood]
- Allow to disable the progressbar (#53) [Fabian Hofmann]
- Update README. [Matin Mahmood]
- Update OutFileWriter to EarthOSMWriter for consistency. [Matin
  Mahmood]

  Refactor OutFileWriter to EarthOSMWriter and optimize CSV/GeoJSON export

  Renamed `OutFileWriter` to `EarthOSMWriter` across the codebase to maintain consistency with project naming conventions. Enhanced the export functionality by introducing a batch processing approach, accumulating dataframes before writing, which streamlines the CSV and GeoJSON file generation process. This change reduces I/O operations during export, potentially improving performance for large datasets. Furthermore, redundant data manipulation and file handling logic were removed, simplifying the export process. The new approach also includes optimizations such as melting tags with high percentages of NaN values and consolidating dataframe operations to minimize memory usage and improve runtime efficiency.
- Rename test_power to test_export. [Matin Mahmood]
- Update api docs. [Matin Mahmood]
- - add a test for comparing earth_osm with osmium - update test
  dependencies. [Matin Mahmood]
- Auto-remove corrupt PBF and MD5 files on verification fail. [Matin
  Mahmood]
- Improve debug code. [Matin Mahmood]
- Moved `OutFileWriter` and related functions (`convert_pd_to_gdf` and
  `get_list_slug`) into a new `export.py` module to centralize export-
  related responsibilities. This enhancement clears up `utils.py`,
  focusing it more on utility functions that aren't directly tied to
  data export. The shift to `export.py` allows for a more organized
  structure, making it easier to extend export functionalities in the
  future. [Matin Mahmood]


2.1 (2024-03-03)
----------------
- Release: version 2.1 🚀 [Matin Mahmood]


2.0 (2024-03-03)
----------------
- Release: version 2.0 🚀 [Matin Mahmood]
- Improve error handling and adjust geom definition criteria. [Matin
  Mahmood]

  - Added a missing return statement to immediately exit the `lonlat_lookup` function when the `refs` column is unavailable, enhancing error resilience.
  - Modified the minimum number of references required to classify geometries as areas or ways: now considering a sequence as an area if it's closed (first and last refs are the same) and consists of at least 4 points (previously 3), and as a way if it includes at least 2 points (previously 3). This adjustment aligns better with common geometric definitions, ensuring that areas have a more defined shape and ways are simplified.
  - Replaced a TODO comment with a debug log statement for instances where geometries have less than the intended number of references, improving debuggability and future maintenance.

  This change aims to enhance the accuracy of geometrical data processing and improve error handling for better stability and clarity in logs.
- Update taginfo for data. [Matin Mahmood]
- Standardize logger. [Matin Mahmood]
- Small fixes to main function. [Matin Mahmood]
- Update docs. [Matin Mahmood]
- Corrupt pbf files cause bugs #36, also fix update param. [Matin
  Mahmood]
- Remove deprecated functions. [Matin Mahmood]
- Fail CI if tests fail. [Matin Mahmood]
- Fix issue ValueError: Must have equal len keys and value when setting
  with an iterable #47. [Matin Mahmood]
- Improve tests and coverage report (60% to 76%) [Matin Mahmood]
- Fail test if error (#49) [Matin Mahmood]
- Add tests to diagnose issue #47 (#48) [Matin Mahmood]

  * add tests to diagnose issue #47

  * update get_osm_data
- Release: version 0.2 🚀 [Matin Mahmood]
- Merge pull request #46 from davide-f/buildings. [Matin Mahmood]

  Buildings
- Update building test. [Matin Mahmood]
- Change wildcard identifier. [Matin Mahmood]
- Update is_feature and building test. [Davide Fioriti]
- Merge commit 'e6e95a01469f784e541e48d96284536659c205d1' into
  buildings. [Davide Fioriti]
- Merge branch 'main' into add_out_dir. [Davide Fioriti]
- Remove refuse. [Davide Fioriti]
- Simplify PR. [Davide Fioriti]
- Add option to download all primary features. [Davide Fioriti]
- Enable downloading all data of primary feature, e.g. buildings.
  [Davide Fioriti]
- Update gitignore. [Davide Fioriti]
- Add release_note. [Davide Fioriti]
- Add out_dir option. [Davide Fioriti]


0.2 (2023-12-13)
----------------
- Release: version 0.2 🚀 [Matin Mahmood]
- Improve tests. [Matin Mahmood]
- Improve gfk logging. [Matin Mahmood]
- Dynamically get feature from taginfo api. [Matin Mahmood]
- Update README.md. [Max Parzen]
- Update api-docs. [Matin Mahmood]
- Add lazydoc auto api documentaiton generation. [Matin Mahmood]
- Add api docs generation. [Matin Mahmood]
- Update docs workflow to use makefile. [Matin Mahmood]
- Separate docs. [Matin Mahmood]
- Update docs-ci.yml. [Matin Mahmood]
- Add MkDocs. [Matin Mahmood]
- Improve readibility. [Matin Mahmood]
- Improve readability. [Matin Mahmood]
- Update README.md. [Matin Mahmood]
- Create docs-ci.yml. [Matin Mahmood]
- Improve test. [Matin Mahmood]
- Improve test. [Matin Mahmood]
- Add building to config. [Matin Mahmood]
- Add data_dir. [Matin Mahmood]
- General bug fix. [Matin Mahmood]
- Rename multiprocessing. [Matin Mahmood]
- Push aggregation. [Matin Mahmood]
- Rename get_osm_data to save_osm_data. [Matin Mahmood]
- Add area (#38) [Matin Mahmood]

  * add way_or_area funciton

  * add way_to_polygon function

  * fix retun statement in ways_lines

  * add tags melt and explode functions

  * combine functions to pd_to_gdf

  * add output_creation

  * add debug code

  * improve imports

  * rename country to region

  * refactor process pipe

  * add comments and small refactor

  * reduce config

  * add notes

  * small refactor

  * improve base test

  * remove comment

  * add power tests

  * add todo code

  * remove lint from make test for now
- Remove code cov fixes #35. [Matin Mahmood]
- Update protobuf. [Matin Mahmood]
- Update README.md. [Matin Mahmood]
- Improve error message missing region (#34) [Davide Fioriti]


0.1.0 (2023-03-04)
------------------
- Release: version 0.1.0 🚀 [Matin Mahmood]
- Update utils.py (#30) [Davide Fioriti]

  Drop non-way elements in way entries


0.0.9 (2023-02-17)
------------------
- Release: version 0.0.9 🚀 [Matin Mahmood]
- Add current work in progress. [mnm-matin]
- Fix sitemap download everytime. [mnm-matin]
- Fix out format. [mnm-matin]
- Add new args decription to readme. [Max Parzen]
- Update contributing. [mnm-matin]
- Add gfk_data test. [mnm-matin]
- Update code cov workflow. [mnm-matin]
- Add codecov again, remove size. [Matin Mahmood]
- Update README.md. [Matin Mahmood]
- Update README.md. [Max Parzen]
- Fix badge version. [Max Parzen]
- Add conda badge. [Max Parzen]


0.0.8 (2023-01-01)
------------------
- Release: version 0.0.8 🚀 [Max Parzen]
- Revert changes. [Max Parzen]


0.0.7 (2023-01-01)
------------------
- Release: version 0.0.7 🚀 [Max Parzen]
- Read automatically requirements. [Max Parzen]


0.0.6 (2022-12-31)
------------------
- Release: version 0.0.6 🚀 [Max Parzen]
- Add missing comma. [Max Parzen]


0.0.5 (2022-12-31)
------------------
- Release: version 0.0.5 🚀 [Max Parzen]
- Make packages explicit in setup. [Max Parzen]


0.0.4 (2022-12-31)
------------------
- Release: version 0.0.4 🚀 [Max Parzen]
- Add requirements to manifest. [Max Parzen]


0.0.3 (2022-12-31)
------------------
- Release: version 0.0.3 🚀 [Max Parzen]
- Release: version 0.0.2 🚀 [Max Parzen]
- Remove for now docker file (#24) [Max Parzen]
- Small path fix. [mnm-matin]
- Add whitespace. [mnm-matin]
- Disable CI for mac and windows. [mnm-matin]
- Add docstrings for filter_pbf. [mnm-matin]
- Revert "lint code (#22)" [mnm-matin]

  This reverts commit 0c5388e8cd0d82c185a44aa4a50fba76a9419c14.
- Revert "release 0.0.2 (#23)" [mnm-matin]

  This reverts commit 8a1ee61c4a6f39770d24b7f9b2d60c96e617bc45.


0.0.2 (2022-12-30)
------------------
- Release 0.0.2 (#23) [Max Parzen]
- Lint code (#22) [Max Parzen]
- Add docs and classifiers to setup. [Max Parzen]
- Update README.md. [Max Parzen]
- Update setup.py. [Max Parzen]
- Merge branch 'main' of https://github.com/pypsa-meets-africa/earth-osm
  into main. [mnm-matin]
- Update README.md. [Max Parzen]
- Add badges (#21) [Max Parzen]

  * add badges

  * rename header
- Pin mypy version. [mnm-matin]
- Contrib add docs update. [mnm-matin]
- Add codecov badge. [mnm-matin]
- Add test tot makefile. [mnm-matin]
- Add test. [mnm-matin]
- Enable tests and code cov. [mnm-matin]
- Add CI badge. [mnm-matin]
- Add development notes to README. [mnm-matin]
- Remove f string. [mnm-matin]
- Add make release to make file. [mnm-matin]
- Add release instruction. [mnm-matin]


0.0.1 (2022-12-30)
------------------
- Release: version 0.0.1 🚀 [mnm-matin]
- Merge pull request #20 from pz-max/cat. [Matin Mahmood]

  add aggregate option and output format choice
- Fixes n roll. [Max Parzen]
- Add aggregate option and output format choice. [Max Parzen]
- Add MANIFEST.in and History.md. [mnm-matin]
- Add pypi release workkflow. [mnm-matin]
- Merge pull request #19 from pz-max/main. [Matin Mahmood]

  fix encoding bug
- Fix encoding bug. [Max Parzen]
- Merge pull request #17 from pypsa-meets-earth/pz-max-patch-1. [Matin
  Mahmood]

  area crs correction and documentation
- Area crs correction and documentation. [Max Parzen]
- Disable tests from CI. [mnm-matin]
- Add CI test without linter. [mnm-matin]
- Merge pull request #2 from pz-max/rename-africa. [Matin Mahmood]

  rename africa to earth
- Rename africa to earth. [Max Parzen]
- Improve readability. [mnm-matin]
- Merge branch 'main' of https://github.com/pypsa-meets-africa/earth-osm
  into main. [mnm-matin]
- Update README.md. [Matin Mahmood]
- Update README.md. [Matin Mahmood]
- Requirements specify version for protobuf. [mnm-matin]
- Add contributing guide. [mnm-matin]
- Pull Request Template. [mnm-matin]
- Feature request template. [mnm-matin]
- Add bug_report template. [mnm-matin]
- Add docker containerfile. [mnm-matin]
- Make docs. [mnm-matin]
- Make virtualenv. [mnm-matin]
- Make clean. [mnm-matin]
- Add linting. [mnm-matin]
- Add formatting. [mnm-matin]
- Make install Makefile. [mnm-matin]
- Generate lazydocs api docs. [mnm-matin]
- Docs index. [mnm-matin]
- Add mkdocs config. [mnm-matin]
- Header. [mnm-matin]
- Advanced usage instructions. [mnm-matin]
- Args explained. [mnm-matin]
- Extract readme. [mnm-matin]
- Getting started readme. [mnm-matin]
- Setup tools and requirements. [mnm-matin]
- Add version file package. [mnm-matin]
- Initialize test module. [mnm-matin]
- Misc argparser notes. [mnm-matin]
- Version arg for test. [mnm-matin]
- Help arg and subparser helper. [mnm-matin]
- Add earth_osm print. [mnm-matin]
- Add not implemented interactive parser. [mnm-matin]
- Exeecute get_osm_data. [mnm-matin]
- Verbose print args. [mnm-matin]
- Verify data args. [mnm-matin]
- Verify feature args. [mnm-matin]
- Not implemented coord args. [mnm-matin]
- Region arg logic. [mnm-matin]
- Print regions. [mnm-matin]
- Parse args. [mnm-matin]
- View type arg. [mnm-matin]
- Sub parser view. [mnm-matin]
- Extract data_dir arg. [mnm-matin]
- Extract mp arg. [mnm-matin]
- Extract update arg. [mnm-matin]
- Extract feature arg. [mnm-matin]
- Extract region list arg. [mnm-matin]
- Add extract primary arg. [mnm-matin]
- Add basic argparser. [mnm-matin]
- Finalize base executer function. [mnm-matin]
- Add function rename todo. [mnm-matin]
- Csv and geojson emitter. [mnm-matin]
- Conv pd to gdf lines. [mnm-matin]
- Conv pd to gdf nodes. [mnm-matin]
- Add earth_osm region processor. [mnm-matin]
- Convert ways to lines. [mnm-matin]
- Conv ways to points. [mnm-matin]
- Lonlat lookup. [mnm-matin]
- Filtered data wrapper. [mnm-matin]
- Primary dict filter. [mnm-matin]
- Add filter runner. [mnm-matin]
- Filter primary data. [mnm-matin]
- Add feature filter header. [mnm-matin]
- Add osm config. [mnm-matin]
- Add extract script header. [mnm-matin]
- Add multiprocessing supported primary filter. [mnm-matin]
- Commands for generating latest protoc file. [mnm-matin]
- How to install protoc. [mnm-matin]
- Osm proto compile instructions. [mnm-matin]
- Add proto files to gitignore. [mnm-matin]
- Add osmpbf file script header. [mnm-matin]
- Add osmpbf filereader. [mnm-matin]
- Generate latest protocol buffer. [mnm-matin]
- Add relation namedtuple. [mnm-matin]
- Add way namedtuple. [mnm-matin]
- Add Node namedtuple. [mnm-matin]
- Initialize osmpbf module. [mnm-matin]
- Region tuple docstring. [mnm-matin]
- Region tuple getter. [mnm-matin]
- Id by string docstrings. [mnm-matin]
- Id by string getter. [mnm-matin]
- Code by id docstring. [mnm-matin]
- Code by id getter. [mnm-matin]
- Id_by_code docstring. [mnm-matin]
- Get id by using code. [mnm-matin]
- Add region dict getter. [mnm-matin]
- View_region doc strings. [mnm-matin]
- View region function. [mnm-matin]
- Add all region doc srings. [mnm-matin]
- Add all region dict getter. [mnm-matin]
- Add valid list function. [mnm-matin]
- Add root list function. [mnm-matin]
- Add support for geometric sitemap. [mnm-matin]
- Add short_code to sitemap df. [mnm-matin]
- Download sitemap. [mnm-matin]
- Add gfk_data header. [mnm-matin]
- Add misc download verify code. [mnm-matin]
- Add update param todo. [mnm-matin]
- Add sitemap downloader. [mnm-matin]
- Add multi-download todo. [mnm-matin]
- Add earth_downloader docstrings. [mnm-matin]
- Add earth_downloader function. [mnm-matin]
- Gfk_download header. [mnm-matin]
- Add args entry point header. [mnm-matin]
- Set earth_osm entry point. [mnm-matin]
- Initialize python project. [mnm-matin]
- Add YEAR and PyPSA-meets-Earth. [mnm-matin]
- Add MIT LICENSE. [mnm-matin]
- Gitignore misc. [mnm-matin]
- Gitingore docs. [mnm-matin]
- Gitignore environments. [mnm-matin]
- Gitignore unit tests. [mnm-matin]
- Gitingore py package files. [mnm-matin]
- Gitignore py files. [mnm-matin]
- Gitignore external data dir. [mnm-matin]
- Gitignore internal dir. [mnm-matin]


