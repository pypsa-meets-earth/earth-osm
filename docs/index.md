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

## 📊 Example: Complete Power Network Analysis

Let's extract and visualize a complete power network in Monaco, including substations, generators, lines, and cables:

```python
from earth_osm.eo import save_osm_data
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# Extract complete power infrastructure for Monaco
save_osm_data(
    region_list=['monaco'],
    primary_name='power',
    out_dir='./earth_data'
)

# Load all power network components
substations = gpd.read_file('./earth_data/out/MC_substation.geojson')
generators = gpd.read_file('./earth_data/out/MC_generator.geojson')
lines = gpd.read_file('./earth_data/out/MC_line.geojson')
cables = gpd.read_file('./earth_data/out/MC_cable.geojson')

# Create comprehensive visualization with basemap
fig, ax = plt.subplots(figsize=(14, 12))

# Convert to Web Mercator for basemap
substations_web = substations.to_crs(epsg=3857)
generators_web = generators.to_crs(epsg=3857)
lines_web = lines.to_crs(epsg=3857)
cables_web = cables.to_crs(epsg=3857)

# Plot network components
lines_web.plot(ax=ax, color='#3498db', linewidth=2, alpha=0.6, label='Power Lines')
cables_web.plot(ax=ax, color='#9b59b6', linewidth=1.5, alpha=0.6, linestyle='--', label='Cables')
generators_web.plot(ax=ax, color='#2ecc71', markersize=80, alpha=0.8, label='Generators')
substations_web.plot(ax=ax, color='#e74c3c', markersize=120, alpha=0.9, label='Substations', marker='s')

# Add basemap for geographic context
ctx.add_basemap(ax, source=ctx.providers.CartoDB.DarkMatter, alpha=0.7)

ax.set_title('Monaco Complete Power Network', fontsize=16, fontweight='bold')
ax.legend(loc='upper left')
ax.set_axis_off()
plt.show()
```

### Complete Power Network Visualization

![Monaco Complete Power Network](generated-examples/images/monaco_power_network_complete.png)

*This visualization shows Monaco's complete electrical infrastructure network with substations (red squares), generators (green circles), power lines (blue), and underground cables (purple dashes) overlaid on a geographic basemap.*

### Statistical Analysis

Create detailed infrastructure analysis with data quality metrics:

![Monaco Power Analysis](generated-examples/images/monaco_power_analysis.png)

*Multi-panel analysis showing OSM element type distribution, power source types, data completeness metrics, and infrastructure feature counts.*

### Road Network Hierarchy

Earth-OSM supports various infrastructure types. Here's a highway network visualization for Luxembourg showing road classification hierarchy with basemap:

![Luxembourg Highway Hierarchy](generated-examples/images/luxembourg_highway_hierarchy.png)

*Luxembourg's road network color-coded by importance: motorways (dark red), trunk roads (purple), primary roads (bright red), secondary (orange), tertiary (yellow), and residential streets (gray), displayed over an OpenStreetMap base layer.*

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


