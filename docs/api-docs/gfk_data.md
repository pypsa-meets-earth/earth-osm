<!-- markdownlint-disable -->

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/gfk_data.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `gfk_data`




**Global Variables**
---------------
- **pkg_data_dir**
- **sitemap**
- **f**
- **d**
- **row_list**
- **feature**

---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/gfk_data.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_geom_sitemap`

```python
get_geom_sitemap()
```






---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/gfk_data.py#L45"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_root_list`

```python
get_root_list()
```

Returns a list of regions without parents (i.e continents) 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/gfk_data.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_all_valid_list`

```python
get_all_valid_list()
```

Returns a list of all valid region ids 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/gfk_data.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_all_regions_dict`

```python
get_all_regions_dict(level=0)
```

It takes a level argument, and returns a dictionary of all regions, grouped by their parent region 



**Args:**
 
 - <b>`level`</b>:  0 = all regions, 1 = world regions, 2 = local regions, defaults to 0 A dictionary of dictionaries. 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/gfk_data.py#L84"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `view_regions`

```python
view_regions(level=0)
```

Takes the `all_regions` dictionary and returns a new dictionary with the same keys, but with the values being the `region_id`s of the regions 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/gfk_data.py#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_region_dict`

```python
get_region_dict(id)
```

Takes a region id (eg. germany) and returns a ditctionary consisting of strings 'id', 'name', 'parent', 'short_code' and dictionary of 'urls' Raises error if id is not found 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/gfk_data.py#L107"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_id_by_code`

```python
get_id_by_code(code)
```

Takes a region code (eg. DE) and returns its id (eg. germany) Supresses error if id is not found 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/gfk_data.py#L118"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_code_by_id`

```python
get_code_by_id(id)
```

Takes a region id (eg. germany) and returns its code (eg. DE) Supresses error if id is not found 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/gfk_data.py#L132"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_id_by_str`

```python
get_id_by_str(region_str)
```

Takes a region id or code (eg. DE, germany) and returns its id (eg. germany) Raises error if the string is not a valid id or code 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/gfk_data.py#L151"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_region_tuple`

```python
get_region_tuple(region_str)
```

Takes a region id or code (eg. DE, germany) and returns a named tuple with  'id', 'name', 'short', 'parent', 'short_code' and dictionary of 'urls' The 'short' field is an iso code if found otherwise the id is used. iso3166-1:alpha2 is used for countries, iso3166-2 is used for sub-divisions Raises error if the string is not a valid id or code 


