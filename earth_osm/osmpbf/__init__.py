from collections import namedtuple

Node = namedtuple('Node', ('id', 'tags', 'lonlat'))
"""
A OpenStreetMap `node <https://wiki.openstreetmap.org/wiki/Node>

id: int (node id)
tags: dict (tag names -> tag values)
lonlat: tuple (lon, lat)
"""


