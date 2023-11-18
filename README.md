<p align="center"> 
<a href="https://pypsa-meets-earth.github.io/earth-osm/">
    <img src="https://github.com/pypsa-meets-earth/pypsa-meets-earth.github.io/raw/main/assets/img/logo.png" height="50">
<a/>
</p>

# earth-osm. Python tool to extract large-amounts of OpenStreetMap data 


[![PyPI version](https://img.shields.io/pypi/v/earth-osm.svg)](https://pypi.org/project/earth-osm/)
[![Conda version](https://img.shields.io/conda/vn/conda-forge/earth-osm.svg)](https://anaconda.org/conda-forge/earth-osm)
[![codecov](https://codecov.io/gh/pypsa-meets-earth/earth-osm/branch/main/graph/badge.svg?token=ZS4PC5T4S8)](https://codecov.io/gh/pypsa-meets-earth/earth-osm)
[![CI](https://github.com/pypsa-meets-africa/earth-osm/actions/workflows/main.yml/badge.svg)](https://github.com/pypsa-meets-africa/earth-osm/actions/workflows/main.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Discord](https://img.shields.io/discord/911692131440148490?logo=discord)](https://discord.gg/AnuJBk23FU)
[![Docs](https://github.com/pypsa-meets-earth/earth-osm/actions/workflows/docs-ci.yml/badge.svg)](https://pypsa-meets-earth.github.io/earth-osm/)

earth-osm is a python package that provides an end-to-end solution to extract & standardize **power infrastructure** data from OpenStreetmap (OSM).

## Features
* Extracts power infrastructure data from OSM
* Cleans and Standardizes the data *(coming soon)*
* No API rate limits (data served from GeoFabrik)
* Provides a Python API
* Supports multiprocessing
* Outputs .csv and .geojson files
* Aggregate data per feature or per region
* Easy to use CLI interface

## Getting Started
Install earth-osm with pip:
```bash
pip install earth-osm
```
Or with conda:
```bash
conda install --channel=conda-forge earth-osm
```
Extract osm data
```bash
# Example CLI command
earth_osm extract power --regions benin monaco  --features substation line
```
This will extract
*primary feature = power* for the *regions = benin* and *monaco* and the *secondary features = substation* and *line*.
By default the resulting .csv and .geojson are stored in `./earth_data/out`

Load the substation data for benin using pandas
```bash
# For Pandas
df_substations = pd.read_csv('./earth_data/out/BJ_raw_substations.csv')
# For GeoPandas
gdf_substations = gpd.read_file('./earth_data/out/BJ_raw_substations.geojson')
```

## Other Arguments
usage: earth_osm extract **primary** **--regions** region1, region2 **--features** feature1, feature2 **--data_dir** DATA_DIR [**--update**] [**--mp**] 

  **primary** (e.g power, water, road, etc) NOTE: currently only power is supported

  **--regions** region1 region2 ... (use either iso3166-1:alpha2 or iso3166-2 codes or full names as given by running 'earth_osm view regions')

  **--features** feature1 feature2 ... (*optional*, use sub-features of primary feature, e.g. substation, line, etc)

  **--update** (*optional*, update existing data, default False)

  **--mp** (*optional*, use multiprocessing, default True)
  
  **--data_dir** (*optional*, path to data directory, default './earth_data')
  
  **--out_format** (*optional*, export format options csv or geojson, default csv)
  
  **--out_aggregate** (*options*, combine outputs per feature, default False)

## Advanced Usage

```py
import earth_osm as eo

eo.save_osm_data(
  primary_name = 'power',
  region_list = ['benin', 'monaco'],
  feature_list = ['substation', 'line'],
  update = False,
  mp = True,
  data_dir = './earth_data',
  out_format = ['csv', 'geojson'],
  out_aggregate = False,
)
```

## Development

(Optional) Intstall a specific version of earth_osm
```
pip install git+https://github.com/pypsa-meets-earth/earth-osm.git@<required-commit-hash>
```

(Optional) Create a virtual environment for python>=3.10 
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
```bash
pip install git+https://github.com/pypsa-meets-earth/earth-osm.git
pip install -r requirements-test.txt 
```
