__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""OSMPBF file reader.

This module provides a reader for OpenStreetMap PBF files.

Modified from esy-osm-pbf/file.py

"""

import struct
import zlib
from itertools import accumulate

from . import Node, Relation, Way, fileformat_pb2, osmformat_pb2


def decode_strmap(primitive_block):
    """
    Decode the string table from a primitive block into a list of strings.
    """

    return tuple(s.decode('utf8') for s in primitive_block.stringtable.s)


def iter_blocks(file):
    """
    Iterate over the blocks in a OpenStreetMap PBF file.
    """

    ofs = 0
    while True:
        file.seek(ofs)
        data = file.read(4)
        if len(data) < 4:
            return
        header_size, = struct.unpack('>I', data)
        header = fileformat_pb2.BlobHeader()
        header.ParseFromString(file.read(header_size))
        ofs += 4 + header_size
        yield ofs, header
        ofs += header.datasize


def read_blob(file, ofs, header):
    """
    Read a blob from a OpenStreetMap PBF file.
    """

    file.seek(ofs)
    blob = fileformat_pb2.Blob()
    blob.ParseFromString(file.read(header.datasize))
    if blob.raw:
        return blob.raw
    elif blob.zlib_data:
        return zlib.decompress(blob.zlib_data)
    else:
        raise ValueError('Unknown blob type')


def parse_tags(strmap, keys_vals):
    """
    Parse the tags from a OpenStreetMap PBF file.
    """

    tags = {}
    is_value = False
    for idx in keys_vals:
        if idx == 0:
            yield tags
            tags = {}
        elif is_value:
            tags[key] = strmap[idx]
            is_value = False
        else:
            key = strmap[idx]
            is_value = True


def iter_primitive_block(primitive_block):
    """
    Iterate over the elements in a primitive block.
    """

    strmap = decode_strmap(primitive_block)
    for group in primitive_block.primitivegroup:
        for id, tags, lonlat in iter_nodes(primitive_block, strmap, group):
            yield Node(id, tags, lonlat)

        for id, refs, tags in iter_ways(primitive_block, strmap, group):
            yield Way(id, tags, refs)

        for id, members, tags in iter_relations(primitive_block, strmap, group):
            yield Relation(id, tags, members)


def iter_nodes(block, strmap, group):
    dense = group.dense
    if not dense:
        raise ValueError('Only dense nodes are supported')
    granularity = block.granularity or 100
    lat_offset = block.lat_offset or 0
    lon_offset = block.lon_offset or 0
    coord_scale = 0.000000001
    id = lat = lon = tag_pos = 0
    for did, dlat, dlon, tags in zip(
            dense.id, dense.lat, dense.lon,
            parse_tags(strmap, dense.keys_vals)):
        id += did
        lat += coord_scale * (lat_offset + granularity * dlat)
        lon += coord_scale * (lon_offset + granularity * dlon)
        yield (id, tags, (lon, lat))


def iter_ways(block, strmap, group):
    for way in group.ways:
        tags = {strmap[k]: strmap[v] for k, v in zip(way.keys, way.vals)}
        refs = tuple(accumulate(way.refs))
        yield way.id, refs, tags


def iter_relations(block, strmap, group):
    namemap = {}
    for relation in group.relations:
        tags = {
            strmap[k]: strmap[v] for k, v in zip(relation.keys, relation.vals)
        }
        refs = tuple(accumulate(relation.memids))
        members = [
            (
                ref,
                namemap.setdefault(
                    rel_type, osmformat_pb2.Relation.MemberType.Name(rel_type)
                ),
                strmap[sid],
            )
            for ref, rel_type, sid in zip(
                refs, relation.types, relation.roles_sid
            )
        ]

        yield relation.id, members, tags
