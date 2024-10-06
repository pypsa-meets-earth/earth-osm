
def get_overpass_data(region, primary_name, feature_name, data_dir, progress_bar):
    # returns data of the following form:
    # https://github.com/pypsa-meets-earth/earth-osm/issues/54

    print('\n'.join(['',
        f'-------- Overpass Function------- ',
        f'Primary Feature: {primary_name}',
        f'Feature Name: {feature_name}',
        f'Region Short: {region.short}',
        f'Data Directory = {data_dir}',
        f'Progress Bar = {progress_bar}'
    ]))


    # return op_dict, op_dict # hacky solution right now to return the same data twice
    raise NotImplementedError