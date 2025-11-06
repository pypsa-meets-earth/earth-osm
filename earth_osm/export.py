
__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Export functions for earth_osm

This module contains functions for exporting OSM data to different file formats.

"""

import os
import ast
import csv
import json
import logging
import math
import tempfile
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set

import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point, Polygon

logger = logging.getLogger("eo.export")
logger.setLevel(logging.INFO)


def get_list_slug(str_list):
    import hashlib
    str_list.sort()
    if len(str_list) == 1:
        return str_list[0]
    else:
        file_slug = "_".join(str_list)
        if len(file_slug)>15:
            name_string = file_slug[:15]
            name_code = hashlib.md5(file_slug[15:].encode()).hexdigest()[:8]
            file_slug = name_string + '_' + name_code
        return file_slug
    
def convert_pd_to_gdf(pd_df):
    pd_df['lonlat'] = pd_df['lonlat'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    def create_geometry(lonlat_list, geom_type):
        if geom_type == 'node':
            return Point(lonlat_list[0])
        if geom_type == 'way':
            return LineString(lonlat_list)
        if geom_type == 'area':
            return Polygon(lonlat_list)

    geometry_col = pd_df.apply(lambda row: create_geometry(row['lonlat'], row['Type']), axis=1)
    lonlat_index = pd_df.columns.get_loc('lonlat')
    pd_df.insert(lonlat_index, "geometry", geometry_col)
    gdf = gpd.GeoDataFrame(pd_df, geometry='geometry')
    gdf.drop(columns=['lonlat'], inplace=True)
    pd_df.drop(columns=['geometry'], inplace=True)

    return gdf



class _ExportTarget:

    def __init__(self, region_list, primary_name, feature_list, data_dir, out_format):
        self.region_list = region_list
        self.primary_name = primary_name
        self.feature_list = feature_list
        self.data_dir = data_dir

        formats = [out_format] if isinstance(out_format, str) else list(out_format)
        if not formats:
            raise ValueError("out_format must contain at least one value")
        if "geojson" in formats and "csv" not in formats:
            raise ValueError("geojson output requires csv format")
        self.out_format = formats

        self.out_slug: Optional[str] = None
        self._temp_file = None
        self._temp_path: Optional[str] = None
        self._seen_columns: Set[str] = set()
        self._non_null_counts: Dict[str, int] = {}
        self._total_rows = 0
        self._melt_threshold = 0.95

        logger.debug(
            "File writer initialized with region_list: %s, primary_name: %s, feature_list: %s",
            region_list,
            primary_name,
            feature_list,
        )

    def open(self):
        if self._temp_file is not None:
            raise RuntimeError("Writer is already open")

        region_slug = get_list_slug(self.region_list)
        feature_slug = get_list_slug(self.feature_list)

        out_dir = os.path.join(self.data_dir, "out")
        self.out_slug = os.path.join(out_dir, f"{region_slug}_{feature_slug}")

        os.makedirs(out_dir, exist_ok=True)

        for ext in self.out_format:
            out_path = f"{self.out_slug}.{ext}"
            if os.path.exists(out_path):
                logger.debug("Deleting existing file: %s", out_path)
                os.remove(out_path)

        self._temp_file = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        )
        self._temp_path = self._temp_file.name
        self._seen_columns.clear()
        self._non_null_counts.clear()
        self._total_rows = 0

        return self

    def __enter__(self):
        return self.open()

    def __call__(self, rows):
        for record in self._iter_records(rows):
            self._write_record(record)

    def __exit__(self, exc_type, exc_value, traceback):
        return self._close(exc_type, exc_value, traceback)

    def close(self, exc_type=None, exc_value=None, traceback=None):
        self._close(exc_type, exc_value, traceback)

    def _close(self, exc_type, exc_value, traceback):
        if self._temp_file is not None:
            self._temp_file.close()

        try:
            if exc_type is not None:
                return False

            if self._total_rows == 0:
                self._write_empty_outputs()
            else:
                self._finalize_outputs()
        finally:
            self._cleanup_temp()

        return False

    def _iter_records(self, payload) -> Iterator[Dict[str, Any]]:
        if isinstance(payload, pd.DataFrame):
            yield from payload.to_dict(orient="records")
            return

        if isinstance(payload, dict):
            yield payload
            return

        for item in payload:
            if isinstance(item, pd.DataFrame):
                yield from item.to_dict(orient="records")
            else:
                yield item

    @staticmethod
    def _sanitize_value(value):
        if isinstance(value, float) and math.isnan(value):
            return None
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, pd.Series):
            return value.tolist()
        return value

    @staticmethod
    def _is_null(value) -> bool:
        if value is None:
            return True
        return isinstance(value, float) and math.isnan(value)

    def _write_record(self, record: Dict[str, Any]) -> None:
        if self._temp_file is None:
            raise RuntimeError("Writer is not active")

        sanitized: Dict[str, Any] = {}
        for key, value in record.items():
            value = self._sanitize_value(value)
            if key == "lonlat" and value is not None:
                value = [list(pair) for pair in value]
            elif key == "refs" and value is not None:
                value = list(value)

            sanitized[key] = value
            self._seen_columns.add(key)
            if not self._is_null(value):
                self._non_null_counts[key] = self._non_null_counts.get(key, 0) + 1

        self._temp_file.write(json.dumps(sanitized, ensure_ascii=False))
        self._temp_file.write("\n")
        self._total_rows += 1

    def _columns_to_melt(self) -> Set[str]:
        melt: Set[str] = set()
        if self._total_rows == 0:
            return melt

        threshold = 1.0 - self._melt_threshold
        for column in self._seen_columns:
            if not column.startswith("tags."):
                continue
            ratio = self._non_null_counts.get(column, 0) / self._total_rows
            if ratio <= threshold:
                melt.add(column)
        return melt

    def _determine_columns(self, melt_columns: Set[str]) -> List[str]:
        columns: List[str] = ["id", "Type", "Region", "lonlat"]
        if "refs" in self._seen_columns:
            columns.append("refs")

        reserved = set(columns)
        reserved.update(melt_columns)
        remaining = sorted(
            col
            for col in self._seen_columns
            if col not in reserved and col != "other_tags"
        )
        columns.extend(col for col in remaining if col not in columns)

        if melt_columns or "other_tags" in self._seen_columns:
            if "other_tags" not in columns:
                columns.append("other_tags")

        return columns

    def _apply_melt(self, record: Dict[str, Any], melt_columns: Set[str]) -> Dict[str, Any]:
        other_tags: Dict[str, Any] = {}
        existing = record.get("other_tags")
        if isinstance(existing, dict):
            other_tags.update(existing)

        for column in melt_columns:
            if column in record:
                value = record.pop(column)
                if not self._is_null(value):
                    other_tags[column] = value

        record["other_tags"] = other_tags or None
        return record

    def _prepare_csv_row(self, record: Dict[str, Any], columns: List[str]) -> Dict[str, Any]:
        row: Dict[str, Any] = {}
        for column in columns:
            value = record.get(column)
            if column == "other_tags":
                row[column] = json.dumps(value, ensure_ascii=False) if value else ""
            elif column == "lonlat":
                row[column] = json.dumps(value, ensure_ascii=False) if value else ""
            elif isinstance(value, (list, dict)):
                row[column] = json.dumps(value, ensure_ascii=False)
            elif value is None:
                row[column] = ""
            else:
                row[column] = value
        return row

    def _write_empty_outputs(self) -> None:
        csv_path = None
        if 'csv' in self.out_format:
            csv_path = f"{self.out_slug}.csv"
            with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["id", "Type", "Region", "lonlat"])
                writer.writeheader()
            logger.info("CSV: %s.csv (empty)", self.out_slug)

        if 'geojson' in self.out_format and csv_path is not None:
            self._convert_csv_to_geojson(csv_path)

    def _finalize_outputs(self) -> None:
        melt_columns = self._columns_to_melt()
        columns = self._determine_columns(melt_columns)

        csv_writer = None
        csv_file = None
        csv_path = None

        try:
            if 'csv' in self.out_format:
                csv_path = f"{self.out_slug}.csv"
                csv_file = open(csv_path, 'w', newline='', encoding='utf-8')
                csv_writer = csv.DictWriter(csv_file, fieldnames=columns)
                csv_writer.writeheader()

            with open(self._temp_path, 'r', encoding='utf-8') as source:
                for line in source:
                    record = json.loads(line)
                    record = self._apply_melt(record, melt_columns)

                    if csv_writer is not None:
                        csv_writer.writerow(self._prepare_csv_row(record, columns))

        finally:
            if csv_file is not None:
                csv_file.close()

        if 'csv' in self.out_format:
            logger.info("CSV: %s.csv", self.out_slug)
        if 'geojson' in self.out_format and csv_path is not None:
            self._convert_csv_to_geojson(csv_path)

    def _cleanup_temp(self) -> None:
        if self._temp_path and os.path.exists(self._temp_path):
            os.remove(self._temp_path)
        self._temp_path = None
        self._temp_file = None

    def _convert_csv_to_geojson(self, csv_path: str) -> None:
        geojson_path = f"{self.out_slug}.geojson"

        df = pd.read_csv(csv_path)
        if df.empty:
            base = df.drop(columns=["lonlat"], errors="ignore")
            geometry = gpd.GeoSeries([], name="geometry", dtype="geometry")
            gdf = gpd.GeoDataFrame(base, geometry=geometry)
        else:
            gdf = convert_pd_to_gdf(df)

        gdf.set_crs(epsg=4326, inplace=True, allow_override=True)
        gdf.to_file(geojson_path, driver="GeoJSON")
        logger.info("GEOJSON: %s.geojson", self.out_slug)


class EarthOSMWriter:

    def __init__(self, primary_name: str, data_dir: str, out_format):
        formats = [out_format] if isinstance(out_format, str) else list(out_format)
        if not formats:
            raise ValueError("out_format must contain at least one value")
        if "geojson" in formats and "csv" not in formats:
            raise ValueError("geojson output requires csv format")

        self.primary_name = primary_name
        self.data_dir = data_dir
        self.out_format = formats
        self._targets: Dict[tuple, _ExportTarget] = {}
        self._closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close(exc_type, exc_value, traceback)
        return False

    def prepare_target(self, region_list: Iterable[str], feature_list: Iterable[str]) -> None:
        self._ensure_target(region_list, feature_list)

    def write(
        self,
        region_list: Iterable[str],
        feature_list: Iterable[str],
        rows: Iterable[Any],
    ) -> None:
        target = self._ensure_target(region_list, feature_list)
        target(rows)

    def close(self, exc_type=None, exc_value=None, traceback=None):
        if self._closed:
            return
        self._closed = True
        for target in self._targets.values():
            target.close(exc_type, exc_value, traceback)

    def _ensure_target(
        self,
        region_list: Iterable[str],
        feature_list: Iterable[str],
    ) -> _ExportTarget:
        region_key = tuple(sorted(region_list))
        feature_key = tuple(sorted(feature_list))
        slug_key = (region_key, feature_key)

        target = self._targets.get(slug_key)
        if target is None:
            target = _ExportTarget(
                list(region_list),
                self.primary_name,
                list(feature_list),
                self.data_dir,
                self.out_format,
            )
            target.open()
            self._targets[slug_key] = target
        return target

