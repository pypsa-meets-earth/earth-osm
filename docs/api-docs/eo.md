<!-- markdownlint-disable -->

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/eo.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `eo`





---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/eo.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `process_region`

```python
process_region(region, primary_name, feature_name, mp, update, data_dir)
```

Process Country 



**Args:**
 
 - <b>`region`</b>:  Region object 
 - <b>`primary_name`</b>:  Primary Feature Name 
 - <b>`feature_name`</b>:  Feature Name 
 - <b>`mp`</b>:  Multiprocessing object 
 - <b>`update`</b>:  Update flag 



**Returns:**
 None 


---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/eo.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_osm_data`

```python
get_osm_data(region_str, primary_name, feature_name, cached)
```






---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/eo.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `save_osm_data`

```python
save_osm_data(
    region_list=['germany'],
    primary_name='power',
    feature_list=['tower'],
    update=False,
    mp=True,
    data_dir='/home/matin/Projects/earth-osm/earth_data',
    out_format='csv',
    out_aggregate=True
)
```

Get OSM Data for a list of regions and features 

**args:**
 
 - <b>`region_list`</b>:  list of regions to get data for 
 - <b>`primary_name`</b>:  primary feature to get data for 
 - <b>`feature_list`</b>:  list of features to get data for 
 - <b>`update`</b>:  update data 
 - <b>`mp`</b>:  use multiprocessing 

**returns:**
 dict of dataframes 


