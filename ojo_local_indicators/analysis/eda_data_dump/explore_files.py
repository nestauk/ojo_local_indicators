# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     comment_magics: true
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.2
#   kernelspec:
#     display_name: ojo_local_indicators
#     language: python
#     name: ojo_local_indicators
# ---

# Import libraries
import pandas as pd
import numpy as np
import ojo_local_indicators
import ojo_local_indicators.pipeline.clean_data as cd
import json
import matplotlib.pyplot as plt
import missingno as msno


def percent_missing(df):
    percent_missing = df.isnull().sum() * 100 / len(df)
    missing_value_df = pd.DataFrame(
        {"column_name": df.columns, "percent_missing": percent_missing}
    )
    missing_value_df.sort_values("percent_missing", inplace=True)
    return missing_value_df


def time_index(df):
    df["created"] = pd.to_datetime(df["created"], format="%d-%m-%Y")
    df = df.set_index("created")
    df["jobs"] = 1
    return df


# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# Read in files
data_july = cd.open_data_dump(
    f"{project_directory}/inputs/data/job_ads_no_descriptions-15-07-2021.json"
)
data_april = cd.open_data_dump(
    f"{project_directory}/inputs/data/job_ads_no_descriptions-15-04-2021.json"
)

# Create dataframes
df_july = cd.create_df(data_july)
df_april = cd.create_df(data_april)

# +
pd.concat(
    {
        "July data": df_july["duplicated"].value_counts(normalize=True).mul(100),
        "April data": df_april["duplicated"].value_counts(normalize=True).mul(100),
    },
    axis=1,
).plot.bar()

plt.title("Percent job title duplicated - July/April data dumps")
plt.xlabel("Is duplicated")
plt.ylabel("Percent")
# -

df_july.drop(
    df_july[df_july["duplicated"] == True].index, inplace=True
)  # Remove duplicated jobs
df_april.drop(
    df_april[df_april["duplicated"] == True].index, inplace=True
)  # Remove duplicated jobs

cd.rem_cols(df_july)
cd.rem_cols(df_april)

cd.re_assign_brighton(df_july)
cd.re_assign_brighton(df_july)

# Slice for Sussex and non-sussex
df_ukj2 = df_july.loc[
    df_july["nuts_2_code"] == "UKJ2"
].copy()  # Slice by UKJ2 - Surrey, East and West Sussex
df_uk = df_july.loc[df_july["nuts_2_code"] != "UKJ2"].copy()  # Slice by not UKJ2
# Non Sussex random sample
df_uk_sample = df_uk.sample(n=9158, random_state=2)

print(df_ukj2.shape, df_uk_sample.shape)

# #### Exploratory data analysis

pd.concat(
    {
        "July data": df_july["nuts_2_name"].value_counts(normalize=True).mul(100),
        "April data": df_april["nuts_2_name"].value_counts(normalize=True).mul(100),
    },
    axis=1,
).plot(kind="barh", figsize=(10, 12))
plt.title("Percentage of jobs by Nuts 2 region")
plt.xlabel("Percent")
plt.ylabel("Nuts 2 Regions")

msno.matrix(df_july)

msno.matrix(df_april)

percent_missing_july = percent_missing(df_july)
percent_missing_april = percent_missing(df_april)

pd.concat(
    {
        "July data": percent_missing_july.tail(10),
        "April data": percent_missing_april.tail(10),
    },
    axis=1,
).plot(kind="barh", figsize=(7, 5))
plt.title("Percent missing - July/April data")
plt.xlabel("Percent")
plt.ylabel("Columns")

pd.concat(
    {
        "July data": df_july.nunique().sort_values().head(8),
        "April data": df_april.nunique().sort_values().head(8),
    },
    axis=1,
).plot(kind="barh", figsize=(7, 5))
plt.title("No unique values - July/April data (lower)")
plt.xlabel("Unique values")
plt.ylabel("Columns")

pd.concat(
    {
        "July data": df_july.nunique().sort_values().tail(8),
        "April data": df_april.nunique().sort_values().tail(8),
    },
    axis=1,
).plot(kind="barh", figsize=(7, 5))
plt.title("No unique values - July/April data (upper)")
plt.xlabel("Unique values")
plt.ylabel("Columns")

df_july = time_index(df_july)
df_april = time_index(df_april)

df_july["jobs"].resample("D").sum().plot(style="-o", figsize=(10, 5))
plt.title("Count of daily jobs posted - July data dump")
plt.xlabel("Created date")
plt.ylabel("Job count")

df_april["jobs"].resample("D").sum().plot(style="-o", figsize=(10, 5))
plt.title("Count of daily jobs posted - April data dump")
plt.xlabel("Created date")
plt.ylabel("Job count")

# Save id's to data outputs...
df_july.to_csv(f"{project_directory}/outputs/data/july_data_dump.csv", index=True)
df_ukj2.to_csv(f"{project_directory}/outputs/data/ukj2_july.csv", index=False)
df_uk_sample.to_csv(f"{project_directory}/outputs/data/uk_sample_july.csv", index=False)
