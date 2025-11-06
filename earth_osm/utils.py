__author__ = "PyPSA meets Earth"
__copyright__ = "Copyright 2022, The PyPSA meets Earth Initiative"
__license__ = "MIT"

"""Utilities functions for earth_osm

This module contains utilities functions for handling OSM data.

"""

import ast
import logging
import pandas as pd

logger = logging.getLogger("eo.utils")
logger.setLevel(logging.INFO)


def iter_tag_values(value):
    """Yield normalized tag values from a raw OSM tag payload."""

    if value is None:
        return

    if isinstance(value, (list, tuple, set)):
        for item in value:
            yield from iter_tag_values(item)
        return

    text = str(value)
    for part in text.split(";"):
        token = part.strip()
        if token:
            yield token


def tag_value_matches(value, feature_name):
    """Return True when the provided tag value matches the requested feature."""

    if feature_name.startswith("ALL_"):
        return True

    for token in iter_tag_values(value):
        if token == feature_name:
            return True
    return False


def tags_melt(df_exp, nan_threshold=0.75):
    # Find columns with high percentage of NaN values
    high_nan_cols = df_exp.columns[df_exp.isnull().mean() > nan_threshold]

    logger.debug(f"Melting tags from the following columns: {high_nan_cols}")

    df_high_nan = df_exp[high_nan_cols]

    # assert other_tags column does not already exist, if it does,
    assert 'other_tags' not in df_exp.columns, "other_tags column already exists in dataframe"
    df_exp['other_tags'] = df_high_nan.apply(lambda x: x.dropna().to_dict(), axis=1)

    # drop {} in other tags so that its nan
    df_exp['other_tags'] = df_exp['other_tags'].apply(lambda x: x if x != {} else None)

    df_exp.drop(columns=high_nan_cols, inplace=True)
    return df_exp


def columns_melt(df_exp, columns_to_move):
    def concat_melt(row, col):
        # check if value to melt is NaN
        if str(row[col]) == 'nan':
            return None
        # if other_tags column does not exist, no need to concat
        # or if other tags exist, but is empty/none/nan, still no need to concat
        if (
            'other_tags' not in row.keys()
            or row['other_tags'] == {}
            or row['other_tags'] is None
            or str(row['other_tags']) == 'nan'
        ):
            return {col: row[col]}

        # before concating, check if the column already exists in other_tags
        if col in row['other_tags']:
            logger.warning(f"'{col}' already exists in 'row'.")
        return {**row['other_tags'], col: row[col]}

    # Move specified columns to other_tags
    for col in columns_to_move:
        if col in df_exp.columns:
            df_exp['other_tags'] = df_exp.apply(lambda x: concat_melt(x, col), axis=1)
            df_exp.drop(columns=col, inplace=True)
        else:
            logger.warning(f"Column '{col}' not found in dataframe.")

    return df_exp


def tags_explode(df_melt):
    # check if df_melt has column 'other_tags'
    if 'other_tags' not in df_melt.columns:
        logger.warning("df is not melted, but tags_explode was called")
        return df_melt

    # check if other_tags is empty
    if df_melt['other_tags'].isnull().all():
        logger.debug("nothing to explode, other_tags is empty, returning df with dropped other_tags column")
        # drop other_tags column
        df_melt.drop(columns=['other_tags'], inplace=True)
        return df_melt

    # convert stringified dicts to dict
    df_melt['other_tags'] = df_melt['other_tags'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )

    # explode other_tags column into multiple columns
    df_exploded = df_melt.join(pd.json_normalize(df_melt['other_tags']))

    # drop the original other_tags column
    df_exploded.drop(columns=['other_tags'], inplace=True)

    return df_exploded
