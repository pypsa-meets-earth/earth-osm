<!-- markdownlint-disable -->

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `utils`




**Global Variables**
---------------
- **primary_feature_element**

---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `lonlat_lookup`

```python
lonlat_lookup(df_way, primary_data)
```

Lookup refs and convert to list of longlats 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `convert_ways_points`

```python
convert_ways_points(df_way, primary_data)
```

Convert Ways to Point Coordinates 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L77"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `convert_ways_lines`

```python
convert_ways_lines(df_way, primary_data)
```

Convert Ways to Line Coordinates 



**Args:**
 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `convert_pd_to_gdf_nodes`

```python
convert_pd_to_gdf_nodes(df_way)
```

Convert Nodes Pandas Dataframe to GeoPandas Dataframe 



**Args:**
 
 - <b>`df_way`</b>:  Pandas Dataframe 



**Returns:**
 GeoPandas Dataframe 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L113"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `convert_pd_to_gdf_lines`

```python
convert_pd_to_gdf_lines(df_way)
```

Convert Lines Pandas Dataframe to GeoPandas Dataframe 



**Args:**
 
 - <b>`df_way`</b>:  Pandas Dataframe 



**Returns:**
 GeoPandas Dataframe 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/utils.py#L130"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `output_csv_geojson`

```python
output_csv_geojson(
    df_feature,
    primary_name,
    feature_name,
    region_list,
    data_dir
)
```

Output CSV and GeoJSON files for each region 



**Args:**
 
 - <b>`df_feature`</b>:  _description_ 
 - <b>`primary_name`</b>:  _description_ 
 - <b>`feature_name`</b>:  _description_ 
 - <b>`region_list`</b>:  _description_ 


