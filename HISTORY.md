# Changelog

## 3.1.0 — 2026-10-25

### Added

- Limit extraction workers with `--mp N` or `save_osm_data(mp=N)` in both the legacy and streaming pipelines. Existing automatic sizing and `--no_mp` behavior are preserved. [#90](https://github.com/pypsa-meets-earth/earth-osm/pull/90)
- Configure Overpass endpoints and timeouts through environment variables. [#81](https://github.com/pypsa-meets-earth/earth-osm/pull/81)

### Fixed

- Remove duplicate OSM elements from exports, including overlapping regional extracts. [#89](https://github.com/pypsa-meets-earth/earth-osm/pull/89)
- Correct historical Geofabrik download URLs, including nested region identifiers. [#85](https://github.com/pypsa-meets-earth/earth-osm/pull/85)
- Refresh the Geofabrik region catalogue. [#86](https://github.com/pypsa-meets-earth/earth-osm/pull/86)
- Expose `save_osm_data` and `get_osm_data` at package level and read package metadata from the version file. [#80](https://github.com/pypsa-meets-earth/earth-osm/pull/80)

### Upgrade note

Deduplication is automatic: each output retains the first occurrence of a `(Type, id)` pair. Exported row counts may decrease where regional extracts overlap; later copies of the same element are discarded even if their coordinates or tags differ.

[All changes since 3.0.2](https://github.com/pypsa-meets-earth/earth-osm/compare/3.0.2...3.1.0)
