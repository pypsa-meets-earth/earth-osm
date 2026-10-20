"""Tests for the multiprocessing option (see issue #82).

Covers the ``--mp [N]`` CLI switch, the ``resolve_worker_count`` helper shared
by the extraction pipelines, and the plumbing that pins the worker count of the
underlying multiprocessing pools.
"""

import multiprocessing

import pytest

from earth_osm import args as args_module
from earth_osm import extract, stream


class TestResolveWorkerCount:
    def test_disabled_uses_single_process(self):
        assert extract.resolve_worker_count(False) == 1
        assert extract.resolve_worker_count(None) == 1

    def test_auto_matches_historic_default(self):
        expected = max(1, multiprocessing.cpu_count() - 1 or 1)
        assert extract.resolve_worker_count(True) == expected

    @pytest.mark.parametrize("processes", [1, 2, 4, 17, 512])
    def test_explicit_count_is_pinned(self, processes):
        assert extract.resolve_worker_count(processes) == processes

    @pytest.mark.parametrize("processes", [0, -1, -100])
    def test_non_positive_count_is_rejected(self, processes):
        with pytest.raises(ValueError):
            extract.resolve_worker_count(processes)


class _FakePool:
    """Records the process count a pool would have been created with."""

    def __init__(self, processes=None):
        self.processes = processes

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def starmap(self, func, iterable):
        return []


def _patch_pool(monkeypatch):
    captured = {}

    def fake_pool(processes=None):
        captured["processes"] = processes
        return _FakePool(processes)

    monkeypatch.setattr(extract.mp, "Pool", fake_pool)
    monkeypatch.setattr(extract, "iter_blocks", lambda file: iter(()))
    return captured


class TestFilterPbfWorkerCount:
    def test_explicit_count_is_honoured(self, monkeypatch, tmp_path):
        captured = _patch_pool(monkeypatch)

        pbf_file = tmp_path / "empty.osm.pbf"
        pbf_file.write_bytes(b"")

        result = extract.filter_pbf(str(pbf_file), {}, 3)

        assert captured["processes"] == 3
        assert result == {"Node": {}, "Way": {}, "Relation": {}}

    def test_disabled_uses_single_process(self, monkeypatch, tmp_path):
        captured = _patch_pool(monkeypatch)

        pbf_file = tmp_path / "empty.osm.pbf"
        pbf_file.write_bytes(b"")

        extract.filter_pbf(str(pbf_file), {}, False)

        assert captured["processes"] == 1

    def test_auto_matches_cpu_count(self, monkeypatch, tmp_path):
        captured = _patch_pool(monkeypatch)

        pbf_file = tmp_path / "empty.osm.pbf"
        pbf_file.write_bytes(b"")

        extract.filter_pbf(str(pbf_file), {}, True)

        assert captured["processes"] == max(1, multiprocessing.cpu_count() - 1 or 1)


class TestStreamWorkerCountPlumbing:
    def test_collect_targets_pins_worker_count(self, monkeypatch):
        captured = {}

        def fake_parallel(
            filename, primary_name, feature_names, block_descriptors, worker_count
        ):
            captured["worker_count"] = worker_count
            return {}, [], set()

        monkeypatch.setattr(stream, "_collect_targets_parallel", fake_parallel)
        monkeypatch.setattr(stream, "_prepare_block_descriptors", lambda filename: [])

        result = stream._collect_targets("dummy.osm.pbf", "power", ["line"], multiprocess=5)

        assert captured["worker_count"] == 5
        assert result == ({}, [], set())

    def test_collect_targets_falls_back_to_sequential(self, monkeypatch):
        sequential_called = []

        def fake_sequential(filename, primary_name, feature_names):
            sequential_called.append(True)
            return {}, [], set()

        monkeypatch.setattr(stream, "_collect_targets_sequential", fake_sequential)

        result = stream._collect_targets(
            "dummy.osm.pbf", "power", ["line"], multiprocess=False
        )

        assert sequential_called == [True]
        assert result == ({}, [], set())

    def test_collect_nodes_pins_worker_count(self, monkeypatch):
        captured = {}

        def fake_parallel(filename, required_node_ids, block_descriptors, worker_count):
            captured["worker_count"] = worker_count
            return {}

        monkeypatch.setattr(stream, "_collect_nodes_parallel", fake_parallel)
        monkeypatch.setattr(stream, "_prepare_block_descriptors", lambda filename: [])

        result = stream._collect_nodes("dummy.osm.pbf", {1, 2, 3}, multiprocess=2)

        assert captured["worker_count"] == 2
        assert result == {}


def _parse_extract(argv):
    parser = args_module.setup_parser()
    return parser.parse_args(["extract", "power", "--regions", "malta", *argv])


class TestMpCliOption:
    def test_default_keeps_historic_behaviour(self):
        args = _parse_extract([])
        assert args.mp is None
        assert args.no_mp is False

    def test_no_mp_disables_multiprocessing(self):
        args = _parse_extract(["--no_mp"])
        assert args.no_mp is True
        assert args.mp is None

    def test_bare_mp_keeps_auto_behaviour(self):
        args = _parse_extract(["--mp"])
        assert args.mp is True
        assert args.no_mp is False

    @pytest.mark.parametrize("value", ["1", "2", "8", "64"])
    def test_mp_accepts_process_count(self, value):
        args = _parse_extract(["--mp", value])
        assert args.mp == int(value)

    @pytest.mark.parametrize("value", ["0", "-3", "abc", "1.5", ""])
    def test_mp_rejects_invalid_process_count(self, value):
        with pytest.raises(SystemExit):
            _parse_extract(["--mp", value])

    def test_mp_and_no_mp_are_mutually_exclusive(self):
        with pytest.raises(SystemExit):
            _parse_extract(["--mp", "--no_mp"])
