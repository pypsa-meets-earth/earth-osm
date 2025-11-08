---
title: Getting Started
description: Quick start guide for Earth-OSM
---

# Getting Started with Earth-OSM

Earth-OSM is a powerful Python tool for extracting large-scale infrastructure data from OpenStreetMap (OSM). This guide will help you get up and running quickly.

## Installation

### Via pip (Recommended)

```bash
pip install earth-osm
```

### Via conda

```bash
conda install --channel=conda-forge earth-osm
```

### Development Installation

For development or to get the latest features:

```bash
pip install git+https://github.com/pypsa-meets-earth/earth-osm.git
```

## Quick Start

### Command Line Interface

Extract power infrastructure data for Monaco:

```bash
earth_osm extract power --regions monaco --features substation line
```

This command will:

- Download Monaco's OSM data from GeoFabrik
- Extract power substations and lines
- Save results in `./earth_data/out/` as both CSV and GeoJSON files

### Python API

```python
import earth_osm as eo

# Extract power infrastructure for multiple regions
eo.save_osm_data(
    primary_name='power',
    region_list=['monaco', 'luxembourg'],
    feature_list=['substation', 'line', 'generator'],
    data_dir='./my_data',
    out_format=['csv', 'geojson']
)
```

## Key Concepts

### Infrastructure Types

Earth-OSM supports various infrastructure types (called "primary features"):

- **Power**: Electrical infrastructure (substations, lines, generators)
- **Railway**: Rail transport infrastructure
- **Highway**: Road infrastructure
- **Waterway**: Water-related infrastructure
- **And many more**: amenity, building, boundary, etc.

### Regions

You can specify regions using:

- **ISO codes**: `DE`, `FR`, `US-CA` 
- **Full names**: `germany`, `france`, `california`
- **Region IDs**: Numeric identifiers from GeoFabrik

!!! tip "Finding Regions"
    Visit the [Supported Regions](../regions.md) page for a complete list of available regions.

### Features

Features are sub-categories within each infrastructure type:

- **Power features**: `substation`, `line`, `generator`, `tower`, `cable`
- **Railway features**: `rail`, `station`, `platform`, `signal`
- **Highway features**: `primary`, `secondary`, `trunk`, `motorway`

## Output Formats

Earth-OSM supports multiple output formats:

=== "CSV"
    Tabular data with all attributes as columns
    ```
    id,lonlat,Type,Region,tags.power,tags.voltage,...
    123,"[(7.41, 43.73)]",node,MC,substation,20000,...
    ```

=== "GeoJSON"
    Spatial data format for GIS applications
    ```json
    {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": {"type": "Point", "coordinates": [7.41, 43.73]},
          "properties": {"power": "substation", "voltage": "20000"}
        }
      ]
    }
    ```

## Next Steps

- Learn about [Basic Usage](basic-usage.md) patterns
- Explore [Advanced Examples](advanced-examples.md) 
- See [Visualization](visualization.md) techniques
- Check the [API Reference](../api-docs/README.md)

## Need Help?

- 📖 Read the full documentation
- 💬 Join our [Discord community](https://discord.gg/reAx9Ed8Xq)
- 🐛 Report issues on [GitHub](https://github.com/pypsa-meets-earth/earth-osm/issues)
- 📧 Contact the PyPSA meets Earth team