from collections import namedtuple

Node = namedtuple('Node', ('id', 'tags', 'lonlat'))
"""
A OpenStreetMap `node <https://wiki.openstreetmap.org/wiki/Node>

id: int (node id)
tags: dict (tag names -> tag values)
lonlat: tuple (lon, lat)
"""

Way = namedtuple('Way', ('id', 'tags', 'refs'))
"""
A OpenStreetMap `way <https://wiki.openstreetmap.org/wiki/Way>

id: int (way id)
tags: dict (tag names -> tag values)
refs: list (node ids)
"""

