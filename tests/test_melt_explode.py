import os
from earth_osm.eo import get_osm_data
from earth_osm.utils import tags_melt, tags_explode, columns_melt

def test_column_melt(shared_data_dir):
    region = "nigeria"
    primary_name = "power"
    feature_name = "substation"
    mp = True
    update = False
    data_dir = shared_data_dir

    df = get_osm_data(
        region, 
        primary_name, 
        feature_name,
        data_dir=data_dir
        )

    df_cols = list(df.columns)

    df_col_melt = columns_melt(df.copy(), ['refs'])
    assert df_cols == list(df.columns) # check if original df is same
    df_col_melt_cols = list(df_col_melt.columns)

    df_exp  = tags_explode(df_col_melt.copy())
    assert df_col_melt_cols == list(df_col_melt.columns) # check if original df is same
    # print(df_exp.columns)

    # print difference in columns
    print(set(df_exp.columns.tolist()) - set(df.columns.tolist()))
    print(set(df.columns.tolist()) - set(df_exp.columns.tolist()))

    assert set(df_exp.columns.tolist()) == set(df.columns.tolist())

    # check the types of the column refs, row by row
    for i in range(len(df)):
        if not df['refs'].iloc[i] == df_exp['refs'].iloc[i]:
            # check if nan
            if str(df['refs'].iloc[i]) == 'nan' and str(df_exp['refs'].iloc[i]) == 'nan':
                continue
            
            print(f'Row {i} is not equal')
            i_ = i
            print(df['refs'].iloc[i_])
            print(df_exp['refs'].iloc[i_])

            print(type(df['refs'].iloc[i_]))
            print(type(df_exp['refs'].iloc[i_]))


    for col in df.columns:
        assert df[col].equals(df_exp[col]), f'Column {col} is not equal'

    
def test_melt(shared_data_dir):
    region = "nigeria"
    primary_name = "power"
    feature_name = "substation"
    mp = True
    update = False
    data_dir = shared_data_dir

    df = get_osm_data(
        region, 
        primary_name, 
        feature_name,
        data_dir=data_dir
        )
    
    df_cols = list(df.columns)

    # melt tags
    df_melt = tags_melt(df.copy(), nan_threshold=0.75)
    assert df_cols == list(df.columns) # check if original df is same
    df_melt_cols = list(df_melt.columns)
    assert 'other_tags' in df_melt.columns
    # print(df_melt['other_tags'])

    # explode tags
    df_explode = tags_explode(df_melt.copy())
    assert df_melt_cols == list(df_melt.columns) # check if original df is same
    # print(df_explode.columns)

    # print difference
    print(set(df.columns.tolist()) - set(df_explode.columns.tolist()))
    print(set(df_explode.columns.tolist()) - set(df.columns.tolist()))

  
    assert set(df.columns.tolist()) == set(df_explode.columns.tolist())    

    # print length of columns for all
    print(f'Length of df columns: {len(df.columns)}')
    print(f'Length of df_melt columns: {len(df_melt.columns)}')
    print(f'Length of df_explode columns: {len(df_explode.columns)}')

    # check if each column has the same length and values, df_exp and df should be same
    for col in df.columns:
        assert df[col].equals(df_explode[col])



if __name__ == '__main__':
    test_column_melt()
    test_melt()