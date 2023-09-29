<!-- markdownlint-disable -->

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/extract.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `extract`





---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/extract.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `primary_entry_filter`

```python
primary_entry_filter(entry, pre_filter)
```






---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/extract.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `id_filter`

```python
id_filter(entry, idset)
```






---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/extract.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `way_filter`

```python
way_filter(entry, way_relation_members)
```






---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/extract.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `filter_file_block`

```python
filter_file_block(filename, ofs, header, filter_func, args, kwargs)
```






---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/extract.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `pool_file_query`

```python
pool_file_query(filename, pool)
```

returns query function that accepts a filter function and returns a list of filtered entries 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/extract.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `filter_pbf`

```python
filter_pbf(filename, pre_filter, multiprocess=True)
```

Parallized pre-Filtering of OSM file by a pre_filter 



**Args:**
 
 - <b>`filename`</b>:    PBF file 
 - <b>`pre_filter`</b>:  dict of dicts in the following format: { 
 - <b>`Node`</b>:  {primary_name: feature_list},  
 - <b>`Way`</b>:  {primary_name: feature_list}, 
 - <b>`Relation`</b>:  {primary_name: feature_list}} 



**Returns:**
 
 - <b>`targetname`</b>:  JSON-file 


