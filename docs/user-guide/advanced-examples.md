---
title: Advanced Examples
description: Complex workflows and use cases for Earth-OSM
---

# Advanced Examples

This section demonstrates advanced use cases and complex workflows using Earth-OSM.

## Large-Scale Analysis

### Continental Power Grid Analysis

Extract power infrastructure for all European countries:

```python
import earth_osm as eo

# List of European countries
european_countries = [
    'germany', 'france', 'italy', 'spain', 'poland', 
    'netherlands', 'belgium', 'czech-republic', 'austria', 
    'switzerland', 'denmark', 'sweden', 'norway'
]

# Extract power infrastructure
eo.save_osm_data(
    primary_name='power',
    region_list=european_countries,
    feature_list=['substation', 'line'],
    out_dir='./europe_power_grid',
    mp=True,  # Enable multiprocessing
    out_format=['csv', 'geojson']
)
```

### Cross-Border Infrastructure Analysis

Analyze transportation connections between neighboring countries:

```python
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Extract railway data for border regions
border_regions = ['germany', 'france', 'belgium', 'netherlands']

for region in border_regions:
    eo.save_osm_data(
        primary_name='railway',
        region_list=[region],
        feature_list=['rail', 'station'],
        out_dir=f'./border_analysis/{region}'
    )

# Combine and analyze
all_stations = []
for region in border_regions:
    df = pd.read_csv(f'./border_analysis/{region}/{region.upper()[:2]}_station.csv')
    df['country'] = region
    all_stations.append(df)

combined_stations = pd.concat(all_stations, ignore_index=True)
print(f"Total stations: {len(combined_stations)}")
```

## Data Integration and Processing

### Combining Multiple Infrastructure Types

```python
import pandas as pd
import numpy as np

def extract_multiple_infrastructure(region, output_dir):
    """Extract multiple infrastructure types for comprehensive analysis."""
    
    infrastructure_types = {
        'power': ['substation', 'line', 'generator'],
        'railway': ['rail', 'station'],
        'highway': ['primary', 'secondary', 'trunk'],
        'waterway': ['river', 'canal']
    }
    
    for infra_type, features in infrastructure_types.items():
        print(f"Extracting {infra_type} infrastructure...")
        eo.save_osm_data(
            primary_name=infra_type,
            region_list=[region],
            feature_list=features,
            out_dir=f'{output_dir}/{region}_{infra_type}',
            out_format=['csv']
        )

# Extract for Germany
extract_multiple_infrastructure('germany', './comprehensive_analysis')
```

### Custom Data Processing Pipeline

```python
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import ast

def process_power_data(csv_file):
    """Advanced processing of power infrastructure data."""
    
    df = pd.read_csv(csv_file)
    
    # Parse coordinates
    def parse_lonlat(lonlat_str):
        try:
            coords = ast.literal_eval(lonlat_str)
            if isinstance(coords, list) and len(coords) > 0:
                if len(coords) == 1:
                    return Point(coords[0])
                else:
                    return LineString(coords)
        except:
            return None
    
    df['geometry'] = df['lonlat'].apply(parse_lonlat)
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
    
    # Clean voltage data
    def clean_voltage(voltage_str):
        if pd.isna(voltage_str):
            return None
        try:
            # Extract numeric voltage values
            import re
            numbers = re.findall(r'\d+', str(voltage_str))
            if numbers:
                return max([int(n) for n in numbers])
        except:
            return None
    
    gdf['voltage_kv'] = gdf['tags.voltage'].apply(clean_voltage)
    
    # Categorize by voltage level
    def voltage_category(voltage):
        if pd.isna(voltage):
            return 'Unknown'
        elif voltage >= 400:
            return 'Extra High Voltage (≥400kV)'
        elif voltage >= 100:
            return 'High Voltage (100-400kV)'
        elif voltage >= 35:
            return 'Medium Voltage (35-100kV)'
        else:
            return 'Low Voltage (<35kV)'
    
    gdf['voltage_category'] = gdf['voltage_kv'].apply(voltage_category)
    
    return gdf

# Process German substations
gdf = process_power_data('./earth_data/out/DE_substation.csv')
print(gdf['voltage_category'].value_counts())
```

## Temporal Analysis

### Monitoring Infrastructure Changes

```python
import datetime
import os

def track_infrastructure_changes(region, infrastructure_type):
    """Track infrastructure changes over time."""
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    output_dir = f'./temporal_analysis/{region}_{infrastructure_type}_{timestamp}'
    
    # Extract current data
    eo.save_osm_data(
        primary_name=infrastructure_type,
        region_list=[region],
        out_dir=output_dir,
        update=True  # Force fresh download
    )
    
    # Compare with previous extraction if exists
    previous_files = []
    for root, dirs, files in os.walk('./temporal_analysis'):
        for file in files:
            if file.startswith(f'{region}_{infrastructure_type}') and file.endswith('.csv'):
                previous_files.append(os.path.join(root, file))
    
    if len(previous_files) > 1:
        # Simple comparison
        current_df = pd.read_csv(f'{output_dir}/out/{region.upper()[:2]}_{infrastructure_type}.csv')
        previous_df = pd.read_csv(sorted(previous_files)[-2])
        
        print(f"Current features: {len(current_df)}")
        print(f"Previous features: {len(previous_df)}")
        print(f"Change: {len(current_df) - len(previous_df):+d}")

# Track monthly changes
track_infrastructure_changes('netherlands', 'power')
```

## Spatial Analysis Examples

### Distance Analysis

```python
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
from scipy.spatial.distance import cdist

def analyze_substation_density(region):
    """Analyze spatial distribution of substations."""
    
    # Load substation data
    gdf = gpd.read_file(f'./earth_data/out/{region.upper()[:2]}_substation.geojson')
    
    # Convert to projected CRS for accurate distance calculations
    gdf_proj = gdf.to_crs('EPSG:3857')  # Web Mercator
    
    # Calculate nearest neighbor distances
    coords = np.array([[geom.x, geom.y] for geom in gdf_proj.geometry if geom.geom_type == 'Point'])
    
    if len(coords) > 1:
        distances = cdist(coords, coords)
        np.fill_diagonal(distances, np.inf)
        nearest_distances = np.min(distances, axis=1)
        
        print(f"Substation Analysis for {region.title()}:")
        print(f"- Total substations: {len(gdf)}")
        print(f"- Mean nearest neighbor distance: {np.mean(nearest_distances):.0f} meters")
        print(f"- Median nearest neighbor distance: {np.median(nearest_distances):.0f} meters")
        
        return nearest_distances
    
    return None

# Analyze multiple regions
regions = ['netherlands', 'belgium', 'denmark']
for region in regions:
    distances = analyze_substation_density(region)
```

### Buffer Analysis

```python
import geopandas as gpd
from shapely.geometry import Point

def analyze_coverage(region, infrastructure_type, buffer_km=5):
    """Analyze infrastructure coverage using buffer analysis."""
    
    # Load infrastructure data
    gdf = gpd.read_file(f'./earth_data/out/{region.upper()[:2]}_{infrastructure_type}.geojson')
    
    # Convert to appropriate projected CRS
    gdf_proj = gdf.to_crs('EPSG:3857')
    
    # Create buffer around infrastructure
    buffer_m = buffer_km * 1000  # Convert km to meters
    gdf_proj['buffer'] = gdf_proj.geometry.buffer(buffer_m)
    
    # Calculate total coverage area
    union_buffer = gdf_proj['buffer'].unary_union
    coverage_area_km2 = union_buffer.area / 1e6  # Convert m² to km²
    
    print(f"{infrastructure_type.title()} Coverage Analysis for {region.title()}:")
    print(f"- Number of features: {len(gdf)}")
    print(f"- Coverage area ({buffer_km}km buffer): {coverage_area_km2:.0f} km²")
    
    return gdf_proj

# Analyze power line coverage
coverage_gdf = analyze_coverage('netherlands', 'line', buffer_km=2)
```

## Performance Optimization

### Parallel Processing for Large Datasets

```python
import multiprocessing as mp
import earth_osm as eo
from functools import partial

def extract_region_data(region, infrastructure_type, base_dir):
    """Extract data for a single region."""
    try:
        eo.save_osm_data(
            primary_name=infrastructure_type,
            region_list=[region],
            out_dir=f'{base_dir}/{region}',
            mp=False  # Disable internal MP since we're already parallelizing
        )
        return f"Completed: {region}"
    except Exception as e:
        return f"Failed: {region} - {str(e)}"

def parallel_extraction(regions, infrastructure_type, max_workers=None):
    """Extract data for multiple regions in parallel."""
    
    if max_workers is None:
        max_workers = min(len(regions), mp.cpu_count())
    
    extract_func = partial(
        extract_region_data, 
        infrastructure_type=infrastructure_type,
        base_dir='./parallel_extraction'
    )
    
    with mp.Pool(max_workers) as pool:
        results = pool.map(extract_func, regions)
    
    for result in results:
        print(result)

# Extract power data for all EU countries in parallel
eu_countries = [
    'germany', 'france', 'italy', 'spain', 'poland',
    'netherlands', 'belgium', 'austria', 'portugal'
]

parallel_extraction(eu_countries, 'power', max_workers=4)
```

### Memory-Efficient Processing

```python
import pandas as pd
import numpy as np

def process_large_dataset_chunked(csv_file, chunk_size=10000):
    """Process large CSV files in chunks to manage memory."""
    
    results = []
    chunk_iter = pd.read_csv(csv_file, chunksize=chunk_size)
    
    for i, chunk in enumerate(chunk_iter):
        print(f"Processing chunk {i+1}...")
        
        # Process chunk
        processed_chunk = chunk[chunk['tags.power'].notna()]
        
        # Calculate statistics
        chunk_stats = {
            'chunk_id': i,
            'total_features': len(chunk),
            'power_features': len(processed_chunk),
            'unique_power_types': processed_chunk['tags.power'].nunique()
        }
        
        results.append(chunk_stats)
        
        # Optional: save processed chunk
        processed_chunk.to_csv(f'./processed/chunk_{i:03d}.csv', index=False)
    
    # Combine statistics
    stats_df = pd.DataFrame(results)
    print("\nProcessing Summary:")
    print(f"Total chunks: {len(stats_df)}")
    print(f"Total features: {stats_df['total_features'].sum()}")
    print(f"Power features: {stats_df['power_features'].sum()}")
    
    return stats_df

# Process large dataset
# stats = process_large_dataset_chunked('./earth_data/out/DE_power.csv')
```

## Custom Workflows

### Research Pipeline Example

```python
import earth_osm as eo
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

class PowerGridAnalyzer:
    """Complete workflow for power grid analysis."""
    
    def __init__(self, region, output_dir='./power_analysis'):
        self.region = region
        self.output_dir = output_dir
        self.data = {}
    
    def extract_data(self):
        """Extract all power-related data."""
        print(f"Extracting power data for {self.region}...")
        
        eo.save_osm_data(
            primary_name='power',
            region_list=[self.region],
            out_dir=self.output_dir,
            out_format=['csv', 'geojson']
        )
        
        # Load extracted data
        region_code = self.region.upper()[:2]
        
        try:
            self.data['substations'] = pd.read_csv(f'{self.output_dir}/out/{region_code}_substation.csv')
            self.data['lines'] = pd.read_csv(f'{self.output_dir}/out/{region_code}_line.csv') 
            self.data['generators'] = pd.read_csv(f'{self.output_dir}/out/{region_code}_generator.csv')
        except FileNotFoundError as e:
            print(f"Some data files not found: {e}")
    
    def analyze_voltage_levels(self):
        """Analyze voltage level distribution."""
        if 'substations' not in self.data:
            return
        
        df = self.data['substations']
        voltage_data = df['tags.voltage'].dropna()
        
        print(f"\nVoltage Level Analysis for {self.region.title()}:")
        print(f"Substations with voltage data: {len(voltage_data)}")
        print(f"Unique voltage levels: {voltage_data.nunique()}")
        print("\nTop voltage levels:")
        print(voltage_data.value_counts().head(10))
    
    def generate_report(self):
        """Generate comprehensive analysis report."""
        report = []
        report.append(f"# Power Grid Analysis: {self.region.title()}")
        report.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")
        
        for feature_type, df in self.data.items():
            if df is not None and len(df) > 0:
                report.append(f"## {feature_type.title()}")
                report.append(f"- Total features: {len(df)}")
                report.append(f"- Node features: {sum(df['Type'] == 'node')}")
                report.append(f"- Way/Area features: {sum(df['Type'] != 'node')}")
                report.append("")
        
        # Save report
        with open(f'{self.output_dir}/analysis_report.md', 'w') as f:
            f.write('\n'.join(report))
        
        print(f"Analysis report saved to {self.output_dir}/analysis_report.md")

# Use the analyzer
analyzer = PowerGridAnalyzer('netherlands')
analyzer.extract_data()
analyzer.analyze_voltage_levels()
analyzer.generate_report()
```

## Integration with Other Tools

### PyPSA Integration Example

```python
# Example showing how to prepare Earth-OSM data for PyPSA
import pandas as pd
import geopandas as gpd
import numpy as np

def prepare_pypsa_network(region):
    """Convert Earth-OSM data to PyPSA-compatible format."""
    
    # Load Earth-OSM data
    substations = pd.read_csv(f'./earth_data/out/{region.upper()[:2]}_substation.csv')
    lines = pd.read_csv(f'./earth_data/out/{region.upper()[:2]}_line.csv')
    
    # Process substations for PyPSA buses
    buses = substations.copy()
    buses['bus_id'] = buses['id'].astype(str)
    buses['v_nom'] = pd.to_numeric(buses['tags.voltage'], errors='coerce') / 1000  # Convert to kV
    buses = buses[['bus_id', 'v_nom', 'lonlat']].dropna()
    
    # Process lines for PyPSA
    lines_processed = lines.copy()
    lines_processed['line_id'] = lines_processed['id'].astype(str)
    lines_processed['voltage'] = pd.to_numeric(lines_processed['tags.voltage'], errors='coerce')
    
    print(f"Prepared for PyPSA:")
    print(f"- Buses: {len(buses)}")
    print(f"- Lines: {len(lines_processed)}")
    
    return buses, lines_processed

# Prepare data for PyPSA
buses, lines = prepare_pypsa_network('netherlands')
```

This advanced examples section demonstrates the flexibility and power of Earth-OSM for complex infrastructure analysis workflows. The examples can be adapted and extended based on specific research or analysis needs.

## Next Steps

- Learn about [Visualization](visualization.md) techniques
- Check the [API Reference](../api-docs/README.md) for detailed function documentation
- Explore the source code on [GitHub](https://github.com/pypsa-meets-earth/earth-osm) for more examples