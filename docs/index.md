---
title: Home
description: Extract large-scale OpenStreetMap infrastructure data with Python
hide:
  - navigation
---

<div align="center" markdown=1>

# Earth-OSM
**Extract large-scale OpenStreetMap infrastructure data with Python**

[![][badge-pypi-monthly-downloads]][pypi-url]
[![][badge-codecov]][codecov-url]
[![][badge-ci]][gh-repo-url]
[![][badge-docs]][docs-url]
[![][badge-pypi]][pypi-url]
[![][badge-conda]][conda-url]
[![][badge-release]][gh-release-url]
[![][badge-license]][license]
[![][badge-discord]][discord-url]

</div>

## 🚀 Quick Start

### Installation

=== "pip"
    ```bash
    pip install earth-osm
    ```

=== "conda"
    ```bash
    conda install --channel=conda-forge earth-osm
    ```

### Basic Usage

=== "Command Line"
    ```bash
    earth_osm extract power --regions monaco --features substation line
    ```

=== "Python API"
    ```python
    import earth_osm as eo
    
    eo.save_osm_data(
        primary_name='power',
        region_list=['monaco'],
        feature_list=['substation', 'line']
    )
    ```

### Load Results

=== "Pandas"
    ```python
    import pandas as pd
    df = pd.read_csv('./earth_data/out/MC_substation.csv')
    ```

=== "GeoPandas"
    ```python
    import geopandas as gpd
    gdf = gpd.read_file('./earth_data/out/MC_substation.geojson')
    ```

## 🌟 Key Features

<div class="grid cards" markdown>

-   :material-flash:{ .lg .middle } __Fast Extraction__
    
    ---
    
    No API rate limits - data served from GeoFabrik mirrors
    
    [:octicons-arrow-right-24: Getting Started](user-guide/getting-started.md)

-   :material-earth:{ .lg .middle } __Global Coverage__
    
    ---
    
    Support for 200+ regions worldwide with comprehensive infrastructure data
    
    [:octicons-arrow-right-24: Supported Regions](regions.md)

-   :material-cog:{ .lg .middle } __Multiple Formats__
    
    ---
    
    Export to CSV, GeoJSON, and other formats for seamless integration
    
    [:octicons-arrow-right-24: Basic Usage](user-guide/basic-usage.md)

-   :material-chart-line:{ .lg .middle } __Rich Visualizations__
    
    ---
    
    Built-in plotting capabilities with examples for common use cases
    
    [:octicons-arrow-right-24: Visualization Guide](user-guide/visualization.md)

</div>

## 🛠️ Infrastructure Types

Earth-OSM supports extraction of various infrastructure types:

| Type | Description | Example Features |
|------|-------------|------------------|
| **Power** | Electrical infrastructure | `substation`, `line`, `generator`, `tower` |
| **Railway** | Rail transport | `rail`, `station`, `platform`, `signal` |
| **Highway** | Road infrastructure | `primary`, `secondary`, `trunk`, `motorway` |
| **Waterway** | Water infrastructure | `river`, `canal`, `dam`, `weir` |
| **Building** | Built environment | `residential`, `commercial`, `industrial` |
| **And more...** | 20+ infrastructure types | `amenity`, `boundary`, `leisure`, etc. |

## 🎯 Use Cases

<div class="grid cards" markdown>

-   **Energy System Analysis**
    
    Extract power grids for energy modeling with PyPSA, PowerSystemsX, and similar tools

-   **Transportation Planning**
    
    Analyze road and rail networks for logistics and urban planning applications

-   **Infrastructure Research**
    
    Academic research on infrastructure patterns, coverage, and development

-   **Geospatial Analysis**
    
    Spatial analysis and visualization of infrastructure data with standard GIS tools

</div>

## 📊 Example: Power Infrastructure Analysis

Let's extract and visualize power substations in Monaco:

```python
from earth_osm.eo import save_osm_data
import geopandas as gpd
import matplotlib.pyplot as plt

# Extract power infrastructure for Monaco
save_osm_data(
    region_list=['monaco'],
    primary_name='power',
    out_dir='./earth_data'
)

# Load and visualize
substations = gpd.read_file('./earth_data/out/MC_substation.geojson')
generators = gpd.read_file('./earth_data/out/MC_generator.geojson')

fig, ax = plt.subplots(figsize=(12, 8))
generators.plot(ax=ax, color='green', markersize=60, alpha=0.8, label='Generators')
substations.plot(ax=ax, color='red', markersize=100, alpha=0.8, label='Substations', marker='s')
ax.set_title('Monaco Power Infrastructure')
ax.legend()
plt.show()
```

### Visualization Results

![Monaco Power Infrastructure](generated-examples/images/monaco_power_infrastructure.png)

The visualization shows Monaco's power infrastructure with generators (green circles) and substations (red squares). You can also create detailed analysis plots:

![Monaco Power Analysis](generated-examples/images/monaco_power_analysis.png)

### Multi-Infrastructure Analysis

Earth-OSM supports various infrastructure types. Here's a highway network visualization for Luxembourg:

![Luxembourg Highway Network](generated-examples/images/luxembourg_highway_network.png)

### Regional Comparisons

Compare infrastructure across different regions:

![Regional Comparison](generated-examples/images/region_comparison.png)

!!! tip "Next Steps"
    - 📖 Read the [User Guide](user-guide/getting-started.md) for comprehensive tutorials
    - 🎨 Explore [Visualization Examples](user-guide/visualization.md) 
    - 🔧 Check the [API Reference](api-docs/README.md) for detailed documentation
    - 💬 Join our [Discord Community](https://discord.gg/reAx9Ed8Xq) for support

## 🤝 Community & Support

- **Documentation**: Comprehensive guides and API reference
- **Discord**: Active community support and discussions  
- **GitHub**: Source code, issues, and contributions
- **PyPI**: Regular releases and package distribution

---

<p align="center">
<strong>Made with ❤️ by the PyPSA meets Earth team</strong>
</p>

<!-- LINK GROUP -->
[contributing]: https://github.com/pypsa-meets-earth/earth-osm/blob/main/CONTRIBUTING.md
[license]: https://github.com/pypsa-meets-earth/earth-osm/blob/main/LICENSE
[docs-url]: https://pypsa-meets-earth.github.io/earth-osm/
[discord-url]: https://discord.gg/AnuJBk23FU
[pypi-url]: https://pypi.org/project/earth-osm/
[conda-url]: https://anaconda.org/conda-forge/earth-osm
[codecov-url]: https://codecov.io/gh/pypsa-meets-earth/earth-osm
[gh-repo-url]: https://github.com/pypsa-meets-earth/earth-osm
[gh-release-url]: https://github.com/pypsa-meets-earth/earth-osm/releases

<!-- Primary badges -->
[badge-pypi-monthly-downloads]: https://img.shields.io/pypi/dm/earth-osm?style=flat&labelColor=black&logoColor=white&logo=pypi
[badge-codecov]: https://img.shields.io/codecov/c/github/pypsa-meets-earth/earth-osm?style=flat&labelColor=black&logoColor=white&logo=codecov
[badge-ci]: https://img.shields.io/github/actions/workflow/status/pypsa-meets-earth/earth-osm/main.yml?style=flat&labelColor=black&logoColor=white&logo=github
[badge-docs]: https://img.shields.io/github/actions/workflow/status/pypsa-meets-earth/earth-osm/docs-ci.yml?style=flat&labelColor=black&logoColor=white&logo=github

[badge-pypi]: https://img.shields.io/pypi/v/earth-osm.svg?style=flat&labelColor=black&logoColor=white&logo=pypi
[badge-conda]: https://img.shields.io/conda/vn/conda-forge/earth-osm.svg?style=flat&labelColor=black&logoColor=white&logo=conda-forge

[badge-discord]: https://img.shields.io/discord/911692131440148490?style=flat&labelColor=black&logoColor=white&logo=discord&color=blue
[badge-license]: https://img.shields.io/badge/License-MIT-blue.svg?style=flat&labelColor=black
[badge-release]: https://img.shields.io/github/v/release/pypsa-meets-earth/earth-osm?style=flat&labelColor=black&logoColor=white&logo=github


