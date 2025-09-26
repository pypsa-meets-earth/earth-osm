# Monaco Power Infrastructure Example

*Generated on 2024-09-26*

## Overview

This example demonstrates extracting power infrastructure data for Monaco using Earth-OSM.

**Statistics:**
- Total features extracted: 32
- Feature types: substation, generator, cable, tower
- Region: Monaco

## Code Example

```python
from earth_osm.eo import save_osm_data
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Extract power infrastructure for Monaco
save_osm_data(
    region_list=['monaco'],
    primary_name='power',
    out_dir='./earth_data',
    out_format=['csv', 'geojson']
)

# Load substations data
substations_df = pd.read_csv('./earth_data/out/MC_substation.csv')
print(f"Found {len(substations_df)} substations")

# Load generators data  
generators_df = pd.read_csv('./earth_data/out/MC_generator.csv')
print(f"Found {len(generators_df)} generators")

# Display sample data
print("\nSubstation data sample:")
print(substations_df[['id', 'Type', 'tags.power', 'tags.voltage']].head())
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