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
    with open(file) as json_file:
        data = json.load(json_file)
    return data


# %%
def is_duplicate(data):
    data = [item for item in data if item["features"].get("is_duplicate") == False]
    return data


# %%
def get_location_fields(data, field):
    location_field = [
        d["features"].get("location", {}).get(field) for d in data if "features" in d
    ]
    return location_field


def get_feature_fields(data, field):
    feature_field = [d["features"].get(field) for d in data if "features" in d]
    return feature_field


# %%
def create_df(data):
    location_code = get_location_fields(data, "nuts_2_code")
    location_name = get_location_fields(data, "nuts_2_name")
    dup = get_feature_fields(data, "is_duplicate")
    skills = get_feature_fields(data, "skills")

    df = pd.DataFrame(data)
    df["duplicated"] = dup
    df["nuts_2_code"] = location_code
    df["nuts_2_name"] = location_name

    return df


# %%
def re_assign_brighton(df):
    brighton_names = list(
        df[df["job_location_raw"].str.contains("Brighton")]["job_location_raw"].unique()
    )
    for name in brighton_names:
        df.loc[df["job_location_raw"] == name, "nuts_2_code"] = "UKJ2"
        df.loc[
            df["job_location_raw"] == name, "nuts_2_name"
        ] = "Surrey, East And West Sussex"


# %%
def rem_cols(df):
    df.drop("features", axis=1, inplace=True)
    # Drop completely empty columns
    df.dropna(how="all", axis=1, inplace=True)
    df.drop(["__version__", "duplicated", "data_source"], axis=1, inplace=True)
