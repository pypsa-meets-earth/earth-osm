#!/usr/bin/env python3
"""
Quick visualization examples for Earth-OSM documentation.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Add earth_osm to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from earth_osm.eo import save_osm_data

def create_quick_visualizations():
    """Create visualizations using existing sample data or extracting simple examples."""
    
    output_dir = Path('docs/generated-examples/images')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎨 Creating Quick Earth-OSM Visualizations")
    print("=" * 50)
    
    generated_files = []
    
    # Set matplotlib style
    plt.style.use('default')
    sns.set_palette("husl")
    
    try:
        # 1. Extract power data for Monaco (small region)
        print("📊 Extracting power data for Monaco...")
        save_osm_data(
            region_list=['monaco'],
            primary_name='power',
            out_dir='./temp_viz/monaco_power',
            out_format=['csv', 'geojson'],
            mp=False
        )
        
        # Load and visualize Monaco power data
        gdf_substations = gpd.read_file('./temp_viz/monaco_power/out/MC_substation.geojson')
        gdf_generators = gpd.read_file('./temp_viz/monaco_power/out/MC_generator.geojson')
        
        # Create power infrastructure map
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot generators as green circles
        if len(gdf_generators) > 0:
            gdf_generators.plot(ax=ax, color='#2ecc71', markersize=60, alpha=0.8, label='Generators', edgecolor='darkgreen')
        
        # Plot substations as red squares
        if len(gdf_substations) > 0:
            gdf_substations.plot(ax=ax, color='#e74c3c', markersize=100, alpha=0.8, label='Substations', marker='s', edgecolor='darkred')
        
        ax.set_title('Monaco Power Infrastructure', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename1 = output_dir / 'monaco_power_infrastructure.png'
        plt.savefig(filename1, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files.append(filename1)
        print(f"  ✅ Generated: {filename1.name}")
        
        # 2. Create data analysis plots
        df_power = pd.read_csv('./temp_viz/monaco_power/out/MC_generator.csv')
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Monaco Power Infrastructure Analysis', fontsize=16, fontweight='bold')
        
        # Feature type distribution
        if 'Type' in df_power.columns:
            type_counts = df_power['Type'].value_counts()
            colors = ['#3498db', '#e74c3c', '#2ecc71'][:len(type_counts)]
            axes[0, 0].pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', colors=colors)
            axes[0, 0].set_title('OSM Element Types Distribution')
        
        # Power source types (if available)
        power_columns = [col for col in df_power.columns if 'power' in col.lower()]
        if power_columns:
            power_col = power_columns[0]
            power_types = df_power[power_col].value_counts().head(5)
            axes[0, 1].bar(range(len(power_types)), power_types.values, color='#f39c12')
            axes[0, 1].set_xticks(range(len(power_types)))
            axes[0, 1].set_xticklabels(power_types.index, rotation=45, ha='right')
            axes[0, 1].set_title('Power Source Types')
            axes[0, 1].set_ylabel('Count')
        
        # Data completeness
        completeness = (df_power.isnull().sum() / len(df_power) * 100).sort_values(ascending=False)
        top_missing = completeness.head(8)
        axes[1, 0].barh(range(len(top_missing)), top_missing.values, color='#95a5a6')
        axes[1, 0].set_yticks(range(len(top_missing)))
        axes[1, 0].set_yticklabels([col[:15] + '...' if len(col) > 15 else col for col in top_missing.index], fontsize=8)
        axes[1, 0].set_title('Missing Data by Column (%)')
        axes[1, 0].set_xlabel('Percentage Missing')
        
        # Feature count summary
        feature_counts = {
            'Generators': len(gdf_generators),
            'Substations': len(gdf_substations),
        }
        axes[1, 1].bar(feature_counts.keys(), feature_counts.values(), color=['#2ecc71', '#e74c3c'])
        axes[1, 1].set_title('Infrastructure Feature Count')
        axes[1, 1].set_ylabel('Number of Features')
        
        plt.tight_layout()
        filename2 = output_dir / 'monaco_power_analysis.png'
        plt.savefig(filename2, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files.append(filename2)
        print(f"  ✅ Generated: {filename2.name}")
        
    except Exception as e:
        print(f"❌ Error with Monaco power data: {e}")
    
    try:
        # 3. Extract highway data for Luxembourg (small region with good road coverage)
        print("🛣️  Extracting highway data for Luxembourg...")
        save_osm_data(
            region_list=['luxembourg'],
            primary_name='highway',
            out_dir='./temp_viz/luxembourg_highway',
            out_format=['geojson'],
            mp=False
        )
        
        # Load highway data
        highway_files = list(Path('./temp_viz/luxembourg_highway/out/').glob('LU_*.geojson'))
        
        if highway_files:
            fig, ax = plt.subplots(figsize=(14, 10))
            
            # Road hierarchy (plot in order - less important first)
            road_hierarchy = {
                'residential': ('#bdc3c7', 0.5, 0.3),
                'service': ('#95a5a6', 0.5, 0.3),
                'tertiary': ('#f1c40f', 1.0, 0.5),
                'secondary': ('#e67e22', 1.5, 0.6),
                'primary': ('#e74c3c', 2.0, 0.7),
                'trunk': ('#8e44ad', 2.5, 0.8),
                'motorway': ('#2c3e50', 3.0, 0.9)
            }
            
            plotted_types = []
            
            for highway_file in highway_files:
                road_type = highway_file.stem.replace('LU_', '')
                
                if road_type in road_hierarchy:
                    try:
                        gdf = gpd.read_file(highway_file)
                        if len(gdf) > 0:
                            color, linewidth, alpha = road_hierarchy[road_type]
                            gdf.plot(ax=ax, color=color, linewidth=linewidth, alpha=alpha, label=road_type.title())
                            plotted_types.append(road_type)
                    except Exception as e:
                        print(f"  Warning: Could not load {highway_file}: {e}")
            
            ax.set_title('Luxembourg Road Network by Classification', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Longitude', fontsize=12)
            ax.set_ylabel('Latitude', fontsize=12)
            
            if plotted_types:
                ax.legend(loc='best', frameon=True, fancybox=True, shadow=True)
            
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            filename3 = output_dir / 'luxembourg_highway_network.png'
            plt.savefig(filename3, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            generated_files.append(filename3)
            print(f"  ✅ Generated: {filename3.name}")
        
    except Exception as e:
        print(f"❌ Error with Luxembourg highway data: {e}")
    
    try:
        # 4. Create a comparison chart using different regions
        print("📈 Creating multi-region comparison...")
        
        regions_data = []
        for region in ['monaco', 'andorra']:
            try:
                save_osm_data(
                    region_list=[region],
                    primary_name='power',
                    out_dir=f'./temp_viz/{region}_power_comp',
                    out_format=['csv'],
                    mp=False
                )
                
                # Count features
                csv_files = list(Path(f'./temp_viz/{region}_power_comp/out/').glob('*.csv'))
                total_features = 0
                for csv_file in csv_files:
                    df = pd.read_csv(csv_file)
                    total_features += len(df)
                
                regions_data.append({
                    'region': region.title(),
                    'total_features': total_features
                })
                
            except Exception as e:
                print(f"  Warning: Could not process {region}: {e}")
        
        if len(regions_data) >= 2:
            df_comparison = pd.DataFrame(regions_data)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(df_comparison['region'], df_comparison['total_features'], 
                         color=['#3498db', '#e74c3c'], alpha=0.8)
            
            # Add value labels on bars
            for bar, value in zip(bars, df_comparison['total_features']):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                       str(value), ha='center', va='bottom', fontweight='bold')
            
            ax.set_title('Power Infrastructure Comparison', fontsize=16, fontweight='bold', pad=20)
            ax.set_ylabel('Total Power Features', fontsize=12)
            ax.set_xlabel('Region', fontsize=12)
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            filename4 = output_dir / 'region_comparison.png'
            plt.savefig(filename4, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            generated_files.append(filename4)
            print(f"  ✅ Generated: {filename4.name}")
        
    except Exception as e:
        print(f"❌ Error with comparison chart: {e}")
    
    # 5. Create a workflow diagram
    try:
        print("🔄 Creating workflow diagram...")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create a simple workflow visualization
        steps = [
            "1. Install\nearth-osm",
            "2. Choose\nRegion & Type", 
            "3. Extract\nOSM Data",
            "4. Load &\nAnalyze",
            "5. Visualize\nResults"
        ]
        
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
        
        # Create boxes for each step
        for i, (step, color) in enumerate(zip(steps, colors)):
            x = i * 2
            
            # Draw box
            box = plt.Rectangle((x-0.4, 0.3), 0.8, 0.4, facecolor=color, alpha=0.8, edgecolor='black')
            ax.add_patch(box)
            
            # Add text
            ax.text(x, 0.5, step, ha='center', va='center', fontweight='bold', fontsize=10, color='white')
            
            # Add arrow (except for last step)
            if i < len(steps) - 1:
                ax.arrow(x + 0.5, 0.5, 0.9, 0, head_width=0.05, head_length=0.1, 
                        fc='black', ec='black', alpha=0.7)
        
        ax.set_xlim(-1, len(steps) * 2)
        ax.set_ylim(0, 1)
        ax.set_title('Earth-OSM Workflow', fontsize=16, fontweight='bold', pad=30)
        ax.axis('off')
        
        plt.tight_layout()
        filename5 = output_dir / 'earth_osm_workflow.png'
        plt.savefig(filename5, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        generated_files.append(filename5)
        print(f"  ✅ Generated: {filename5.name}")
        
    except Exception as e:
        print(f"❌ Error with workflow diagram: {e}")
    
    # Clean up temporary data
    import shutil
    temp_dir = Path('./temp_viz')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print("\n🧹 Cleaned up temporary data")
    
    print(f"\n🎉 Generated {len(generated_files)} visualization files:")
    for file in generated_files:
        print(f"   📊 {file.name}")
    
    return generated_files

if __name__ == '__main__':
    create_quick_visualizations()