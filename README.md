# earth-osm 
<p align="left"> 
by
<a href="https://pypsa-meets-earth.github.io">
    <img src="https://github.com/pypsa-meets-earth/pypsa-meets-earth.github.io/raw/main/assets/img/logo.png" width="150">
<a/>
</p>

[![PyPI version](https://img.shields.io/pypi/v/earth-osm.svg)](https://pypi.org/project/earth-osm/)
[![CI](https://github.com/pypsa-meets-africa/earth-osm/actions/workflows/main.yml/badge.svg)](https://github.com/pypsa-meets-africa/earth-osm/actions/workflows/main.yml)
![Size](https://img.shields.io/github/repo-size/pypsa-meets-earth/earth-osm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Discord](https://img.shields.io/discord/911692131440148490?logo=discord)](https://discord.gg/AnuJBk23FU)

earth-osm is a free software tool that can extract large-amounts of OpenStreetMap data. It implements filters and multi-processing for fast and memory-efficient computations. You can extract e.g. power lines for the whole Africa on your laptop. It builds on esy-osmfilter and improves its package design, usability and performance.

## Getting Started
Install earth-osm
```bash
pip install git+https://github.com/pypsa-meets-earth/earth-osm.git
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

  **--update** (*optional*, update existing data, dafult False)

  **--mp** (*optional*, use multiprocessing, default True)
  
  **--data_dir** (*optional*, path to data directory, default './earth_data')
                      

## Advanced Usage

```py
import earth_osm as eo

eo.get_osm_data(
  primary_name = 'power',
  region_list = ['benin', 'monaco'],
  feature_list = ['substation', 'line'],
  update = False,
  mp = True,
  data_dir = './earth_data',
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
