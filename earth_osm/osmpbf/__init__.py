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

Relation = namedtuple('Relation', ('id', 'tags', 'members'))
"""
A OpenStreetMap `relation <https://wiki.openstreetmap.org/wiki/Relation>

id: int (relation id)
tags: dict (tag names -> tag values)
members: tuple (ref, member_type, role)
    where:
        member_type: str (Node, way, or Relation)
        role: str (role of the member)
"""
