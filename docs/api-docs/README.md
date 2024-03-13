<!-- markdownlint-disable -->

# API Overview

## Modules

- [`args`](./args.md#module-args)
- [`config`](./config.md#module-config)
- [`eo`](./eo.md#module-eo)
- [`export`](./export.md#module-export)
- [`extract`](./extract.md#module-extract)
- [`filter`](./filter.md#module-filter)
- [`gfk_data`](./gfk_data.md#module-gfk_data)
- [`gfk_download`](./gfk_download.md#module-gfk_download)
- [`osmpbf`](./osmpbf.md#module-osmpbf)
- [`tagdata`](./tagdata.md#module-tagdata)
- [`taginfo`](./taginfo.md#module-taginfo)
- [`utils`](./utils.md#module-utils)

## Classes

- [`export.OutFileWriter`](./export.md#class-outfilewriter)
- [`osmpbf.Node`](./osmpbf.md#class-node): Node(id, tags, lonlat)
- [`osmpbf.Relation`](./osmpbf.md#class-relation): Relation(id, tags, members)
- [`osmpbf.Way`](./osmpbf.md#class-way): Way(id, tags, refs)

## Functions

- [`args.main`](./args.md#function-main): The main function executes on commands:
- [`eo.get_osm_data`](./eo.md#function-get_osm_data)
- [`eo.process_region`](./eo.md#function-process_region): Process Country
- [`eo.save_osm_data`](./eo.md#function-save_osm_data): Get OSM Data for a list of regions and features
- [`export.convert_pd_to_gdf`](./export.md#function-convert_pd_to_gdf)
- [`export.get_list_slug`](./export.md#function-get_list_slug)
- [`extract.filter_file_block`](./extract.md#function-filter_file_block)
- [`extract.filter_pbf`](./extract.md#function-filter_pbf): Parallized pre-Filtering of OSM file by a pre_filter
- [`extract.id_filter`](./extract.md#function-id_filter)
- [`extract.pool_file_query`](./extract.md#function-pool_file_query): returns query function that accepts a filter function and returns a list of filtered entries
- [`extract.primary_entry_filter`](./extract.md#function-primary_entry_filter)
- [`extract.way_filter`](./extract.md#function-way_filter)
- [`filter.feature_filter`](./filter.md#function-feature_filter)
- [`filter.get_filtered_data`](./filter.md#function-get_filtered_data)
- [`filter.run_feature_filter`](./filter.md#function-run_feature_filter)
- [`filter.run_primary_filter`](./filter.md#function-run_primary_filter)
- [`gfk_data.get_all_regions_dict`](./gfk_data.md#function-get_all_regions_dict): It takes a level argument, and returns a dictionary of all regions, grouped by their parent region
- [`gfk_data.get_all_valid_list`](./gfk_data.md#function-get_all_valid_list): Returns a list of all valid region ids
- [`gfk_data.get_code_by_id`](./gfk_data.md#function-get_code_by_id): Takes a region id (eg. germany) and returns its code (eg. DE)
- [`gfk_data.get_geom_sitemap`](./gfk_data.md#function-get_geom_sitemap)
- [`gfk_data.get_id_by_code`](./gfk_data.md#function-get_id_by_code): Takes a region code (eg. DE) and returns its id (eg. germany)
- [`gfk_data.get_id_by_str`](./gfk_data.md#function-get_id_by_str): Takes a region id or code (eg. DE, germany) and returns its id (eg. germany)
- [`gfk_data.get_region_dict`](./gfk_data.md#function-get_region_dict): Takes a region id (eg. germany) and returns a ditctionary consisting of
- [`gfk_data.get_region_tuple`](./gfk_data.md#function-get_region_tuple): Takes a region id or code (eg. DE, germany) and returns a named tuple with 
- [`gfk_data.get_root_list`](./gfk_data.md#function-get_root_list): Returns a list of regions without parents (i.e continents)
- [`gfk_download.calculate_md5`](./gfk_download.md#function-calculate_md5)
- [`gfk_download.download_file`](./gfk_download.md#function-download_file): Download file from url to dir
- [`gfk_download.download_pbf`](./gfk_download.md#function-download_pbf)
- [`gfk_download.download_sitemap`](./gfk_download.md#function-download_sitemap)
- [`gfk_download.verify_pbf`](./gfk_download.md#function-verify_pbf)
- [`tagdata.get_feature_list`](./tagdata.md#function-get_feature_list)
- [`tagdata.get_popular_features`](./tagdata.md#function-get_popular_features)
- [`tagdata.get_primary_list`](./tagdata.md#function-get_primary_list)
- [`tagdata.load_tag_data`](./tagdata.md#function-load_tag_data)
- [`taginfo.fetch_all_data`](./taginfo.md#function-fetch_all_data)
- [`taginfo.fetch_data_from_api`](./taginfo.md#function-fetch_data_from_api)
- [`taginfo.get_data`](./taginfo.md#function-get_data)
- [`taginfo.get_key_overview`](./taginfo.md#function-get_key_overview)
- [`taginfo.get_tag_data`](./taginfo.md#function-get_tag_data)
- [`taginfo.get_wiki_features`](./taginfo.md#function-get_wiki_features)
- [`taginfo.get_wiki_features_df`](./taginfo.md#function-get_wiki_features_df)
- [`taginfo.save_data`](./taginfo.md#function-save_data)
- [`utils.columns_melt`](./utils.md#function-columns_melt)
- [`utils.lonlat_lookup`](./utils.md#function-lonlat_lookup): Lookup refs and convert to list of longlats
- [`utils.tags_explode`](./utils.md#function-tags_explode)
- [`utils.tags_melt`](./utils.md#function-tags_melt)
- [`utils.way_or_area`](./utils.md#function-way_or_area)
