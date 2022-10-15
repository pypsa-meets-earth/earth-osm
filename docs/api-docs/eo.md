<!-- markdownlint-disable -->

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/eo.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `eo`




**Global Variables**
---------------
- **primary_feature_element**

---

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/eo.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `process_country`

```python
process_country(region, primary_name, feature_name, mp, update, data_dir)
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

<a href="https://github.com/pypsa-meets-earth/earth-osm/blob/main/earth_osm/eo.py#L73"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_osm_data`

```python
get_osm_data(
    region_list=['germany'],
    primary_name='power',
    feature_list=['tower'],
    update=False,
    mp=True,
    data_dir='/home/matin/earth-osm/earth_data'
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


