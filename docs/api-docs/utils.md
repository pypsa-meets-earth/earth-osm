<!-- markdownlint-disable -->

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `utils`




**Global Variables**
---------------
- **primary_feature_element**

---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `lonlat_lookup`

```python
lonlat_lookup(df_way, primary_data)
```

Lookup refs and convert to list of longlats 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `way_or_area`

```python
way_or_area(df_way)
```






---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `convert_ways_points`

```python
convert_ways_points(df_way, primary_data)
```

Convert Ways to Point Coordinates 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L107"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `convert_ways_polygons`

```python
convert_ways_polygons(df_way, primary_data)
```

Convert Ways to Polygon and Point Coordinates 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L124"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `convert_ways_lines`

```python
convert_ways_lines(df_way, primary_data)
```

Convert Ways to Line Coordinates 



**Args:**
 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L146"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `tags_melt`

```python
tags_melt(df_exp, nan_threshold=0.75)
```






---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `columns_melt`

```python
columns_melt(df_exp, columns_to_move)
```






---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L184"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `tags_explode`

```python
tags_explode(df_melt)
```






---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L243"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `convert_pd_to_gdf`

```python
convert_pd_to_gdf(pd_df)
```






---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L270"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `write_csv`

```python
write_csv(df_feature, outputfile_partial, feature_name, out_aggregate, fn_name)
```

Create csv file. Optimized for large files as write on disk in chunks 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L284"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `write_geojson`

```python
write_geojson(
    gdf_feature,
    outputfile_partial,
    feature_name,
    out_aggregate,
    fn_name
)
```

Create geojson file. Optimized for large files as write on disk in chunks 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L298"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_list_slug`

```python
get_list_slug(str_list)
```






---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L406"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `output_creation`

```python
output_creation(
    df_feature,
    primary_name,
    feature_list,
    region_list,
    data_dir,
    out_format
)
```

Save Dataframe to disk Currently supports   CSV: Comma Separated Values  GeoJSON: GeoJSON format (including geometry) 



**Args:**
  df_feature 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L311"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OutFileWriter`




<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L313"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(region_list, feature_list, data_dir, out_format)
```









