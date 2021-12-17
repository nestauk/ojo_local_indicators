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

import ojo_local_indicators
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ojo_local_indicators.pipeline.clean_data as cd

# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# Open July dataframe
df_july = pd.read_csv(f"{project_directory}/outputs/data/july_data_dump.csv")

# Open labelled samples
sample_label = pd.read_excel("archive/sample_data_dump.xlsx")

# +
sample_label = sample_label[
    [
        "id",
        "job_location_raw",
        "Nuts 2 Name",
        "Nuts 3 Name",
        "Is the raw location field assigned to the correct Nuts 2 region?",
        "Is the raw location field assigned to the correct Nuts 3 region?",
    ]
].copy()

sample_label["label_match"] = sample_label[
    "Is the raw location field assigned to the correct Nuts 2 region?"
].eq(sample_label["Is the raw location field assigned to the correct Nuts 3 region?"])
# -

sample_label.label_match.value_counts().plot(kind="bar")

sample_label[
    "Is the raw location field assigned to the correct Nuts 2 region?"
].value_counts().plot(kind="bar")

sample_label[
    "Is the raw location field assigned to the correct Nuts 3 region?"
].value_counts().plot(kind="bar")

# +
sample_label["nut_2_correct"] = sample_label[
    "Is the raw location field assigned to the correct Nuts 2 region?"
]
sample_label["nut_3_correct"] = sample_label[
    "Is the raw location field assigned to the correct Nuts 3 region?"
]

sample_label["nut_2_correct"].replace(
    "No region assigned - incorrect", "No", inplace=True
)
sample_label["nut_2_correct"].replace(
    "No region assigned - correct", "Yes", inplace=True
)
sample_label["nut_3_correct"].replace(
    "No region assigned - incorrect", "No", inplace=True
)
sample_label["nut_3_correct"].replace(
    "No region assigned - correct", "Yes", inplace=True
)

# +
y = [352, 148]
labels = ["Yes", "No"]
fig, ax = plt.subplots(figsize=(6, 6))

# Capture each of the return elements.
patches, texts, pcts = ax.pie(
    y,
    labels=labels,
    autopct="%.1f%%",
    wedgeprops={"linewidth": 0, "edgecolor": "white"},
    textprops={"size": "x-large"},
)
# Style just the percent values.
plt.setp(pcts, color="white", fontweight="bold")
ax.set_title("Nuts 2 regions correct (direct from sample)", fontsize=18)
plt.tight_layout()

# +
y = [351, 148]
labels = ["Yes", "No"]
fig, ax = plt.subplots(figsize=(6, 6))

# Capture each of the return elements.
patches, texts, pcts = ax.pie(
    y,
    labels=labels,
    autopct="%.1f%%",
    wedgeprops={"linewidth": 0, "edgecolor": "white"},
    textprops={"size": "x-large"},
)
# Style just the percent values.
plt.setp(pcts, color="white", fontweight="bold")
ax.set_title("Nuts 3 regions correct", fontsize=18)
plt.tight_layout()
# -

sample_label.rename({"Nuts 2 Name": "nuts_2_name"}, axis=1, inplace=True)
sample_label["sample"] = "yes"

df_matched = pd.merge(
    df_july,
    sample_label[["job_location_raw", "sample", "nut_2_correct"]],
    how="left",
    on="job_location_raw",
)

print(
    "Number of jobs in the sample location: "
    + str(list(df_matched["sample"].value_counts()))
)
print(
    "Number of unique raw locations in July dataset: "
    + str(df_matched["job_location_raw"].nunique())
)
print("Percent of July dataset assessed: " + str((20828 / 263142) * 100))

df_july_sample = df_matched[df_matched["sample"] == "yes"].copy()

# +
y = [16452, 4376]
labels = ["Yes", "No"]
fig, ax = plt.subplots(figsize=(6, 6))

# Capture each of the return elements.
patches, texts, pcts = ax.pie(
    y,
    labels=labels,
    autopct="%.1f%%",
    wedgeprops={"linewidth": 0, "edgecolor": "white"},
    textprops={"size": "x-large"},
)
# Style just the percent values.
plt.setp(pcts, color="white", fontweight="bold")
ax.set_title("Nuts 2 regions correct (location weighted)", fontsize=18)
plt.tight_layout()
# -

# #### Summary
#
# - Nuts 2 accuracy (sample): 70.4%
# - Nuts 3 accuracy (sample) 70.3%
# - Nuts 2 accuracy (sample - frequencies): 79%
# - Percentage of whole July dataset covered: 7.9%
# - Percentage of Sussex regions covered

# #### Top 20 locations

((df_july["job_location_raw"].value_counts(normalize=True).head(5)) * 100)

((df_july["job_location_raw"].value_counts(normalize=True).head(20)) * 100).plot(
    kind="barh", figsize=(15, 7)
)
plt.title("Percentage share of top 20 raw locations (in the July data dump)")

((df_july["job_location_raw"].value_counts(normalize=True).head(20)) * 100).sum()

top_20 = list(df_july["job_location_raw"].value_counts(normalize=True).head(20).index)
# df_july[df_july['job_location_raw'].isin(top_20)].drop_duplicates(subset=['job_location_raw', 'nuts_2_name'])

# +
# df_july[df_july['job_location_raw'].isin(top_20)].drop_duplicates(subset=['job_location_raw', 'nuts_2_name']).to_csv('top20locations.csv', index=False)
# -

top_locations = pd.read_excel("archive/top_locations_data_dump.xlsx")

top_locations.drop(
    ["Notes", "If incorrectly assigned, what is the correct Nuts 2 region"],
    axis=1,
    inplace=True,
)

top_locations[
    "Is the raw location field assigned to the correct Nuts 2 region?"
].value_counts()

# +
top_locations["nut_2_correct"] = top_locations[
    "Is the raw location field assigned to the correct Nuts 2 region?"
]

top_locations["nut_2_correct"].replace(
    "No region assigned - incorrect", "No", inplace=True
)
top_locations["nut_2_correct"].replace(
    "No region assigned - correct", "Yes", inplace=True
)

# +
y = [17, 3]
labels = ["Yes", "No"]
fig, ax = plt.subplots(figsize=(6, 6))

# Capture each of the return elements.
patches, texts, pcts = ax.pie(
    y,
    labels=labels,
    autopct="%.1f%%",
    wedgeprops={"linewidth": 0, "edgecolor": "white"},
    textprops={"size": "x-large"},
)
# Style just the percent values.
plt.setp(pcts, color="white", fontweight="bold")
ax.set_title("Nuts 2 regions correct (direct from sample)", fontsize=18)
plt.tight_layout()
# -

top_locations["sample"] = "yes"
df_matched = pd.merge(
    df_july,
    top_locations[["job_location_raw", "sample", "nut_2_correct"]],
    how="left",
    on="job_location_raw",
)

print(
    "Number of jobs in the sample location: "
    + str(list(df_matched["sample"].value_counts()))
)
print(
    "Number of unique raw locations in July dataset: "
    + str(df_matched["job_location_raw"].nunique())
)
print("Percent of July dataset assessed: " + str((93481 / 263142) * 100))

df_july_locations = df_matched[df_matched["sample"] == "yes"].copy()

# +
y = [86012, 7469]
labels = ["Yes", "No"]
fig, ax = plt.subplots(figsize=(6, 6))

# Capture each of the return elements.
patches, texts, pcts = ax.pie(
    y,
    labels=labels,
    autopct="%.1f%%",
    wedgeprops={"linewidth": 0, "edgecolor": "white"},
    textprops={"size": "x-large"},
)
# Style just the percent values.
plt.setp(pcts, color="white", fontweight="bold")
ax.set_title("Nuts 2 regions correct (location weighted)", fontsize=18)
plt.tight_layout()
# -

# ### Sussex location DQA

data_july = cd.open_data_dump(
    f"{project_directory}/inputs/data/job_ads_no_descriptions-15-07-2021.json"
)

data_july = cd.is_duplicate(data_july)
df_july = cd.create_df(data_july)
cd.rem_cols(df_july)

# +
### Take top N locations in the Sussex Nuts 2 field
# -

(
    (
        df_july.loc[(df_july["nuts_2_code"] == "UKJ2")]
        .copy()["job_location_raw"]
        .value_counts(normalize=True)
        .head(30)
    )
    * 100
)

# Percent of locations covered by top 55
(
    (
        df_july.loc[(df_july["nuts_2_code"] == "UKJ2")]
        .copy()["job_location_raw"]
        .value_counts(normalize=True)
        .head(55)
    )
    * 100
).sum()

# Number of unique locations
df_july.loc[(df_july["nuts_2_code"] == "UKJ2")].copy()["job_location_raw"].nunique()

top_55 = list(
    df_july.loc[(df_july["nuts_2_code"] == "UKJ2")]
    .copy()["job_location_raw"]
    .value_counts(normalize=True)
    .head(55)
    .index
)
sussex_top55 = df_july[df_july["job_location_raw"].isin(top_55)].drop_duplicates(
    subset=["job_location_raw", "nuts_2_name"]
)

percent_share = (
    (
        df_july.loc[(df_july["nuts_2_code"] == "UKJ2")]
        .copy()["job_location_raw"]
        .value_counts(normalize=True)
        .head(55)
    )
    * 100
).reset_index()

percent_share.head(1)

sussex_top55 = pd.merge(
    sussex_top55[["job_location_raw", "nuts_2_name"]].copy(),
    percent_share,
    how="left",
    left_on="job_location_raw",
    right_on="index",
)

sussex_top55.head(1)

# +
# sussex_top55.to_csv('top20locations_sussex.csv', index=False)
# -


# +
### Top areas in sussex - keyword search of job_location_raw field

# +
# https://en.wikipedia.org/wiki/List_of_settlements_in_East_Sussex_by_population
# -

east_sussex = [
    "Brighton",
    "Hove",
    "Eastbourne",
    "Hastings",
    "Bexhill-on-Sea",
    "Seaford",
    "Crowborough",
    "Hailsham",
    "Portslade-by-Sea",
    "Peacehaven",
    "Lewes",
    "Uckfield",
    "Newhaven",
    "Saltdean",
    "Polegate",
    "Heathfield",
    "Battle",
    "Rye",
]

# +
# https://en.wikipedia.org/wiki/List_of_settlements_in_West_Sussex_by_population
# -

west_sussex = [
    "Worthing",
    "Crawley",
    "Bognor Regis",
    "Littlehampton",
    "Shoreham-by-Sea",
    "Horsham",
    "Haywards Heath",
    "Burgess Hill",
    "East Grinstead",
    "Chichester",
    "Hurstpierpoint",
    "Southwick",
    "Selsey",
    "Westergate",
    "Southwater",
    "Storrington",
    "West Chiltington Common",
    "Billingshurst",
    "Steyning",
    "East Wittering",
    "Midhurst",
    "Henfield",
    "Crawley Down",
]

sussex = east_sussex + west_sussex

sussex = list(map(str.lower, sussex.copy()))

import string

sussex_clean = [
    "".join(x for x in par if x not in string.punctuation) for par in sussex
]

sussex[0]

df_july["location_clean"] = df_july["job_location_raw"].str.lower()

pattern = "|".join(sussex)

sussex_keywords = df_july[df_july["location_clean"].str.contains(pattern) == True]

sussex_keywords.drop_duplicates(
    subset=["job_location_raw", "nuts_2_name"], inplace=True
)

sussex_keywords[["job_location_raw", "nuts_2_name"]].to_csv(
    "locations_sussex_keywords.csv", index=False
)
