# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     comment_magics: true
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
import numpy as np
import ojo_local_indicators
import json
import matplotlib.pyplot as plt
import missingno as msno
from sklearn.model_selection import train_test_split

# %%
# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# %% [markdown]
# Merge data-dumps as one dataframe

# %%
# Open json files

# July
with open(
    f"{project_directory}/inputs/data/job_ads_no_descriptions-15-07-2021.json"
) as json_file:
    data_july = json.load(json_file)
# April
with open(
    f"{project_directory}/inputs/data/job_ads_no_descriptions-15-04-2021.json"
) as json_file:
    data_april = json.load(json_file)

# %%
data = data_july + data_april
df = pd.DataFrame(data)

# %%
df.info()

# %%
print(len(data))

# %%
# Access fields from nested dictionary
location_code = [
    d["features"].get("location", {}).get("nuts_2_code")
    for d in data
    if "features" in d
]
location_name = [
    d["features"].get("location", {}).get("nuts_2_name")
    for d in data
    if "features" in d
]
dup = [d["features"].get("is_duplicate") for d in data if "features" in d]

df["duplicated"] = dup
df["nuts_2_code"] = location_code
df["nuts_2_name"] = location_name

# %%
df["duplicated"].value_counts().plot(kind="barh")
plt.title("Count of duplicated job entries")

# %%
# Removing 'is duplicate = True'
print(df.shape)
df.drop(df[df["duplicated"] == True].index, inplace=True)  # Remove duplicated
print(df.shape)

# %%
plt.figure(figsize=(15, 10))
df["nuts_2_name"].value_counts().plot(kind="barh")
plt.title("Count of jobs by Nuts 2 region")

# %%
msno.matrix(df)

# %%
msno.heatmap(df)

# %%
percent_missing = df.isnull().sum() * 100 / len(df)
missing_value_df = pd.DataFrame(
    {"column_name": df.columns, "percent_missing": percent_missing}
)
missing_value_df.sort_values("percent_missing", inplace=True)
missing_value_df.tail(10).plot(kind="barh", figsize=(7, 5))

# %%
df.drop("features", axis=1, inplace=True)

# %%
# Drop completely empty columns
df.dropna(how="all", axis=1, inplace=True)

# %%
df.nunique().sort_values().head(5)

# %%
df.drop(["__version__", "duplicated", "data_source"], axis=1, inplace=True)

# %%
ax = df.nunique().sort_values().head(8).plot(kind="barh", figsize=(7, 5))

# %%
ax = df.nunique().sort_values().tail(8).plot(kind="barh", figsize=(7, 5))

# %%
df.head(1)

# %%
df["created"] = pd.to_datetime(df["created"], format="%d-%m-%Y")
df = df.set_index("created")

# %%
print(df.index.min(), df.index.max())

# %%
df["jobs"] = 1

# %%
df["jobs"].resample("M").sum().plot(kind="bar", figsize=(10, 5))
plt.xticks((0, 1, 2, 3, 4), ("March", "April", "May", "June", "July"))

# %%
df["jobs"].resample("D").sum().plot(style="-o", figsize=(10, 5))

# %%
percent_company = pd.concat(
    [
        df["company_raw"].value_counts(),
        df["company_raw"].value_counts(normalize=True).mul(100),
    ],
    axis=1,
    keys=("counts", "percentage"),
)
percent_company["percentage"].head(10).plot(kind="barh")
plt.title("Top ten companies posting jobs - all locations")

# %%
df_ukj2 = df.loc[df["nuts_2_code"] == "UKJ2"]

percent_company = pd.concat(
    [
        df_ukj2["company_raw"].value_counts(),
        df_ukj2["company_raw"].value_counts(normalize=True).mul(100),
    ],
    axis=1,
    keys=("counts", "percentage"),
)
percent_company["percentage"].head(10).plot(kind="barh")
plt.title("Top ten companies posting jobs - UKJ2")

# %%
percent_job = pd.concat(
    [
        df["job_title_raw"].value_counts(),
        df["job_title_raw"].value_counts(normalize=True).mul(100),
    ],
    axis=1,
    keys=("counts", "percentage"),
)
percent_job["percentage"].head(10).plot(kind="barh")
plt.title("Top ten job titles - all locations")

# %%
percent_job = pd.concat(
    [
        df_ukj2["job_title_raw"].value_counts(),
        df_ukj2["job_title_raw"].value_counts(normalize=True).mul(100),
    ],
    axis=1,
    keys=("counts", "percentage"),
)
percent_job["percentage"].head(10).plot(kind="barh")
plt.title("Top ten job titles - UKJ2")

# %%
df.head(1)

# %%
data[0]

# %% [markdown]
# #### Sampling

# %% [markdown]
# 1. Take sample where nuts values are missing
# 2. Take sample across nuts regions (non sussex)
# 3. Take sample sussex

# %%
# Empty nuts2 values

# %% [markdown]
# Difference between empty nut2 rows and full...

# %%
empty_nuts2 = df[df.nuts_2_code.isna()].copy()
empty_sample = empty_nuts2.sample(n=500, random_state=1)

# %%
print(empty_sample.shape, empty_nuts2.shape)

# %%
empty_sample = empty_sample[["id", "job_location_raw"]]

# %%
# empty_sample.to_excel(f"{project_directory}/outputs/data/empty_sample_dq.xlsx", index=False)

# %%
# Sample from sussex nuts2

# %%
# Slice by UKJ2 - Surrey, East and West Sussex
df_ukj2 = df.loc[df["nuts_2_code"] == "UKJ2"]

# %%
df_ukj2_sample = df_ukj2.sample(frac=0.1, random_state=1)
df_ukj2_sample = df_ukj2_sample[
    ["id", "job_title_raw", "job_location_raw", "nuts_2_code", "nuts_2_name"]
]
# df_ukj2_sample.to_excel(f"{project_directory}/outputs/data/ukj2_sample_dq.xlsx", index=False)

# %%
# Slice where location not UKJ2 - Surrey, East and West Sussex
df_not_ukj2 = df.loc[df["nuts_2_code"] != "UKJ2"].copy()

# %%
df_not_ukj2.dropna(subset=["nuts_2_code"], inplace=True)

# %%
df_not_ukj2_sample = df_not_ukj2.sample(n=500, random_state=1)
df_not_ukj2_sample = df_not_ukj2_sample[
    ["id", "job_location_raw", "nuts_2_code", "nuts_2_name"]
]
# df_not_ukj2_sample.to_excel(f"{project_directory}/outputs/data/other_regions_sample_dq.xlsx", index=False)
