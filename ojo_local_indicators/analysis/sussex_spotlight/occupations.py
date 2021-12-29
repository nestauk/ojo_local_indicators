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
import pandas as pd
import json
import time
import random

from ojd_daps.dqa.data_getters import get_cached_job_ads
from ojd_daps.dqa.data_getters import fetch_descriptions
from ojd_daps.dqa.data_getters import get_valid_cache_dates

import ojo_local_indicators
import ojo_local_indicators.pipeline.clean_data as cd

import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px

# %%
# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# %%
sussex = cd.open_data_dump(
    f"{project_directory}/outputs/data/sussex_07-06-2021_22-11-2021.json"
)
uk_sample = cd.open_data_dump(
    f"{project_directory}/outputs/data/uk_sample_07-06-2021_22-11-2021.json"
)

# %%
uk = []
for my_dict in uk_sample:
    if "location" in my_dict["features"]:
        if my_dict["features"]["location"]["nuts_2_code"] != "UKJ2":
            uk.append(my_dict)
    else:
        uk.append(my_dict)
uk_sample = uk
len(uk_sample)

# %%
occupation = [d["sector"] for d in sussex if "sector" in d]
created = [d["created"] for d in sussex if "created" in d]

occupation_uk = [d["sector"] for d in uk_sample if "sector" in d]
created_uk = [d["created"] for d in uk_sample if "created" in d]

# %%
occ = pd.DataFrame(list(zip(occupation, created)), columns=["occupation", "created"])
occ_uk = pd.DataFrame(
    list(zip(occupation_uk, created_uk)), columns=["occupation", "created"]
)

# %%
occ["created"] = pd.to_datetime(occ["created"], format="%Y-%m-%d")
occ["occupation"] = occ["occupation"].str.replace("&amp; ", "")

occ_uk["created"] = pd.to_datetime(occ_uk["created"], format="%Y-%m-%d")
occ_uk["occupation"] = occ_uk["occupation"].str.replace("&amp; ", "")

# %%
occ.head(2)

# %%
occ_uk_sussex = pd.concat(
    {
        "Sussex": occ["occupation"].value_counts(normalize=True).mul(100),
        "UK": occ_uk["occupation"].value_counts(normalize=True).mul(100),
    },
    axis=1,
)

# %%
occ_uk_sussex["Difference from UK"] = occ_uk_sussex["Sussex"] - occ_uk_sussex["UK"]

# %%
occ_uk_sussex.sort_values(by="Sussex", ascending=False).head(30)[
    ["Difference from UK", "Sussex"]
].sort_values(by=["Sussex", "Difference from UK"]).plot(
    kind="barh", figsize=(10, 10), color=["#0000FF", "#18A48C"], alpha=0.7
)

plt.gca().yaxis.grid(True, color="#646363", linestyle="-", linewidth=0.2)

plt.title("Top 30 occupations Sussex compared to the UK")
plt.xlabel("Percentage of vacancies")
plt.ylabel("Occupations")

# plt.show()

# Save chart
plt.savefig("top_occupations_sussex_uk.png", dpi=200, bbox_inches="tight")

# %%
