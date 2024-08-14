<h1 align="center">earth-osm</h1>
<p align="center">Extract Infrastructure data from OpenStreetMap</p>

<p align="center">
<a href="https://anaconda.org/conda-forge/earth-osm"><img src="https://img.shields.io/conda/dn/conda-forge/earth-osm" alt="Conda Downloads"></a>
<a href="https://pypi.org/project/earth-osm/"><img src="https://img.shields.io/pypi/v/earth-osm.svg" alt="PyPI version"></a>
<a href="https://anaconda.org/conda-forge/earth-osm"><img src="https://img.shields.io/conda/vn/conda-forge/earth-osm.svg" alt="Conda version"></a>
<a href="https://codecov.io/gh/pypsa-meets-earth/earth-osm"><img src="https://codecov.io/gh/pypsa-meets-earth/earth-osm/branch/main/graph/badge.svg?token=ZS4PC5T4S8" alt="codecov"></a>
<a href="https://github.com/pypsa-meets-africa/earth-osm/actions/workflows/main.yml"><img src="https://github.com/pypsa-meets-africa/earth-osm/actions/workflows/main.yml/badge.svg" alt="CI"></a>
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
<a href="https://discord.gg/AnuJBk23FU"><img src="https://img.shields.io/discord/911692131440148490?logo=discord" alt="Discord"></a>
<a href="https://pypsa-meets-earth.github.io/earth-osm/"><img src="https://github.com/pypsa-meets-earth/earth-osm/actions/workflows/docs-ci.yml/badge.svg" alt="Docs"></a>
</p>

## 📚 Overview

earth-osm downloads, filters, cleans and exports infrastructure data from OpenStreetMap (OSM). It provides a Python API and a CLI interface to extract data for various infrastructure types, such as power lines, substations, and more.

## 🌟 Key Features

- 🔌 Extracts infrastructure data from OSM
- 🧹 Cleans and standardizes the data *(coming soon)*
- 🚀 No API rate limits (data served from GeoFabrik)
- 🐍 Provides a Python API
- 🖥️ Supports multiprocessing for faster extraction
- 📊 Outputs data in .csv and .geojson formats
- 🌍 Supports global data extraction
- 🖱️ Easy-to-use CLI interface

## 🚀 Getting Started

### Installation

Install earth-osm using pip (recommended):

```bash
pip install earth-osm
```

Or with conda:

```bash
conda install --channel=conda-forge earth-osm
```

### Basic Usage

Extract OSM data using the CLI:

```bash
earth_osm extract power --regions benin monaco --features substation line
```

This command extracts power infrastructure data for Benin and Monaco, focusing on substations and power lines. By default, the resulting .csv and .geojson files are stored in `./earth_data/out`.

Load the extracted data using pandas:

```python
import pandas as pd
import geopandas as gpd

# For Pandas
df_substations = pd.read_csv('./earth_data/out/BJ_raw_substations.csv')

# For GeoPandas
gdf_substations = gpd.read_file('./earth_data/out/BJ_raw_substations.geojson')
```

## 🛠️ CLI Reference

### Extract Command

```bash
earth_osm extract <primary> --regions <region1> <region2> ... [options]
```

#### Arguments:

- `<primary>`: Primary feature to extract (e.g power)

#### Required Options:

- `--regions`: Specify one or more regions using ISO 3166-1 alpha-2, ISO 3166-2 codes, or full names

#### Optional Arguments:

| Argument | Description | Default |
|----------|-------------|---------|
| `--features` | Specify sub-features of the primary feature | All features |
| `--update` | Update existing data | False |
| `--no_mp` | Disable multiprocessing | False (MP enabled) |
| `--data_dir` | Path to data directory | './earth_data' |
| `--out_dir` | Path to output directory | Same as data_dir |
| `--out_format` | Export format(s): csv and/or geojson | ['csv', 'geojson'] |
| `--agg_feature` | Aggregate outputs by feature | False |
| `--agg_region` | Aggregate outputs by region | False |

## 🐍 Python API

For more advanced usage, you can use the Python API:

```python
import earth_osm as eo

eo.save_osm_data(
    primary_name='power',
    region_list=['benin', 'monaco'],
    feature_list=['substation', 'line'],
    update=False,
    mp=True,
    data_dir='./earth_data',
    out_format=['csv', 'geojson'],
    out_aggregate=False,
)
```

## 🛠️ Development

To contribute to earth-osm, follow these steps:

1. (Optional) Install a specific version of earth_osm:
   ```bash
   pip install git+https://github.com/pypsa-meets-earth/earth-osm.git@<required-commit-hash>
   ```

2. (Optional) Create a virtual environment for Python >=3.10:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the development dependencies:
   ```bash
   pip install git+https://github.com/pypsa-meets-earth/earth-osm.git
   pip install -r requirements-test.txt
   ```

4. Read the [CONTRIBUTING.md](CONTRIBUTING.md) file for more detailed information on how to contribute to the project.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Community

Join our [Discord community](https://discord.gg/AnuJBk23FU) to connect with other users and contributors, ask questions, and get support.

## 📚 Documentation

For more detailed information, check out our [full documentation](https://pypsa-meets-earth.github.io/earth-osm/).

---

<p align="center">
Made with ❤️ by the PyPSA meets Earth team
</p>

<p align="center"> 
<a href="https://pypsa-meets-earth.github.io/earth-osm/">
    <img src="https://github.com/pypsa-meets-earth/pypsa-meets-earth.github.io/raw/main/assets/img/logo.png" height="50" alt="earth-osm logo">
</a>
</p>