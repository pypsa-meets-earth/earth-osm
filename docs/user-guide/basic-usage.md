---
title: Basic Usage
description: Common usage patterns and examples for Earth-OSM
---

# Basic Usage Patterns

This guide covers the most common ways to use Earth-OSM for extracting infrastructure data.

## Command Line Interface

### Single Region, Single Feature

Extract power substations from Germany:

```bash
earth_osm extract power --regions germany --features substation
```

### Multiple Regions

Extract data from multiple countries:

```bash
earth_osm extract power --regions germany france italy --features substation line
```

### All Features

Extract all power-related features (omit `--features`):

```bash
earth_osm extract power --regions netherlands
```

## Python API Examples

### Basic Extraction

```python
import earth_osm as eo

# Extract power infrastructure
eo.save_osm_data(
    primary_name='power',
    region_list=['denmark'],
    feature_list=['substation', 'line']
)
```

### Custom Output Directory

```python
import earth_osm as eo

eo.save_osm_data(
    primary_name='railway',
    region_list=['switzerland'],
    feature_list=['rail', 'station'],
    out_dir='./my_project/railway_data',
    out_format=['geojson']  # Only GeoJSON output
)
```

### Loading and Processing Data

```python
import pandas as pd
import geopandas as gpd

# Load CSV data
df = pd.read_csv('./earth_data/out/DE_substation.csv')
print(f"Found {len(df)} substations in Germany")

# Load GeoJSON for spatial analysis
gdf = gpd.read_file('./earth_data/out/DE_substation.geojson')
print(f"CRS: {gdf.crs}")
```

## Configuration Options

### Data Sources

Choose between GeoFabrik (default) and Overpass API:

=== "GeoFabrik (Recommended)"
    ```bash
    earth_osm extract power --regions monaco --source geofabrik
    ```
    - Faster downloads
    - No rate limits
    - Pre-processed regional extracts

=== "Overpass API"
    ```bash
    earth_osm extract power --regions monaco --source overpass
    ```
    - Real-time data
    - Custom queries possible
    - Rate limited

### Output Aggregation

Control how outputs are organized:

=== "By Feature (Default)"
    ```bash
    earth_osm extract power --regions germany --features substation line
    ```
    Creates: `DE_substation.csv`, `DE_line.csv`

=== "By Region"
    ```bash
    earth_osm extract power --regions germany france --agg_region
    ```
    Creates: `germany_power.csv`, `france_power.csv`

=== "Single File"
    ```bash
    earth_osm extract power --regions germany --features substation line --agg_feature
    ```
    Creates: `DE_power.csv` (combined features)

### Multiprocessing

Control parallel processing:

```bash
# Enable multiprocessing (default)
earth_osm extract power --regions germany france italy

# Disable multiprocessing
earth_osm extract power --regions germany france italy --no_mp
```

## Working with Different Infrastructure Types

### Power Infrastructure

```python
# Get all power-related features
eo.save_osm_data('power', ['germany'], ['substation', 'line', 'generator', 'tower'])
```

Common power features:
- `substation`: Electrical substations
- `line`: Power transmission lines  
- `generator`: Power generation facilities
- `tower`: Transmission towers
- `cable`: Underground cables

**See our [visualization examples](../generated-examples/README.md) for power infrastructure analysis with real plots and maps.**

### Transportation

```python
# Railway infrastructure
eo.save_osm_data('railway', ['france'], ['rail', 'station', 'platform'])

# Road infrastructure  
eo.save_osm_data('highway', ['netherlands'], ['primary', 'secondary', 'trunk'])
```

**View the [Luxembourg highway network visualization](../generated-examples/README.md) showing multi-class road networks.**

### Water Infrastructure

```python
# Water-related infrastructure
eo.save_osm_data('waterway', ['austria'], ['river', 'canal', 'dam'])
```

## Data Quality and Filtering

### Understanding OSM Data Structure

Earth-OSM preserves the original OSM data structure:

- **Nodes**: Point features (single coordinates)
- **Ways**: Linear or area features (multiple coordinates)
- **Relations**: Complex features (multipolygons, routes)

### Common Data Columns

All extracted data includes these standard columns:

- `id`: Unique OSM identifier
- `lonlat`: Coordinates (list of tuples)
- `Type`: OSM element type (node/way/relation)
- `Region`: Region code
- `tags.*`: OSM tags as individual columns
- `other_tags`: Additional tags as dictionary

### Filtering Example

```python
import pandas as pd

# Load substation data
df = pd.read_csv('./earth_data/out/DE_substation.csv')

# Filter by voltage level
high_voltage = df[df['tags.voltage'].astype(str).str.contains('400000|220000', na=False)]

# Filter by type
transmission_substations = df[df['tags.substation'] == 'transmission']

print(f"High voltage substations: {len(high_voltage)}")
print(f"Transmission substations: {len(transmission_substations)}")
```

## Error Handling

### Common Issues

1. **Region not found**: Check spelling and available regions
2. **No data found**: Some regions may not have the requested infrastructure
3. **Download failures**: Network issues or GeoFabrik unavailable

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your earth_osm code here
```

## Best Practices

### 1. Start Small
Begin with small regions (like Monaco or Luxembourg) to test your workflow.

### 2. Use Appropriate Data Sources
- Use **GeoFabrik** for large extractions
- Use **Overpass** for real-time or custom queries

### 3. Organize Your Data
```python
# Use descriptive output directories
eo.save_osm_data(
    'power', 
    ['germany'], 
    ['substation'],
    out_dir=f'./projects/germany_power_{date.today()}'
)
```

### 4. Check Data Coverage
```python
import pandas as pd

df = pd.read_csv('./earth_data/out/DE_substation.csv')
print(f"Data summary:")
print(f"- Total features: {len(df)}")
print(f"- Node features: {sum(df['Type'] == 'node')}")
print(f"- Area features: {sum(df['Type'] == 'area')}")
print(f"- Available tags: {[col for col in df.columns if col.startswith('tags.')]}")
```

## Next Steps

- Explore [Advanced Examples](advanced-examples.md) for complex workflows
- Learn about [Visualization](visualization.md) techniques
- Check the [API Reference](../api-docs/README.md) for detailed documentation