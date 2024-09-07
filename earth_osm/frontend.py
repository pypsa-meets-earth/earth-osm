import streamlit as st
import sys
# print folder structure and current dir
print(os.listdir())
print(os.getcwd())
print(os.listdir("../"))
print(sys.path)
sys.path.append("../")
sys.path.append("../earth_osm")
import os
import subprocess
subprocess.call(["make", "install-st"])

import geopandas as gpd

import earth_osm.eo as eo
import earth_osm.tagdata as tagdata
import earth_osm.gfk_data as gfk_data

import folium
from streamlit_folium import folium_static

st.set_page_config(page_title="Earth-OSM", page_icon="🌍")

st.title("Earth-OSM")
st.markdown("Extract Infrastructure data from OpenStreetMap")

# Sidebar
st.sidebar.header("Settings")

# Primary feature selection
primary = st.sidebar.selectbox("Select Primary Feature", tagdata.get_primary_list())

# Region selection
all_regions = gfk_data.get_all_valid_list()
region = st.sidebar.selectbox("Select Region", all_regions)

# Feature selection
all_features = tagdata.get_feature_list(primary)
feature = st.sidebar.selectbox("Select Feature", all_features)

# Other options
data_dir = st.sidebar.text_input("Data Directory", value="./earth_data")

# Extract Data button
if st.sidebar.button("Extract Data"):
    with st.spinner("Extracting data..."):
        try:
            eo.save_osm_data(
                region_list=[region],
                primary_name=primary,
                feature_list=[feature],
                update=True,
                mp=False,
                data_dir=data_dir,
                out_dir=data_dir,
                out_format={"geojson"},
                out_aggregate=False,
            )
            st.sidebar.success("Data extraction completed successfully!")
        except Exception as e:
            st.sidebar.error(f"An error occurred during data extraction: {str(e)}")

# Main content
st.header("Earth-OSM Data Extractor")
st.markdown("Use the sidebar to configure and extract OpenStreetMap data.")

# Display extracted data
st.header("Extracted Data Visualization")

out_dir = os.path.join(data_dir, "out")
if os.path.exists(out_dir):
    file_name = f"{region}_{primary}_{feature}.geojson"
    file_path = os.path.join(out_dir, file_name)
    
    if os.path.exists(file_path):
        gdf = gpd.read_file(file_path)
        
        # Display the data as a table
        st.subheader("Data Preview")
        df = gdf.drop(columns=['geometry'])
        st.write(df.head())
        
        # Visualize the data on a map
        st.subheader("Map Visualization")
        
        # Convert to WGS84 if not already
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")
        
        # Create a map centered on the mean coordinates of the data
        center_lat, center_lon = gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
        
        # Add the GeoJSON data to the map
        folium.GeoJson(gdf).add_to(m)
        
        # Display the map
        folium_static(m)
    else:
        st.info("No extracted data available. Use the 'Extract Data' button to generate data.")
else:
    st.info("No extracted data available. Use the 'Extract Data' button to generate data.")

# Add some information about the project
st.markdown("---")
st.markdown("## About Earth-OSM")
st.markdown("""
Earth-OSM is a tool for extracting infrastructure data from OpenStreetMap (OSM). 
It provides both a Python API and a CLI interface to extract data for various infrastructure types.

Key Features:
- 🔌 Extracts infrastructure data from OSM
- 🧹 Cleans and standardizes the data
- 🚀 No API rate limits (data served from GeoFabrik)
- 🐍 Provides a Python API
- 🖥️ Supports multiprocessing for faster extraction
- 📊 Outputs data in .csv and .geojson formats
- 🌍 Supports global data extraction
""")

st.markdown("[GitHub Repository](https://github.com/pypsa-meets-earth/earth-osm) | [Documentation](https://pypsa-meets-earth.github.io/earth-osm/)")
