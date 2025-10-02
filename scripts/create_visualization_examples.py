#!/usr/bin/env python3
"""
Create comprehensive visualization examples for Earth-OSM documentation.

This script generates real plots and visualizations for various infrastructure types
and use cases to showcase Earth-OSM capabilities.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import folium
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import contextily as ctx
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add earth_osm to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from earth_osm.eo import save_osm_data

class VisualizationGenerator:
    """Generate comprehensive visualizations for documentation."""
    
    def __init__(self, output_dir='docs/generated-examples'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.image_dir = self.output_dir / 'images'
        self.image_dir.mkdir(exist_ok=True)
        
        # Set matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
        
    def extract_data_for_visualization(self, region, infrastructure_type):
        """Extract data for a specific region and infrastructure type."""
        try:
            print(f"Extracting {infrastructure_type} data for {region}...")
            
            save_osm_data(
                region_list=[region],
                primary_name=infrastructure_type,
                out_dir=f'./temp_viz_data/{region}_{infrastructure_type}',
                out_format=['csv', 'geojson'],
                mp=False
            )
            
            region_code = region.upper()[:2]
            data_dir = Path(f'./temp_viz_data/{region}_{infrastructure_type}/out')
            
            # Load all files for this infrastructure type
            csv_files = list(data_dir.glob(f'{region_code}_*.csv'))
            geojson_files = list(data_dir.glob(f'{region_code}_*.geojson'))
            
            data = {'csv': {}, 'geojson': {}}
            
            for csv_file in csv_files:
                feature_name = csv_file.stem.replace(f'{region_code}_', '')
                df = pd.read_csv(csv_file)
                data['csv'][feature_name] = df
                print(f"  Loaded {len(df)} {feature_name} features (CSV)")
            
            for geojson_file in geojson_files:
                feature_name = geojson_file.stem.replace(f'{region_code}_', '')
                try:
                    gdf = gpd.read_file(geojson_file)
                    data['geojson'][feature_name] = gdf
                    print(f"  Loaded {len(gdf)} {feature_name} features (GeoJSON)")
                except Exception as e:
                    print(f"  Could not load {geojson_file}: {e}")
            
            return data
            
        except Exception as e:
            print(f"Error extracting data for {region} - {infrastructure_type}: {e}")
            return {'csv': {}, 'geojson': {}}
    
    def create_power_infrastructure_plots(self, region='netherlands'):
        """Create comprehensive power infrastructure visualizations."""
        print(f"\n=== Creating Power Infrastructure Visualizations for {region.title()} ===")
        
        data = self.extract_data_for_visualization(region, 'power')
        
        if not data['geojson']:
            print("No GeoJSON data available for power infrastructure")
            return []
        
        generated_files = []
        
        # 1. Infrastructure Overview Map
        fig, ax = plt.subplots(figsize=(14, 10))
        
        colors = {
            'substation': '#e74c3c',
            'line': '#3498db', 
            'generator': '#2ecc71',
            'tower': '#f39c12',
            'cable': '#9b59b6'
        }
        
        legend_handles = []
        
        for feature_type, gdf in data['geojson'].items():
            if len(gdf) == 0:
                continue
                
            color = colors.get(feature_type, '#95a5a6')
            
            if gdf.geometry.iloc[0].geom_type == 'Point':
                gdf.plot(ax=ax, color=color, markersize=40, alpha=0.8, label=feature_type.title())
            else:
                gdf.plot(ax=ax, color=color, linewidth=2, alpha=0.7, label=feature_type.title())
            
            legend_handles.append(feature_type.title())
        
        ax.set_title(f'{region.title()} Power Infrastructure Overview', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        
        if legend_handles:
            ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filename = self.image_dir / f'{region}_power_overview.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files.append(filename)
        print(f"  Generated: {filename.name}")
        
        # 2. Feature Distribution Analysis
        if data['csv']:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'{region.title()} Power Infrastructure Analysis', fontsize=16, fontweight='bold')
            
            # Combine all CSV data
            all_data = []
            for feature_type, df in data['csv'].items():
                df_copy = df.copy()
                df_copy['feature_type'] = feature_type
                all_data.append(df_copy)
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                
                # Feature type distribution
                feature_counts = combined_df['feature_type'].value_counts()
                axes[0, 0].pie(feature_counts.values, labels=feature_counts.index, autopct='%1.1f%%',
                              colors=[colors.get(ft, '#95a5a6') for ft in feature_counts.index])
                axes[0, 0].set_title('Distribution by Feature Type')
                
                # OSM element types
                if 'Type' in combined_df.columns:
                    type_counts = combined_df['Type'].value_counts()
                    axes[0, 1].bar(type_counts.index, type_counts.values, 
                                  color=['#3498db', '#e74c3c', '#2ecc71'][:len(type_counts)])
                    axes[0, 1].set_title('OSM Element Types')
                    axes[0, 1].set_ylabel('Count')
                
                # Voltage distribution (if available)
                voltage_data = []
                for col in combined_df.columns:
                    if 'voltage' in col.lower():
                        voltage_series = pd.to_numeric(combined_df[col], errors='coerce').dropna()
                        voltage_data.extend(voltage_series.tolist())
                
                if voltage_data:
                    axes[1, 0].hist(voltage_data, bins=20, alpha=0.7, color='#3498db', edgecolor='black')
                    axes[1, 0].set_title('Voltage Distribution')
                    axes[1, 0].set_xlabel('Voltage (V)')
                    axes[1, 0].set_ylabel('Count')
                else:
                    axes[1, 0].text(0.5, 0.5, 'No voltage data available', 
                                   ha='center', va='center', transform=axes[1, 0].transAxes)
                    axes[1, 0].set_title('Voltage Distribution')
                
                # Data completeness
                completeness = (combined_df.isnull().sum() / len(combined_df) * 100).sort_values(ascending=True)
                top_complete = completeness.tail(10)
                axes[1, 1].barh(range(len(top_complete)), top_complete.values, 
                               color='#2ecc71', alpha=0.7)
                axes[1, 1].set_yticks(range(len(top_complete)))
                axes[1, 1].set_yticklabels([col[:20] + '...' if len(col) > 20 else col for col in top_complete.index], 
                                          fontsize=8)
                axes[1, 1].set_title('Data Completeness (% Complete)')
                axes[1, 1].set_xlabel('Completeness %')
            
            plt.tight_layout()
            filename = self.image_dir / f'{region}_power_analysis.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            generated_files.append(filename)
            print(f"  Generated: {filename.name}")
        
        return generated_files
    
    def create_railway_infrastructure_plots(self, region='switzerland'):
        """Create railway infrastructure visualizations."""
        print(f"\n=== Creating Railway Infrastructure Visualizations for {region.title()} ===")
        
        data = self.extract_data_for_visualization(region, 'railway')
        
        if not data['geojson']:
            print("No GeoJSON data available for railway infrastructure")
            return []
        
        generated_files = []
        
        # Railway network visualization
        fig, ax = plt.subplots(figsize=(14, 10))
        
        colors = {
            'rail': '#2c3e50',
            'station': '#e74c3c',
            'platform': '#f39c12',
            'signal': '#9b59b6',
            'switch': '#1abc9c'
        }
        
        for feature_type, gdf in data['geojson'].items():
            if len(gdf) == 0:
                continue
                
            color = colors.get(feature_type, '#95a5a6')
            
            if gdf.geometry.iloc[0].geom_type == 'Point':
                markersize = 60 if feature_type == 'station' else 30
                gdf.plot(ax=ax, color=color, markersize=markersize, alpha=0.8, label=feature_type.title())
            else:
                linewidth = 3 if feature_type == 'rail' else 1.5
                gdf.plot(ax=ax, color=color, linewidth=linewidth, alpha=0.7, label=feature_type.title())
        
        ax.set_title(f'{region.title()} Railway Network', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.legend(loc='best', frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename = self.image_dir / f'{region}_railway_network.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files.append(filename)
        print(f"  Generated: {filename.name}")
        
        return generated_files
    
    def create_highway_infrastructure_plots(self, region='denmark'):
        """Create highway/road infrastructure visualizations."""
        print(f"\n=== Creating Highway Infrastructure Visualizations for {region.title()} ===")
        
        data = self.extract_data_for_visualization(region, 'highway')
        
        if not data['geojson']:
            print("No GeoJSON data available for highway infrastructure")
            return []
        
        generated_files = []
        
        # Road network by classification
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Road hierarchy colors (from most to least important)
        road_colors = {
            'motorway': '#e74c3c',
            'trunk': '#e67e22', 
            'primary': '#f39c12',
            'secondary': '#f1c40f',
            'tertiary': '#2ecc71',
            'residential': '#95a5a6',
            'service': '#bdc3c7'
        }
        
        # Plot in order of importance (least important first so important roads appear on top)
        road_order = ['service', 'residential', 'tertiary', 'secondary', 'primary', 'trunk', 'motorway']
        
        for road_type in road_order:
            if road_type in data['geojson'] and len(data['geojson'][road_type]) > 0:
                gdf = data['geojson'][road_type]
                color = road_colors.get(road_type, '#95a5a6')
                linewidth = 3 if road_type in ['motorway', 'trunk'] else 2 if road_type == 'primary' else 1
                
                gdf.plot(ax=ax, color=color, linewidth=linewidth, alpha=0.8, label=road_type.title())
        
        # Plot points (bus stops, traffic signals, etc.)
        point_features = ['bus_stop', 'traffic_signals', 'crossing']
        point_colors = {'bus_stop': '#3498db', 'traffic_signals': '#e74c3c', 'crossing': '#f39c12'}
        
        for feature_type in point_features:
            if feature_type in data['geojson'] and len(data['geojson'][feature_type]) > 0:
                gdf = data['geojson'][feature_type]
                color = point_colors.get(feature_type, '#9b59b6')
                gdf.plot(ax=ax, color=color, markersize=25, alpha=0.7, label=feature_type.replace('_', ' ').title())
        
        ax.set_title(f'{region.title()} Road Network by Classification', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.legend(loc='best', frameon=True, fancybox=True, shadow=True, ncol=2)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename = self.image_dir / f'{region}_highway_network.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files.append(filename)
        print(f"  Generated: {filename.name}")
        
        return generated_files
    
    def create_comparative_analysis(self, regions=['monaco', 'luxembourg', 'andorra']):
        """Create comparative analysis across multiple regions."""
        print(f"\n=== Creating Comparative Analysis ===")
        
        comparison_data = []
        
        for region in regions:
            print(f"Processing {region}...")
            data = self.extract_data_for_visualization(region, 'power')
            
            stats = {
                'region': region.title(),
                'total_features': 0,
                'substations': 0,
                'lines': 0,
                'generators': 0
            }
            
            for feature_type, df in data['csv'].items():
                stats['total_features'] += len(df)
                if feature_type == 'substation':
                    stats['substations'] = len(df)
                elif feature_type == 'line':
                    stats['lines'] = len(df)
                elif feature_type == 'generator':
                    stats['generators'] = len(df)
            
            comparison_data.append(stats)
        
        if not comparison_data:
            return []
        
        df_comparison = pd.DataFrame(comparison_data)
        
        # Create comparison plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Power Infrastructure Comparison Across Regions', fontsize=16, fontweight='bold')
        
        # Total features comparison
        axes[0, 0].bar(df_comparison['region'], df_comparison['total_features'], 
                       color=['#3498db', '#e74c3c', '#2ecc71'][:len(df_comparison)])
        axes[0, 0].set_title('Total Power Features by Region')
        axes[0, 0].set_ylabel('Number of Features')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Feature type breakdown
        feature_types = ['substations', 'lines', 'generators']
        x = np.arange(len(df_comparison))
        width = 0.25
        
        for i, feature_type in enumerate(feature_types):
            if feature_type in df_comparison.columns:
                axes[0, 1].bar(x + i*width, df_comparison[feature_type], width, 
                              label=feature_type.title(), alpha=0.8)
        
        axes[0, 1].set_title('Feature Types by Region')
        axes[0, 1].set_ylabel('Number of Features')
        axes[0, 1].set_xticks(x + width)
        axes[0, 1].set_xticklabels(df_comparison['region'], rotation=45)
        axes[0, 1].legend()
        
        # Infrastructure density (features per region - normalized)
        if len(df_comparison) > 1:
            max_features = df_comparison['total_features'].max()
            df_comparison['density_score'] = df_comparison['total_features'] / max_features * 100
            
            axes[1, 0].pie(df_comparison['density_score'], labels=df_comparison['region'], 
                          autopct='%1.1f%%', colors=['#3498db', '#e74c3c', '#2ecc71'][:len(df_comparison)])
            axes[1, 0].set_title('Relative Infrastructure Density')
        
        # Feature diversity (number of different feature types)
        diversity_scores = []
        for _, row in df_comparison.iterrows():
            diversity = sum(1 for ft in feature_types if row[ft] > 0)
            diversity_scores.append(diversity)
        
        axes[1, 1].bar(df_comparison['region'], diversity_scores, 
                       color=['#9b59b6', '#f39c12', '#1abc9c'][:len(df_comparison)])
        axes[1, 1].set_title('Infrastructure Diversity Score')
        axes[1, 1].set_ylabel('Number of Feature Types Present')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].set_ylim(0, len(feature_types))
        
        plt.tight_layout()
        filename = self.image_dir / 'comparative_power_analysis.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  Generated: {filename.name}")
        
        return [filename]
    
    def create_interactive_folium_map(self, region='monaco'):
        """Create an interactive Folium map."""
        print(f"\n=== Creating Interactive Map for {region.title()} ===")
        
        data = self.extract_data_for_visualization(region, 'power')
        
        if not data['geojson']:
            print("No GeoJSON data available for interactive map")
            return []
        
        # Calculate map center
        all_bounds = []
        for gdf in data['geojson'].values():
            if len(gdf) > 0:
                all_bounds.append(gdf.total_bounds)
        
        if not all_bounds:
            return []
        
        bounds_df = pd.DataFrame(all_bounds, columns=['minx', 'miny', 'maxx', 'maxy'])
        center_lat = (bounds_df['miny'].min() + bounds_df['maxy'].max()) / 2
        center_lon = (bounds_df['minx'].min() + bounds_df['maxx'].max()) / 2
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Add different feature types as layers
        colors = {
            'substation': 'red',
            'generator': 'green', 
            'line': 'blue',
            'cable': 'purple',
            'tower': 'orange'
        }
        
        for feature_type, gdf in data['geojson'].items():
            if len(gdf) == 0:
                continue
                
            feature_group = folium.FeatureGroup(name=feature_type.title())
            color = colors.get(feature_type, 'gray')
            
            for idx, row in gdf.iterrows():
                if row.geometry.geom_type == 'Point':
                    popup_text = f"<b>{feature_type.title()}</b><br>ID: {row.get('id', 'N/A')}"
                    
                    folium.Marker(
                        location=[row.geometry.y, row.geometry.x],
                        popup=folium.Popup(popup_text, max_width=200),
                        icon=folium.Icon(color=color, icon='flash' if feature_type == 'substation' else 'info')
                    ).add_to(feature_group)
                
                elif row.geometry.geom_type == 'LineString':
                    coords = [[point[1], point[0]] for point in row.geometry.coords]
                    popup_text = f"<b>{feature_type.title()}</b><br>ID: {row.get('id', 'N/A')}"
                    
                    folium.PolyLine(
                        locations=coords,
                        color=color,
                        weight=3,
                        opacity=0.8,
                        popup=folium.Popup(popup_text, max_width=200)
                    ).add_to(feature_group)
            
            feature_group.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save the map
        filename = self.image_dir / f'{region}_interactive_map.html'
        m.save(str(filename))
        print(f"  Generated: {filename.name}")
        
        return [filename]
    
    def generate_all_visualizations(self):
        """Generate all visualization examples."""
        print("🎨 Generating Comprehensive Earth-OSM Visualizations")
        print("=" * 60)
        
        all_generated_files = []
        
        try:
            # Power infrastructure visualizations
            files = self.create_power_infrastructure_plots('netherlands')
            all_generated_files.extend(files)
            
            # Railway infrastructure
            files = self.create_railway_infrastructure_plots('switzerland') 
            all_generated_files.extend(files)
            
            # Highway infrastructure
            files = self.create_highway_infrastructure_plots('denmark')
            all_generated_files.extend(files)
            
            # Comparative analysis
            files = self.create_comparative_analysis(['monaco', 'luxembourg', 'andorra'])
            all_generated_files.extend(files)
            
            # Interactive map
            files = self.create_interactive_folium_map('monaco')
            all_generated_files.extend(files)
            
        except Exception as e:
            print(f"Error during visualization generation: {e}")
        
        print(f"\n✅ Generated {len(all_generated_files)} visualization files:")
        for file in all_generated_files:
            print(f"   📊 {file.name}")
        
        return all_generated_files

def main():
    """Main function to generate visualizations."""
    generator = VisualizationGenerator()
    generated_files = generator.generate_all_visualizations()
    
    # Clean up temporary data
    import shutil
    temp_dir = Path('./temp_viz_data')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print("\n🧹 Cleaned up temporary data")
    
    print(f"\n🎉 Visualization generation complete!")
    print(f"📁 Files saved to: {generator.image_dir}")
    
    return generated_files

if __name__ == '__main__':
    main()