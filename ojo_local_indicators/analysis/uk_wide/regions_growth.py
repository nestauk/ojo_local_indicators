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

# %% [markdown]
# ### Which regions have experienced stronger/weaker growth in vacancies?

# %%
import pandas as pd
import json
import time
import random
import numpy as np

from ojd_daps.dqa.data_getters import get_cached_job_ads
from ojd_daps.dqa.data_getters import fetch_descriptions
from ojd_daps.dqa.data_getters import get_valid_cache_dates

import ojo_local_indicators
import ojo_local_indicators.pipeline.clean_data as cd
import ojo_local_indicators.pipeline.uk_wide as uw

import matplotlib.pyplot as plt
import altair as alt
from altair_saver import save
import plotly.express as px
import seaborn as sns
import collections
from collections import Counter
import geopandas as gpd
import altair as alt

# %%
# Get uk ads
uk_ads = uw.get_uk_ads()

# %%
# Read in shape file
county_ua_shapefile = gpd.read_file(
    "NUTS_Level_2_(January_2018)_Boundaries/NUTS_Level_2_(January_2018)_Boundaries.shp"
).to_crs(epsg=4326)

# %%
# Get locations and created date
locations = cd.get_location_fields(uk_ads, "nuts_2_code")
created_uk = [d["created"] for d in uk_ads if "created" in d]

# %%
# Locations / cerated df
loc_uk = pd.DataFrame(list(zip(locations, created_uk)), columns=["location", "created"])
loc_uk = loc_uk[loc_uk["location"].notna()].copy()  # Remove empty
# Set date/time format and index
loc_uk["created"] = pd.to_datetime(loc_uk["created"], format="%Y-%m-%d")
loc_uk.set_index("created", inplace=True)
loc_uk.sort_index(inplace=True)

# %%
# Time period split for growth track
jun_aug = loc_uk["2021-06-01":"2021-08-31"]
sep_nov = loc_uk["2021-09-01":]

# %%
# Get count per location / time periods
locations_count = Counter(list(jun_aug["location"])).most_common()
count_jun_aug = pd.DataFrame(dict(locations_count).items(), columns=["Nuts 2", "count"])

locations_count = Counter(list(sep_nov["location"])).most_common()
count_sep_nov = pd.DataFrame(dict(locations_count).items(), columns=["Nuts 2", "count"])

# %%
# Time period field
count_sep_nov["time_period"] = "September to November"
count_jun_aug["time_period"] = "June to August"
# Adjust so count refers to the same number of days
count_sep_nov["count"] = ((count_sep_nov["count"] / 83) * 86).astype(int)

# %%
# Merge
count_time = count_jun_aug.append(count_sep_nov, ignore_index=True).reset_index(
    drop=True
)

# %%
# London names
london_names = [
    "Inner London - West",
    "Inner London - East",
    "Outer London - East and North East",
    "Outer London - South",
    "Outer London - West and North West",
]
london_codes = ["UKI3", "UKI4", "UKI5", "UKI6", "UKI7"]

# %%
# Change to just London
count_time["Nuts 2"] = np.where(
    count_time["Nuts 2"].isin(london_codes), "UKI", count_time["Nuts 2"]
)

# %%
# Group by area and time period
count_time = count_time.groupby(["Nuts 2", "time_period"]).sum().reset_index()
count_time = count_time.pivot_table(
    index=["time_period"], columns="Nuts 2", values="count"
)  # .reset_index()

# %%
# Check results for London
count_time["UKI"]

# %%
# Get percent change per time period
count_time = count_time.pct_change()
count_time.drop(count_time.index[:1], inplace=True)
count_time = count_time.T.reset_index()
count_time.columns = ["Nuts 2", "Percent change"]

# %%
# Rename shapefile columns to align with df
county_ua_shapefile.rename({"nuts218cd": "Nuts 2"}, axis=1, inplace=True)
county_ua_shapefile.rename({"nuts218nm": "Nuts 2 region"}, axis=1, inplace=True)

# %%
# Make geopandas df
shapefile_geo = gpd.GeoDataFrame(county_ua_shapefile, geometry="geometry")
# Merge London codes
shapefile_geo["Nuts 2"] = np.where(
    shapefile_geo["Nuts 2"].isin(london_codes), "UKI", shapefile_geo["Nuts 2"]
)
shapefile_geo["Nuts 2 region"] = np.where(
    shapefile_geo["Nuts 2 region"].isin(london_names),
    "London",
    shapefile_geo["Nuts 2 region"],
)
shapefile_geo = shapefile_geo.dissolve(by=["Nuts 2", "Nuts 2 region"], aggfunc="mean")
shapefile_geo.reset_index(inplace=True)
# Merge dfs
count_time_geo = pd.merge(shapefile_geo, count_time, how="left", on="Nuts 2")

# %%
# Get min and max
min_pct = count_time_geo["Percent change"].min()
max_pct = count_time_geo["Percent change"].max()

# %%
# Set diverging colour ranges
col_range = ["#18A48C", "white", "#9A1BBE"]

# %%
# Create map
map_info = uw.create_nuts_map_divergent(
    count_time_geo,
    "Percent change",
    "Nuts 2 region",
    col_range,
    min_pct,
    max_pct,
    "descending",
    0,
)

# %%
# View map
map_info

# %%
# Save map
save(
    map_info,
    f"{project_directory}/outputs/figures/uk_wide/Growth_decline_regions_map_ldn_update.html",
)
