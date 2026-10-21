__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Extract OSM from PBF Files

This module extracts OSM data from PBF files.

Modified from esy-osmfilter/pre_filter.py

"""

import itertools
import logging
import multiprocessing as mp

from earth_osm.osmpbf import Node, Relation, Way, osmformat_pb2
from earth_osm.osmpbf.file import iter_blocks, iter_primitive_block, read_blob
from earth_osm.utils import tag_value_matches

logger = logging.getLogger("eo.extract")
logger.setLevel(logging.INFO)


def primary_entry_filter(entry, pre_filter):
    filtermap = pre_filter[type(entry)]  # {"power": ['line', 'tower]}
    for primary_name, feature_names in filtermap.items():
        value = entry.tags.get(primary_name)
        if value is None:
            continue
        for feature_name in feature_names:
            if tag_value_matches(value, feature_name):
                return True
    return False


def id_filter(entry, idset):
    return entry.id in idset


def way_filter(entry, way_relation_members):
    return isinstance(entry, Way) and entry.id in way_relation_members


def filter_file_block(filename, ofs, header, filter_func, args, kwargs):
    with open(filename, "rb") as file:
        entries = osmformat_pb2.PrimitiveBlock()
        entries.ParseFromString(read_blob(file, ofs, header))
        return [
            entry
            for entry in iter_primitive_block(entries)
            if filter_func(entry, *args, **kwargs)
        ]


def pool_file_query(filename, pool):
    """
    returns query function that accepts a filter function and returns a list of filtered entries
    """
    with open(filename, "rb") as file:
        blocks = [(file.name, ofs, header) for ofs, header in iter_blocks(file)]

    def query_func(filter_func, *args, **kwargs):
        entry_lists = pool.starmap(
            filter_file_block,
            [block + (filter_func, args, kwargs) for block in blocks],
        )
        
        return itertools.chain(*(entries for entries in entry_lists))

    return query_func


def resolve_worker_count(multiprocess):
    """Resolve the number of worker processes for a multiprocessing setting.

    Args:
        multiprocess: ``True`` to use all CPUs but one (historic default),
            ``False`` to disable multiprocessing, or a positive integer
            to pin the number of worker processes.

    Returns:
        Number of processes a multiprocessing.Pool should use.

    Raises:
        ValueError: If an integer below 1 is passed.
    """
    if multiprocess is True:
        return max(1, mp.cpu_count() - 1 or 1)
    if multiprocess is False or multiprocess is None:
        return 1
    worker_count = int(multiprocess)
    if worker_count < 1:
        raise ValueError(f"number of processes must be >= 1, got {worker_count}")
    return worker_count


def filter_pbf(filename, pre_filter, multiprocess=True):
    """
    Parallized pre-Filtering of OSM file by a pre_filter

    Args:
        filename:   PBF file
        pre_filter: dict of dicts in the following format: {
                Node: {primary_name: feature_list}, 
                Way: {primary_name: feature_list},
                Relation: {primary_name: feature_list}}
        multiprocess: ``True`` to use all CPUs but one, ``False`` to run
            single-process, or a positive integer to pin the number of
            worker processes (see :func:`resolve_worker_count`)

    Returns:
        targetname: JSON-file
    """

    with mp.Pool(processes=resolve_worker_count(multiprocess)) as pool:
        file_query = pool_file_query(filename, pool)    
        primary_entries = list(file_query(primary_entry_filter, pre_filter)) #list of named  tuples eg. Node(id,tags, lonlat)
        
        node_relation_members = set()
        way_relation_members = set()
        way_refs = set()
        relation_way_node_members = set()
        
        for entry in primary_entries:
            if isinstance(entry, Relation):
                for id, typename, role in entry.members:
                    if typename == "NODE":
                        node_relation_members.add(id)
                    elif typename == "WAY":
                        way_relation_members.add(id)
            
            if isinstance(entry, Way):
                way_refs.update(entry.refs)

        way_entries = list(file_query(way_filter, way_relation_members))

        for entry in way_entries:
            relation_way_node_members.update(entry.refs)

        primary_entries.extend(
            file_query(
                id_filter,
                set.union(
                    node_relation_members,
                    way_refs,
                    way_relation_members,
                    relation_way_node_members,
                ),
            )
        )

        primary_entries.sort(key=lambda entry: entry.id)
        
        primary_data = {"Node": {}, "Way": {}, "Relation": {}}
        for entry in primary_entries:
            primary_data[type(entry).__name__][str(entry.id)] = dict(entry._asdict())
    
    return primary_data
