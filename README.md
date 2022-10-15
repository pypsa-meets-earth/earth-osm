## Getting Started
Install earth-osm
```bash
pip install git+https://github.com/pypsa-meets-earth/earth-osm.git
```

Extract osm data
```bash
# Example CLI command
earth_osm extract power --regions benin monaco  --features substation line
```
This will extract
*primary feature = power* for the *regions = benin* and *monaco* and the *secondary features = substation* and *line*.
By default the resulting .csv and .geojson are stored in `./earth_data/out`

Load the substation data for benin using pandas
```bash
# For Pandas
df_substations = pd.read_csv('./earth_data/out/BJ_raw_substations.csv')
# For GeoPandas
gdf_substations = gpd.read_file('./earth_data/out/BJ_raw_substations.geojson')
```

