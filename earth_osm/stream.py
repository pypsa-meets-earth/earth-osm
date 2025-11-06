"""Streaming pipeline for OpenStreetMap PBF processing.

This module provides generator-based utilities that expose OSM features as
streaming iterables so downstream consumers can process data without loading
entire region exports into memory. The implementation reuses the low-level PBF
parsers that ship with earth-osm and focuses on the subset of geometry elements
(nodes and ways) that are currently required by the public API. Relations are
collected for completeness but not yet converted into feature rows because the
existing exporters only consume nodes and ways.
"""

from __future__ import annotations

import json
import logging
import multiprocessing as mp
import os
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Sequence, Set, Union

from earth_osm.extract import primary_entry_filter
from earth_osm.regions import download_region_pbf
from earth_osm.osmpbf import Node, Relation, Way, fileformat_pb2, osmformat_pb2
from earth_osm.osmpbf.file import iter_blocks, iter_primitive_block, read_blob
from earth_osm.utils import tag_value_matches

logger = logging.getLogger("eo.stream")

PROGRESS_INTERVAL = 50000
BLOCK_PROGRESS_STEP = 1


@dataclass(frozen=True)
class FeatureRow:
    """Representation of a flattened OSM feature row.

    The fields mirror the columns produced by the previous DataFrame-based
    pipeline. Tag keys are stored in their flattened ``tags.<key>`` form so the
    writer can operate without an intermediate pandas dependency.
    """

    id: int
    region: str
    type: str
    lonlat: Sequence[Sequence[float]]
    refs: Optional[List[int]]
    tags: Dict[str, str]

    def to_dict(self) -> Dict[str, object]:
        row: Dict[str, object] = {
            "id": self.id,
            "Region": self.region,
            "Type": self.type,
            "lonlat": [list(pair) for pair in self.lonlat],
        }
        if self.refs is not None:
            row["refs"] = list(self.refs)
        for key, value in self.tags.items():
            row[f"tags.{key}"] = value
        return row


def _normalize_feature_names(feature_selection: Union[str, Sequence[str]]) -> List[str]:
    if isinstance(feature_selection, str):
        candidates: List[str] = [feature_selection]
    else:
        candidates = list(feature_selection)

    normalized: List[str] = []
    seen: Set[str] = set()
    for name in candidates:
        if not name:
            continue
        if name in seen:
            continue
        seen.add(name)
        normalized.append(name)

    if not normalized:
        raise ValueError("feature selection must contain at least one value")

    return normalized


def _format_feature_descriptor(feature_names: Sequence[str]) -> str:
    if not feature_names:
        return "*"
    if len(feature_names) == 1:
        return feature_names[0]
    return ",".join(feature_names)


def _iter_matching_features(
    tags: Dict[str, str],
    primary_name: str,
    feature_names: Sequence[str],
) -> Iterator[str]:
    value = tags.get(primary_name)
    if value is None:
        return

    for feature_name in feature_names:
        if tag_value_matches(value, feature_name):
            yield feature_name


def _build_pre_filter(
    primary_name: str,
    feature_selection: Union[str, Sequence[str]],
) -> Dict[type, Dict[str, List[str]]]:
    feature_values = _normalize_feature_names(feature_selection)
    return {
        Node: {primary_name: feature_values},
        Way: {primary_name: feature_values},
        Relation: {primary_name: feature_values},
    }


def _make_progress_callback(description: str, step: int = 5) -> Callable[[int, int], None]:
    """Build a logging callback that reports incremental scan progress."""

    next_report = 0
    reported_complete = False

    def _callback(processed_bytes: int, total_bytes: int) -> None:
        nonlocal next_report, reported_complete
        if total_bytes <= 0:
            return

        percent = int((processed_bytes / total_bytes) * 100)

        if percent >= 100:
            if not reported_complete:
                logger.info("%s 100%%", description)
                reported_complete = True
            return

        bucket = (percent // step) * step
        if bucket >= next_report:
            logger.info("%s %d%%", description, bucket)
            next_report = bucket + step

    return _callback


def _prepare_block_descriptors(filename: str) -> List[tuple[int, bytes]]:
    descriptors: List[tuple[int, bytes]] = []
    with open(filename, "rb") as file:
        for ofs, header in iter_blocks(file):
            descriptors.append((ofs, header.SerializeToString()))
    return descriptors


def _scan_block_worker(
    task: tuple[str, int, bytes, str, Sequence[str]]
) -> tuple[List[Node], List[Way], Set[int]]:
    filename, ofs, header_bytes, primary_name, feature_names = task

    header = fileformat_pb2.BlobHeader()
    header.ParseFromString(header_bytes)

    primitive = osmformat_pb2.PrimitiveBlock()
    with open(filename, "rb") as file:
        primitive.ParseFromString(read_blob(file, ofs, header))

    pre_filter = _build_pre_filter(primary_name, feature_names)

    nodes: List[Node] = []
    ways: List[Way] = []
    referenced: Set[int] = set()

    for entry in iter_primitive_block(primitive):
        if not primary_entry_filter(entry, pre_filter):
            continue

        if isinstance(entry, Node):
            nodes.append(entry)
        elif isinstance(entry, Way):
            ways.append(entry)
            referenced.update(entry.refs)

    return nodes, ways, referenced


_NODE_TARGETS: Set[int] = set()


def _init_node_worker(required_ids: Set[int]) -> None:
    global _NODE_TARGETS
    _NODE_TARGETS = set(required_ids)


def _collect_nodes_block(task: tuple[str, int, bytes]) -> Dict[int, Node]:
    filename, ofs, header_bytes = task

    header = fileformat_pb2.BlobHeader()
    header.ParseFromString(header_bytes)

    primitive = osmformat_pb2.PrimitiveBlock()
    with open(filename, "rb") as file:
        primitive.ParseFromString(read_blob(file, ofs, header))

    captured: Dict[int, Node] = {}
    targets = _NODE_TARGETS
    if not targets:
        return captured

    for entry in iter_primitive_block(primitive):
        if isinstance(entry, Node) and entry.id in targets:
            captured[entry.id] = entry

    return captured


def _iter_pbf_entries(
    filename: str,
    *,
    progress_cb: Optional[Callable[[int, int], None]] = None,
) -> Iterator[object]:
    file_size = os.path.getsize(filename)
    processed = 0

    with open(filename, "rb") as file:
        for ofs, header in iter_blocks(file):
            primitive = osmformat_pb2.PrimitiveBlock()
            primitive.ParseFromString(read_blob(file, ofs, header))
            processed = min(ofs + header.datasize, file_size)
            if progress_cb is not None:
                progress_cb(processed, file_size)
            yield from iter_primitive_block(primitive)

    if progress_cb is not None:
        progress_cb(file_size, file_size)


def _iter_node_rows(
    nodes: Dict[int, Node],
    region_code: str,
) -> Iterator[FeatureRow]:
    for node_id in sorted(nodes):
        node = nodes[node_id]
        lonlat = (tuple(node.lonlat),)
        yield FeatureRow(
            id=node.id,
            region=region_code,
            type="node",
            lonlat=lonlat,
            refs=None,
            tags=node.tags,
        )


def _iter_way_rows(
    way_records: Iterable[Way],
    nodes: Dict[int, Node],
    region_code: str,
) -> Iterator[FeatureRow]:
    for way in sorted(way_records, key=lambda item: item.id):
        coords: List[tuple] = []
        missing = False
        for ref in way.refs:
            node = nodes.get(ref)
            if node is None:
                missing = True
                logger.debug("Way %s references missing node %s", way.id, ref)
                break
            coords.append(tuple(node.lonlat))

        if missing or len(coords) < 2:
            logger.debug("Skipping way %s due to insufficient coordinates", way.id)
            continue

        feature_type = "area" if len(coords) >= 4 and coords[0] == coords[-1] else "way"

        yield FeatureRow(
            id=way.id,
            region=region_code,
            type=feature_type,
            lonlat=coords,
            refs=list(way.refs),
            tags=way.tags,
        )


def _collect_targets_sequential(
    filename: str,
    primary_name: str,
    feature_names: Sequence[str],
) -> tuple[Dict[int, Node], List[Way], Set[int]]:
    pre_filter = _build_pre_filter(primary_name, feature_names)
    feature_desc = _format_feature_descriptor(feature_names)

    target_nodes: Dict[int, Node] = {}
    target_ways: List[Way] = []
    required_node_ids: Set[int] = set()

    logger.info(
        "Scanning %s for %s=%s candidates",
        os.path.basename(filename),
        primary_name,
        feature_desc,
    )

    progress_cb = _make_progress_callback(
        f"Scanning {os.path.basename(filename)} ({primary_name}={feature_desc})",
        step=1,
    )

    for entry in _iter_pbf_entries(filename, progress_cb=progress_cb):
        if not primary_entry_filter(entry, pre_filter):
            continue

        if isinstance(entry, Node):
            target_nodes[entry.id] = entry
        elif isinstance(entry, Way):
            target_ways.append(entry)
            required_node_ids.update(entry.refs)

    logger.info(
        "Completed scan of %s: %d candidate ways, %d candidate nodes, %d referenced nodes",
        os.path.basename(filename),
        len(target_ways),
        len(target_nodes),
        len(required_node_ids),
    )

    return target_nodes, target_ways, required_node_ids


def _collect_targets_parallel(
    filename: str,
    primary_name: str,
    feature_names: Sequence[str],
    block_descriptors: Sequence[tuple[int, bytes]],
) -> tuple[Dict[int, Node], List[Way], Set[int]]:
    total_blocks = len(block_descriptors)
    if total_blocks == 0:
        return {}, [], set()

    worker_count = max(1, mp.cpu_count() - 1 or 1)
    feature_desc = _format_feature_descriptor(feature_names)
    logger.info(
        "Scanning %s for %s=%s candidates across %d blocks (workers=%d)",
        os.path.basename(filename),
        primary_name,
        feature_desc,
        total_blocks,
        worker_count,
    )

    target_nodes: Dict[int, Node] = {}
    target_ways: List[Way] = []
    required_node_ids: Set[int] = set()

    progress_every = max(1, total_blocks * BLOCK_PROGRESS_STEP // 100)

    feature_tuple = tuple(feature_names)
    tasks = (
        (filename, ofs, header_bytes, primary_name, feature_tuple)
        for ofs, header_bytes in block_descriptors
    )

    with mp.Pool(worker_count) as pool:
        for idx, (node_chunk, way_chunk, ref_chunk) in enumerate(
            pool.imap_unordered(_scan_block_worker, tasks, chunksize=1),
            start=1,
        ):
            if node_chunk:
                for node in node_chunk:
                    target_nodes[node.id] = node
            if way_chunk:
                target_ways.extend(way_chunk)
            if ref_chunk:
                required_node_ids.update(ref_chunk)

            if idx % progress_every == 0 or idx == total_blocks:
                percent = int((idx / total_blocks) * 100)
                logger.info(
                    "Scanning %s (%s=%s): %d%% (%d/%d blocks, nodes=%d, ways=%d)",
                    os.path.basename(filename),
                    primary_name,
                    feature_desc,
                    percent,
                    idx,
                    total_blocks,
                    len(target_nodes),
                    len(target_ways),
                )

    logger.info(
        "Completed scan of %s: %d candidate ways, %d candidate nodes, %d referenced nodes",
        os.path.basename(filename),
        len(target_ways),
        len(target_nodes),
        len(required_node_ids),
    )

    return target_nodes, target_ways, required_node_ids


def _collect_targets(
    filename: str,
    primary_name: str,
    feature_selection: Union[str, Sequence[str]],
    *,
    multiprocess: bool = False,
    block_descriptors: Optional[Sequence[tuple[int, bytes]]] = None,
) -> tuple[Dict[int, Node], List[Way], Set[int]]:
    feature_names = _normalize_feature_names(feature_selection)
    if multiprocess:
        descriptors = block_descriptors or _prepare_block_descriptors(filename)
        return _collect_targets_parallel(filename, primary_name, feature_names, descriptors)
    return _collect_targets_sequential(filename, primary_name, feature_names)


def _collect_nodes_sequential(filename: str, required_node_ids: Set[int]) -> Dict[int, Node]:
    if not required_node_ids:
        return {}

    captured: Dict[int, Node] = {}
    remaining = set(required_node_ids)

    logger.info(
        "Capturing %d prerequisite nodes from %s",
        len(required_node_ids),
        os.path.basename(filename),
    )

    progress_cb = _make_progress_callback(
        f"Collecting nodes from {os.path.basename(filename)}",
        step=1,
    )

    for entry in _iter_pbf_entries(filename, progress_cb=progress_cb):
        if not isinstance(entry, Node):
            continue
        if entry.id not in remaining:
            continue

        captured[entry.id] = entry
        remaining.remove(entry.id)
        if not remaining:
            break

    if remaining:
        logger.info(
            "Finished collecting node coordinates with %d missing nodes",
            len(remaining),
        )
    else:
        logger.info("Captured coordinates for all referenced nodes")

    return captured


def _collect_nodes_parallel(
    filename: str,
    required_node_ids: Set[int],
    block_descriptors: Sequence[tuple[int, bytes]],
) -> Dict[int, Node]:
    if not required_node_ids:
        return {}

    total_blocks = len(block_descriptors)
    if total_blocks == 0:
        return {}

    worker_count = max(1, mp.cpu_count() - 1 or 1)
    logger.info(
        "Capturing %d prerequisite nodes from %s using %d workers",
        len(required_node_ids),
        os.path.basename(filename),
        worker_count,
    )

    captured: Dict[int, Node] = {}
    progress_every = max(1, total_blocks * BLOCK_PROGRESS_STEP // 100)

    tasks = ((filename, ofs, header_bytes) for ofs, header_bytes in block_descriptors)

    with mp.Pool(
        worker_count,
        initializer=_init_node_worker,
        initargs=(required_node_ids,),
    ) as pool:
        for idx, chunk in enumerate(
            pool.imap_unordered(_collect_nodes_block, tasks, chunksize=1),
            start=1,
        ):
            if chunk:
                captured.update(chunk)

            if idx % progress_every == 0 or idx == total_blocks:
                percent = int((idx / total_blocks) * 100)
                logger.info(
                    "Collecting nodes from %s: %d%% (%d/%d blocks, captured=%d/%d)",
                    os.path.basename(filename),
                    percent,
                    idx,
                    total_blocks,
                    len(captured),
                    len(required_node_ids),
                )

            if len(captured) >= len(required_node_ids):
                logger.info(
                    "Captured coordinates for all referenced nodes after %d blocks",
                    idx,
                )
                pool.terminate()
                break

    missing = len(required_node_ids) - len(captured)
    if missing > 0:
        logger.info("Finished collecting node coordinates with %d missing nodes", missing)
    else:
        logger.info("Captured coordinates for all referenced nodes")

    return captured


def _collect_nodes(
    filename: str,
    required_node_ids: Set[int],
    *,
    multiprocess: bool = False,
    block_descriptors: Optional[Sequence[tuple[int, bytes]]] = None,
) -> Dict[int, Node]:
    if multiprocess:
        descriptors = block_descriptors or _prepare_block_descriptors(filename)
        return _collect_nodes_parallel(filename, required_node_ids, descriptors)
    return _collect_nodes_sequential(filename, required_node_ids)


def _log_stage_progress(
    region_code: str,
    primary_name: str,
    feature_name: str,
    stage: str,
    count: int,
    total: int,
    final: bool = False,
) -> None:
    if final:
        logger.info(
            "Region %s (%s=%s): %s stage completed with %d features (%d total)",
            region_code,
            primary_name,
            feature_name,
            stage,
            count,
            total,
        )
        return

    logger.info(
        "Region %s (%s=%s): %s stage streamed %d features (%d total)",
        region_code,
        primary_name,
        feature_name,
        stage,
        count,
        total,
    )


def stream_pbf_features(
    filename: str,
    primary_name: str,
    feature_name: str,
    region_code: str,
    *,
    multiprocess: bool = False,
) -> Iterator[Dict[str, object]]:
    block_descriptors: Optional[Sequence[tuple[int, bytes]]] = None
    if multiprocess:
        block_descriptors = _prepare_block_descriptors(filename)

    target_nodes, target_ways, referenced_node_ids = _collect_targets(
        filename,
        primary_name,
        feature_name,
        multiprocess=multiprocess,
        block_descriptors=block_descriptors,
    )

    feature_label = _format_feature_descriptor((feature_name,))

    logger.info(
        "Region %s (%s=%s): identified %d target nodes, %d target ways",
        region_code,
        primary_name,
        feature_label,
        len(target_nodes),
        len(target_ways),
    )

    coordinate_nodes: Dict[int, Node] = dict(target_nodes)

    missing_node_ids = referenced_node_ids - set(coordinate_nodes.keys())
    if missing_node_ids:
        extra_nodes = _collect_nodes(
            filename,
            missing_node_ids,
            multiprocess=multiprocess,
            block_descriptors=block_descriptors,
        )
        if extra_nodes:
            coordinate_nodes.update(extra_nodes)
        unresolved = missing_node_ids - set(coordinate_nodes.keys())
        if unresolved:
            logger.warning(
                "Region %s (%s=%s): %d referenced nodes missing coordinates after collection",
                region_code,
                primary_name,
                feature_label,
                len(unresolved),
            )

    total_count = 0

    node_stage = 0
    for feature in _iter_node_rows(target_nodes, region_code):
        node_stage += 1
        total_count += 1
        if node_stage % PROGRESS_INTERVAL == 0:
            _log_stage_progress(
                region_code,
                primary_name,
                feature_label,
                stage="node",
                count=node_stage,
                total=total_count,
            )
        yield feature.to_dict()

    _log_stage_progress(
        region_code,
        primary_name,
    feature_label,
        stage="node",
        count=node_stage,
        total=total_count,
        final=True,
    )

    way_stage = 0
    for feature in _iter_way_rows(target_ways, coordinate_nodes, region_code):
        way_stage += 1
        total_count += 1
        if way_stage % PROGRESS_INTERVAL == 0:
            _log_stage_progress(
                region_code,
                primary_name,
                feature_label,
                stage="way",
                count=way_stage,
                total=total_count,
            )
        yield feature.to_dict()

    _log_stage_progress(
        region_code,
        primary_name,
        feature_label,
        stage="way",
        count=way_stage,
        total=total_count,
        final=True,
    )

    logger.info(
        "Region %s (%s=%s): streaming finished with %d features",
        region_code,
        primary_name,
        feature_label,
        total_count,
    )


def stream_pbf_features_multi(
    filename: str,
    primary_name: str,
    feature_names: Sequence[str],
    region_code: str,
    *,
    multiprocess: bool = False,
) -> Iterator[tuple[str, Dict[str, object]]]:
    normalized_features = _normalize_feature_names(feature_names)
    feature_label = _format_feature_descriptor(normalized_features)

    block_descriptors: Optional[Sequence[tuple[int, bytes]]] = None
    if multiprocess:
        block_descriptors = _prepare_block_descriptors(filename)

    target_nodes, target_ways, referenced_node_ids = _collect_targets(
        filename,
        primary_name,
        normalized_features,
        multiprocess=multiprocess,
        block_descriptors=block_descriptors,
    )

    logger.info(
        "Region %s (%s=%s): identified %d target nodes, %d target ways",
        region_code,
        primary_name,
        feature_label,
        len(target_nodes),
        len(target_ways),
    )

    coordinate_nodes: Dict[int, Node] = dict(target_nodes)

    missing_node_ids = referenced_node_ids - set(coordinate_nodes.keys())
    if missing_node_ids:
        extra_nodes = _collect_nodes(
            filename,
            missing_node_ids,
            multiprocess=multiprocess,
            block_descriptors=block_descriptors,
        )
        if extra_nodes:
            coordinate_nodes.update(extra_nodes)
        unresolved = missing_node_ids - set(coordinate_nodes.keys())
        if unresolved:
            logger.warning(
                "Region %s (%s=%s): %d referenced nodes missing coordinates after collection",
                region_code,
                primary_name,
                feature_label,
                len(unresolved),
            )

    total_count = 0

    node_stage = 0
    node_counts = {name: 0 for name in normalized_features}
    for feature in _iter_node_rows(target_nodes, region_code):
        matches = list(_iter_matching_features(feature.tags, primary_name, normalized_features))
        if not matches:
            continue

        row_dict = feature.to_dict()
        for match_index, match in enumerate(matches):
            payload = row_dict if match_index == 0 else row_dict.copy()
            node_counts[match] += 1
            node_stage += 1
            total_count += 1
            if node_stage % PROGRESS_INTERVAL == 0:
                _log_stage_progress(
                    region_code,
                    primary_name,
                    feature_label,
                    stage="node",
                    count=node_stage,
                    total=total_count,
                )
            yield match, payload

    _log_stage_progress(
        region_code,
        primary_name,
        feature_label,
        stage="node",
        count=node_stage,
        total=total_count,
        final=True,
    )

    way_stage = 0
    way_counts = {name: 0 for name in normalized_features}
    for feature in _iter_way_rows(target_ways, coordinate_nodes, region_code):
        matches = list(_iter_matching_features(feature.tags, primary_name, normalized_features))
        if not matches:
            continue

        row_dict = feature.to_dict()
        for match_index, match in enumerate(matches):
            payload = row_dict if match_index == 0 else row_dict.copy()
            way_counts[match] += 1
            way_stage += 1
            total_count += 1
            if way_stage % PROGRESS_INTERVAL == 0:
                _log_stage_progress(
                    region_code,
                    primary_name,
                    feature_label,
                    stage="way",
                    count=way_stage,
                    total=total_count,
                )
            yield match, payload

    _log_stage_progress(
        region_code,
        primary_name,
        feature_label,
        stage="way",
        count=way_stage,
        total=total_count,
        final=True,
    )

    for feature_name in normalized_features:
        logger.info(
            "Region %s (%s=%s -> %s): node rows=%d, way rows=%d, total=%d",
            region_code,
            primary_name,
            feature_label,
            feature_name,
            node_counts.get(feature_name, 0),
            way_counts.get(feature_name, 0),
            node_counts.get(feature_name, 0) + way_counts.get(feature_name, 0),
        )

    logger.info(
        "Region %s (%s=%s): streaming finished with %d features across %d values",
        region_code,
        primary_name,
        feature_label,
        total_count,
        len(normalized_features),
    )
def stream_region_features(
    region,
    primary_name: str,
    feature_name: str,
    data_dir: str,
    update: bool = False,
    progress_bar: bool = True,
    multiprocess: bool = True,
    data_source: str = "geofabrik",
) -> Iterator[Dict[str, object]]:
    """Yield flattened feature dictionaries for a region.

    Args:
        region: Region namedtuple as provided by :func:`gfk_data.get_region_tuple`.
        primary_name: Top-level OSM tag key (e.g. ``power``).
        feature_name: Tag value to filter for (e.g. ``line``). Values starting
            with ``ALL_`` act as wildcards and match any value for ``primary``.
        data_dir: Directory that holds cached PBF archives.
        update: When ``True`` the PBF archive is refreshed before processing.
        progress_bar: Forwarded to the downloader.
        multiprocess: Currently unused for streaming extraction. Included for
            API compatibility with the legacy pipeline.
        data_source: Must be ``geofabrik``; other values are unsupported.

    Yields:
        Dictionaries ready to be consumed by the export writers.
    """

    if data_source != "geofabrik":
        raise ValueError(
            "stream_region_features only supports data_source='geofabrik'"
        )

    pbf_url = region.urls["pbf"]
    logger.info(
        "Region %s (%s=%s): downloading %s",
        region.short,
        primary_name,
        feature_name,
        os.path.basename(pbf_url),
    )
    filename = download_region_pbf(region, update, data_dir, progress_bar=progress_bar)
    logger.debug(
        "Streaming PBF %s for region %s (primary=%s, feature=%s)",
        os.path.basename(filename),
        region.short,
        primary_name,
        feature_name,
    )
    yield from stream_pbf_features(
        filename,
        primary_name,
        feature_name,
        region.short,
        multiprocess=multiprocess,
    )


def _sanitize_cache_component(value: str) -> str:
    value = str(value)
    return "".join(char if char.isalnum() or char in ("-", "_", ".") else "_" for char in value)


def primary_cache_path(
    data_dir: str,
    region_code: str,
    primary_name: str,
    _pbf_filename: str,
) -> str:
    region_key = region_code or "unknown"
    cache_dir = os.path.join(data_dir, primary_name)
    return os.path.join(cache_dir, f"{region_key}_{primary_name}.jsonl")


def _feature_matches(row: Dict[str, object], primary_name: str, feature_name: str) -> bool:
    tag_key = f"tags.{primary_name}"
    value = row.get(tag_key)
    if value is None:
        return False
    return tag_value_matches(value, feature_name)


def _iter_primary_cache_rows(
    cache_path: str,
    primary_name: str,
    feature_name: str,
) -> Iterator[Dict[str, object]]:
    with open(cache_path, "r", encoding="utf-8") as source:
        for line in source:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if _feature_matches(row, primary_name, feature_name):
                yield row


def _build_primary_cache(
    filename: str,
    primary_name: str,
    feature_name: str,
    region_code: str,
    cache_path: str,
    *,
    multiprocess: bool,
) -> Iterator[Dict[str, object]]:
    temp_path = f"{cache_path}.tmp"
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    logger.info(
        "Region %s (%s=*): streaming PBF to build primary cache at %s",
        region_code,
        primary_name,
        cache_path,
    )

    with open(temp_path, "w", encoding="utf-8") as cache_file:
        try:
            for row in stream_pbf_features(
                filename,
                primary_name,
                f"ALL_{primary_name}",
                region_code,
                multiprocess=multiprocess,
            ):
                cache_file.write(json.dumps(row, ensure_ascii=False))
                cache_file.write("\n")
                if _feature_matches(row, primary_name, feature_name):
                    yield row
        except BaseException:
            cache_file.close()
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    os.replace(temp_path, cache_path)
    logger.info(
        "Region %s (%s=*): primary cache finalized at %s",
        region_code,
        primary_name,
        cache_path,
    )


def stream_cached_primary_features(
    filename: str,
    primary_name: str,
    feature_name: str,
    region_code: str,
    cache_path: str,
    *,
    multiprocess: bool = False,
    rebuild_cache: bool = False,
) -> Iterator[Dict[str, object]]:
    if rebuild_cache and os.path.exists(cache_path):
        os.remove(cache_path)

    needs_build = rebuild_cache or not os.path.exists(cache_path)

    if not needs_build:
        try:
            needs_build = os.path.getmtime(cache_path) < os.path.getmtime(filename)
        except FileNotFoundError:
            needs_build = True

    if needs_build:
        yield from _build_primary_cache(
            filename,
            primary_name,
            feature_name,
            region_code,
            cache_path,
            multiprocess=multiprocess,
        )
        return

    logger.info(
        "Region %s (%s=%s): streaming from cached primary snapshot %s",
        region_code,
        primary_name,
        feature_name,
        cache_path,
    )
    yield from _iter_primary_cache_rows(cache_path, primary_name, feature_name)


def stream_region_features_multi(
    region,
    primary_name: str,
    feature_names: Sequence[str],
    data_dir: str,
    update: bool = False,
    progress_bar: bool = True,
    multiprocess: bool = True,
    data_source: str = "geofabrik",
) -> Iterator[tuple[str, Dict[str, object]]]:
    """Yield feature-tagged rows for multiple features without primary caching."""

    normalized_features = _normalize_feature_names(feature_names)
    feature_label = _format_feature_descriptor(normalized_features)

    if data_source != "geofabrik":
        raise ValueError("Multi-feature streaming is only supported for the geofabrik data source")

    pbf_url = region.urls["pbf"]
    logger.info(
        "Region %s (%s=%s): downloading %s",
        region.short,
        primary_name,
        feature_label,
        os.path.basename(pbf_url),
    )
    filename = download_region_pbf(region, update, data_dir, progress_bar=progress_bar)
    logger.debug(
        "Streaming PBF %s for region %s (primary=%s, features=%s)",
        os.path.basename(filename),
        region.short,
        primary_name,
        feature_label,
    )

    yield from stream_pbf_features_multi(
        filename,
        primary_name,
        normalized_features,
        region.short,
        multiprocess=multiprocess,
    )
