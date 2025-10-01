# Monaco Power Infrastructure Example

*Generated on 2024-10-01*

## Overview

This example demonstrates extracting power infrastructure data for Monaco using Earth-OSM.

**Statistics:**
- Total features extracted: 34
- Feature types: substation, generator, cable, tower
- Region: Monaco

## Visualization Results

### Power Infrastructure Map

![Monaco Power Infrastructure](images/monaco_power_infrastructure.png)

The map shows Monaco's power infrastructure with:
- **Green circles**: Power generators (29 features) - includes solar panels and other generation sources
- **Red squares**: Substations (2 features) - critical electrical distribution nodes

### Statistical Analysis

![Monaco Power Analysis](images/monaco_power_analysis.png)

The analysis reveals:
- **Element Types**: Primarily node-based features (point locations)
- **Power Sources**: Various generator types including solar installations
- **Data Quality**: Comprehensive attribute coverage with minimal missing data
- **Infrastructure Count**: Detailed breakdown of each feature type

## Code Example

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

# Load and visualize the data
substations = gpd.read_file('./earth_data/out/MC_substation.geojson')
generators = gpd.read_file('./earth_data/out/MC_generator.geojson')

# Create visualization
fig, ax = plt.subplots(figsize=(12, 10))

# Plot generators as green circles
generators.plot(ax=ax, color='#2ecc71', markersize=60, alpha=0.8, 
                label='Generators', edgecolor='darkgreen')

# Plot substations as red squares
substations.plot(ax=ax, color='#e74c3c', markersize=100, alpha=0.8, 
                 label='Substations', marker='s', edgecolor='darkred')

ax.set_title('Monaco Power Infrastructure', fontsize=16, fontweight='bold')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.legend()
ax.grid(True, alpha=0.3)
plt.show()

# Load CSV data for detailed analysis
df_generators = pd.read_csv('./earth_data/out/MC_generator.csv')
print(f"Found {len(df_generators)} generators")
print(f"Generator types: {df_generators['tags.power'].value_counts()}")
```

## Results

### Power Infrastructure Overview

Monaco's power infrastructure includes:

- **2 Substations**: Critical nodes in the electrical distribution network
- **29 Generators**: Various power generation sources including solar panels
- **2 Cable segments**: Underground power cables
- **1 Tower**: Power transmission infrastructure

### Data Sample

Sample of substation data:

| Column | Sample Value | Description |
|--------|--------------|-------------|
| `id` | 686864062 | Unique OSM identifier |
| `Type` | area | OSM element type (node/way/relation) |
| `Region` | MC | Region code |
| `tags.power` | substation | Power infrastructure type |
| `tags.voltage` | NaN | Voltage specification |
| `tags.substation` | NaN | Substation type |

### Key Features

- **Small dataset**: Perfect for testing and learning
- **Variety of features**: Multiple infrastructure types in one small area
- **Real data**: Extracted from OpenStreetMap via GeoFabrik
- **Fast extraction**: Small region processes quickly

## Usage Notes

- Monaco is an excellent region for testing due to its small size
- The same approach works for larger regions (may take longer to process)
- Data is cached locally - subsequent runs are faster
- Both CSV and GeoJSON formats are available for analysis

## Next Steps

- Try different regions from the [Supported Regions](../regions.md) list
- Explore other infrastructure types: `railway`, `highway`, `waterway`, etc.
- Use the data for spatial analysis, network modeling, or visualization
- Combine multiple regions for larger-scale analysis

## Visualization Example

```python
import pandas as pd
import ast

# Load and process the data
df = pd.read_csv('./earth_data/out/MC_generator.csv')

# Parse coordinates for simple plotting
coords = []
for lonlat_str in df['lonlat'].dropna():
    try:
        coord_list = ast.literal_eval(lonlat_str)
        if coord_list and len(coord_list) > 0:
            coords.append(coord_list[0])
    except:
        continue

if coords:
    lons, lats = zip(*coords)
    
    plt.figure(figsize=(10, 8))
    plt.scatter(lons, lats, c='red', s=50, alpha=0.7)
    plt.title('Monaco Power Generators')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True, alpha=0.3)
    plt.show()
```

This example provides a solid foundation for understanding Earth-OSM's capabilities with real-world infrastructure data.