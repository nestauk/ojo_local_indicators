# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     comment_magics: true
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.2
#   kernelspec:
#     display_name: ojo_local_indicators
#     language: python
#     name: ojo_local_indicators
# ---

# %%
# Import libraries
import pandas as pd
import numpy as np
import ojo_local_indicators
import json


# %%
def open_data_dump(file):
    """Loads and returns data from JSON file."""
    with open(file) as json_file:
        data = json.load(json_file)
    return data


# %%
def is_duplicate(data):
    """Keeps only dictionaries where is_duplicate
    is False in list of dictionaries."""
    data = [item for item in data if item["features"].get("is_duplicate") == False]
    return data


# %%
def get_location_fields(data, field):
    """Get field from location dictionary within list of dictionaries.
    Fields are nut2 name and code."""
    location_field = [
        d["features"].get("location", {}).get(field) for d in data if "features" in d
    ]
    return location_field


def get_feature_fields(data, field):
    """Get field in feature dict in list of dicts."""
    feature_field = [d["features"].get(field) for d in data if "features" in d]
    return feature_field


# %%
def create_df(data):
    """Creates a dataframe from the json data and lists
    created from the get_location_fields and
    get_feature_fields functions."""
    # Calling functions to get fields from dicts within list of dicts
    location_code = get_location_fields(data, "nuts_2_code")
    location_name = get_location_fields(data, "nuts_2_name")
    dup = get_feature_fields(data, "is_duplicate")
    # Create df and add lists created above
    df = pd.DataFrame(data)
    df["duplicated"] = dup
    df["nuts_2_code"] = location_code
    df["nuts_2_name"] = location_name
    # Return df
    return df


# %%
def re_assign_brighton(df):
    """Find and replace nuts 2 codes and names
    with correct Sussex fields where the raw job
    title contains Brighton."""
    # Find 'Brighton' in job_location_raw and return as a list.
    brighton_names = list(
        df[df["job_location_raw"].str.contains("Brighton")]["job_location_raw"].unique()
    )
    # Find cases where Brighton name in job_location_raw and update nuts 2 name and code
    for name in brighton_names:
        df.loc[df["job_location_raw"] == name, "nuts_2_code"] = "UKJ2"
        df.loc[
            df["job_location_raw"] == name, "nuts_2_name"
        ] = "Surrey, East And West Sussex"


# %%
def remove_cols(df):
    """Drop features col and any empty cols."""
    df.drop("features", axis=1, inplace=True)
    # Drop completely empty columns
    df.dropna(how="all", axis=1, inplace=True)
    df.drop(["__version__", "duplicated", "data_source"], axis=1, inplace=True)


# %%
def percent_missing(df):
    """Create df showing percent missing per col."""
    # Calculate percent missing per col
    percent_missing = df.isnull().sum() * 100 / len(df)
    # Create df
    missing_value_df = pd.DataFrame(
        {"column_name": df.columns, "percent_missing": percent_missing}
    )
    # Sort by percent missing
    missing_value_df.sort_values("percent_missing", inplace=True)
    return missing_value_df  # Return df


# %%
def time_index(df):
    """Format df from timeseries plots."""
    # Change created to datetime
    df["created"] = pd.to_datetime(df["created"], format="%d-%m-%Y")
    # Set created as index
    df = df.set_index("created")
    # Set column to 1 (for plotting count)
    df["jobs"] = 1
    # Return df
    return df
