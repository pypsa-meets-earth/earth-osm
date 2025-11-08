#!/usr/bin/env python3
"""
Automated documentation example generation for Earth-OSM

This script automatically generates visualization examples for different regions
and infrastructure types to keep documentation up-to-date.
"""

import os
import sys
import argparse
from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add earth_osm to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from earth_osm.eo import save_osm_data


class DocsExampleGenerator:
    """Generate documentation examples automatically."""
    
    def __init__(self, output_dir='docs/generated-examples'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.image_dir = self.output_dir / 'images'
        self.image_dir.mkdir(exist_ok=True)
        
        # Small regions for quick examples
        self.example_regions = ['monaco', 'luxembourg', 'andorra', 'liechtenstein']
        self.infrastructure_types = ['power', 'railway', 'highway']
        
    def extract_sample_data(self, region, infrastructure_type, max_features=None):
        """Extract sample data for a region and infrastructure type."""
        try:
            print(f"Extracting {infrastructure_type} data for {region}...")
            
            save_osm_data(
                region_list=[region],
                primary_name=infrastructure_type,
                out_dir=f'./temp_data/{region}_{infrastructure_type}',
                out_format=['csv', 'geojson'],
                mp=False  # Disable multiprocessing for small extractions
            )
            
            region_code = region.upper()[:2]
            
            # Load the data
            csv_files = list(Path(f'./temp_data/{region}_{infrastructure_type}/out').glob(f'{region_code}_*.csv'))
            geojson_files = list(Path(f'./temp_data/{region}_{infrastructure_type}/out').glob(f'{region_code}_*.geojson'))
            
            data = {}
            for csv_file in csv_files:
                feature_name = csv_file.stem.split('_', 1)[1]  # Remove region code
                df = pd.read_csv(csv_file)
                
                if max_features and len(df) > max_features:
                    df = df.sample(n=max_features, random_state=42)
                
                data[f'{feature_name}_csv'] = df
            
            for geojson_file in geojson_files:
                feature_name = geojson_file.stem.split('_', 1)[1]  # Remove region code
                try:
                    gdf = gpd.read_file(geojson_file)
                    if max_features and len(gdf) > max_features:
                        gdf = gdf.sample(n=max_features, random_state=42)
                    data[f'{feature_name}_geojson'] = gdf
                except Exception as e:
                    print(f"Could not load {geojson_file}: {e}")
            
            return data
            
        except Exception as e:
            print(f"Error extracting data for {region} - {infrastructure_type}: {e}")
            return {}
    
    def generate_basic_map(self, region, infrastructure_type, data):
        """Generate a basic infrastructure map."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = {'substation': 'red', 'line': 'blue', 'generator': 'green', 
                 'station': 'purple', 'rail': 'orange', 'primary': 'darkblue',
                 'secondary': 'lightblue', 'trunk': 'darkgreen'}
        
        legend_elements = []
        
        for key, gdf in data.items():
            if key.endswith('_geojson') and len(gdf) > 0:
                feature_type = key.replace('_geojson', '')
                color = colors.get(feature_type, 'gray')
                
                if gdf.geometry.iloc[0].geom_type == 'Point':
                    gdf.plot(ax=ax, color=color, markersize=30, alpha=0.8, label=feature_type.title())
                else:
                    gdf.plot(ax=ax, color=color, linewidth=2, alpha=0.7, label=feature_type.title())
                
                legend_elements.append(feature_type.title())
        
        ax.set_title(f'{region.title()} {infrastructure_type.title()} Infrastructure', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        
        if legend_elements:
            ax.legend()
        
        # Save the plot
        filename = self.image_dir / f'{region}_{infrastructure_type}_map.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def generate_statistics_plot(self, region, infrastructure_type, data):
        """Generate statistics visualization."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'{region.title()} {infrastructure_type.title()} Analysis', fontsize=14)
        
        # Combine all CSV data
        all_data = []
        for key, df in data.items():
            if key.endswith('_csv'):
                df['feature_type'] = key.replace('_csv', '')
                all_data.append(df)
        
        if not all_data:
            plt.close()
            return None
        
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # 1. Feature type distribution
        if 'Type' in combined_df.columns:
            type_counts = combined_df['Type'].value_counts()
            axes[0, 0].pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%')
            axes[0, 0].set_title('OSM Element Types')
        
        # 2. Feature count by type
        feature_counts = combined_df['feature_type'].value_counts()
        axes[0, 1].bar(feature_counts.index, feature_counts.values)
        axes[0, 1].set_title('Features by Type')
        axes[0, 1].set_ylabel('Count')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Data completeness
        completeness = (combined_df.isnull().sum() / len(combined_df) * 100).sort_values(ascending=False)
        top_missing = completeness.head(10)
        axes[1, 0].barh(range(len(top_missing)), top_missing.values)
        axes[1, 0].set_yticks(range(len(top_missing)))
        axes[1, 0].set_yticklabels(top_missing.index, fontsize=8)
        axes[1, 0].set_title('Data Completeness (% Missing)')
        axes[1, 0].set_xlabel('Percentage Missing')
        
        # 4. Tag frequency (for infrastructure-specific tags)
        tag_columns = [col for col in combined_df.columns if col.startswith('tags.')]
        if tag_columns:
            tag_completeness = {}
            for col in tag_columns[:10]:  # Top 10 tag columns
                tag_completeness[col.replace('tags.', '')] = combined_df[col].notna().sum()
            
            if tag_completeness:
                axes[1, 1].bar(tag_completeness.keys(), tag_completeness.values())
                axes[1, 1].set_title('Tag Completeness')
                axes[1, 1].set_ylabel('Features with Tag')
                axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save the plot
        filename = self.image_dir / f'{region}_{infrastructure_type}_stats.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def generate_markdown_example(self, region, infrastructure_type, data, map_image, stats_image):
        """Generate markdown documentation with the example."""
        
        # Calculate basic statistics
        total_features = sum(len(df) for key, df in data.items() if key.endswith('_csv'))
        feature_types = [key.replace('_csv', '') for key in data.keys() if key.endswith('_csv')]
        
        markdown_content = f"""# {region.title()} {infrastructure_type.title()} Infrastructure Example

*Auto-generated on {datetime.now().strftime('%Y-%m-%d')}*

## Overview

This example demonstrates extracting {infrastructure_type} infrastructure data for {region.title()}.

**Statistics:**
- Total features extracted: {total_features}
- Feature types: {', '.join(feature_types)}
- Region: {region.title()}

## Code Example

```python
from earth_osm.eo import save_osm_data
import geopandas as gpd
import matplotlib.pyplot as plt

# Extract {infrastructure_type} infrastructure for {region}
save_osm_data(
    region_list=['{region}'],
    primary_name='{infrastructure_type}',
    out_dir='./earth_data'
)

# Load and visualize the data
"""

        # Add loading code for each feature type
        for feature_type in feature_types:
            region_code = region.upper()[:2]
            markdown_content += f"""
# Load {feature_type} data
{feature_type}_gdf = gpd.read_file('./earth_data/out/{region_code}_{feature_type}.geojson')
print(f"Found {{{len(data.get(f'{feature_type}_csv', []))}}} {feature_type} features")
"""

        markdown_content += """
# Create visualization
fig, ax = plt.subplots(figsize=(10, 8))
"""

        # Add plotting code for each feature type
        colors = {'substation': 'red', 'line': 'blue', 'generator': 'green', 
                 'station': 'purple', 'rail': 'orange', 'primary': 'darkblue'}
        
        for feature_type in feature_types:
            color = colors.get(feature_type, 'gray')
            if feature_type in ['line', 'rail', 'primary', 'secondary']:
                markdown_content += f"""
{feature_type}_gdf.plot(ax=ax, color='{color}', linewidth=2, alpha=0.7, label='{feature_type.title()}')
"""
            else:
                markdown_content += f"""
{feature_type}_gdf.plot(ax=ax, color='{color}', markersize=30, alpha=0.8, label='{feature_type.title()}')
"""

        markdown_content += f"""
ax.set_title('{region.title()} {infrastructure_type.title()} Infrastructure')
ax.legend()
plt.show()
```

## Results

### Infrastructure Map
"""

        if map_image:
            markdown_content += f"![{region.title()} {infrastructure_type.title()} Map](images/{map_image.name})\n\n"

        markdown_content += "### Statistical Analysis\n"
        
        if stats_image:
            markdown_content += f"![{region.title()} {infrastructure_type.title()} Statistics](images/{stats_image.name})\n\n"

        # Add data sample
        if feature_types and data:
            sample_data = data.get(f'{feature_types[0]}_csv')
            if sample_data is not None and len(sample_data) > 0:
                markdown_content += f"""
### Data Sample

Sample of {feature_types[0]} data:

| Column | Sample Value | Description |
|--------|--------------|-------------|
"""
                # Show sample of key columns
                key_columns = ['id', 'Type', 'Region'] + [col for col in sample_data.columns if col.startswith('tags.')][:5]
                for col in key_columns:
                    if col in sample_data.columns:
                        sample_value = sample_data[col].dropna().iloc[0] if not sample_data[col].dropna().empty else 'N/A'
                        # Truncate long values
                        if isinstance(sample_value, str) and len(sample_value) > 50:
                            sample_value = sample_value[:47] + "..."
                        markdown_content += f"| `{col}` | {sample_value} | {self._get_column_description(col)} |\n"

        markdown_content += f"""

## Usage Notes

- This example uses {region.title()}, a small region suitable for testing
- The same approach works for larger regions (may take longer to process)
- Data is cached locally - subsequent runs will be faster
- Both CSV and GeoJSON formats are available for analysis

## Next Steps

- Try different regions from the [Supported Regions](../regions.md) list
- Explore other infrastructure types: `railway`, `highway`, `waterway`, etc.
- Use the data for spatial analysis, network modeling, or visualization
- Combine multiple regions for larger-scale analysis

"""
        
        return markdown_content
    
    def _get_column_description(self, column):
        """Get description for common columns."""
        descriptions = {
            'id': 'Unique OSM identifier',
            'Type': 'OSM element type (node/way/relation)',
            'Region': 'Region code',
            'lonlat': 'Coordinates as list of tuples',
            'tags.power': 'Power infrastructure type',
            'tags.voltage': 'Voltage specification',
            'tags.substation': 'Substation type',
            'tags.railway': 'Railway type',
            'tags.highway': 'Highway classification'
        }
        return descriptions.get(column, 'OSM tag data')
    
    def generate_all_examples(self, max_regions=None):
        """Generate all documentation examples."""
        
        print("Starting automatic documentation example generation...")
        
        regions_to_process = self.example_regions[:max_regions] if max_regions else self.example_regions
        
        generated_files = []
        
        for region in regions_to_process:
            for infrastructure_type in self.infrastructure_types:
                print(f"\nProcessing {region} - {infrastructure_type}...")
                
                try:
                    # Extract data
                    data = self.extract_sample_data(region, infrastructure_type, max_features=100)
                    
                    if not data:
                        print(f"No data found for {region} - {infrastructure_type}")
                        continue
                    
                    # Generate visualizations
                    map_image = self.generate_basic_map(region, infrastructure_type, data)
                    stats_image = self.generate_statistics_plot(region, infrastructure_type, data)
                    
                    # Generate markdown
                    markdown_content = self.generate_markdown_example(
                        region, infrastructure_type, data, map_image, stats_image
                    )
                    
                    # Save markdown
                    markdown_file = self.output_dir / f'{region}_{infrastructure_type}_example.md'
                    with open(markdown_file, 'w') as f:
                        f.write(markdown_content)
                    
                    generated_files.append(markdown_file)
                    print(f"Generated: {markdown_file}")
                    
                except Exception as e:
                    print(f"Error processing {region} - {infrastructure_type}: {e}")
                    continue
        
        # Generate index file
        self.generate_examples_index(generated_files)
        
        print(f"\nGenerated {len(generated_files)} example files")
        print(f"Output directory: {self.output_dir}")
        
        return generated_files
    
    def generate_examples_index(self, generated_files):
        """Generate an index of all examples."""
        
        index_content = f"""# Auto-Generated Examples

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

This section contains automatically generated examples showing Earth-OSM usage with different regions and infrastructure types.

## Available Examples

"""
        
        # Group by infrastructure type
        by_infrastructure = {}
        for file_path in generated_files:
            name = file_path.stem
            parts = name.split('_')
            if len(parts) >= 3:
                region = parts[0]
                infrastructure = '_'.join(parts[1:-1])  # Handle multi-word infrastructure types
                
                if infrastructure not in by_infrastructure:
                    by_infrastructure[infrastructure] = []
                by_infrastructure[infrastructure].append((region, file_path))
        
        for infrastructure, regions in by_infrastructure.items():
            index_content += f"\n### {infrastructure.title()} Infrastructure\n\n"
            for region, file_path in sorted(regions):
                relative_path = file_path.name
                index_content += f"- [{region.title()}]({relative_path})\n"
        
        index_content += f"""

## About These Examples

These examples are automatically generated to demonstrate Earth-OSM capabilities:

- **Small regions** are used for quick processing and clear visualization
- **Multiple infrastructure types** show the variety of data available
- **Real data** extracted from OpenStreetMap via GeoFabrik
- **Reproducible code** that you can run yourself

## Usage

Each example includes:

1. **Overview** with basic statistics
2. **Complete code** for data extraction and visualization  
3. **Generated maps** showing the infrastructure
4. **Statistical analysis** of the data
5. **Data samples** with column descriptions

## Customization

You can easily adapt these examples:

- Change the region to any [supported region](../regions.md)
- Extract different infrastructure types
- Modify the visualization style
- Add your own analysis

## Automation

These examples are regenerated automatically to keep the documentation current with:

- Latest Earth-OSM features
- Updated data from OpenStreetMap
- Current API usage patterns

---

*Examples generated with Earth-OSM*
"""
        
        index_file = self.output_dir / 'README.md'
        with open(index_file, 'w') as f:
            f.write(index_content)
        
        print(f"Generated examples index: {index_file}")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Generate Earth-OSM documentation examples')
    parser.add_argument('--output-dir', default='docs/generated-examples',
                       help='Output directory for generated examples')
    parser.add_argument('--max-regions', type=int, default=None,
                       help='Maximum number of regions to process')
    parser.add_argument('--clean', action='store_true',
                       help='Clean temporary data after generation')
    
    args = parser.parse_args()
    
    # Generate examples
    generator = DocsExampleGenerator(args.output_dir)
    generated_files = generator.generate_all_examples(args.max_regions)
    
    # Clean up temporary data if requested
    if args.clean:
        import shutil
        temp_dir = Path('./temp_data')
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print("Cleaned temporary data")
    
    print(f"\nDocumentation examples generated successfully!")
    print(f"Generated {len(generated_files)} examples in {args.output_dir}")


if __name__ == '__main__':
    main()