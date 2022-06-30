# -*- coding: utf-8 -*-
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
import seaborn as sns
from collections import Counter

# %%
# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# %% [markdown]
# ### Which occupations contain the greatest number (or intensity) of green jobs across the UK?

# %%
gr_sample = cd.open_data_dump(
    f"{project_directory}/outputs/data/green_jobs_uk_sample.json"
)

# %%
gr_sample[0]

# %%
test = pd.DataFrame(gr_sample)

# %%
test.shape

# %%
industry = [d["parent_sector"] for d in gr_sample if "parent_sector" in d]

# %%
green = [d["gr_job"] for d in gr_sample if "gr_job" in d]

# %%
j_title = [d["job_title_raw"] for d in gr_sample if "job_title_raw" in d]

# %%
len(industry)

# %%
ind_jd = pd.DataFrame(
    list(zip(industry, green, j_title)), columns=["industry", "green", "job title"]
)
ind_jd["industry"] = ind_jd["industry"].str.replace("&amp; ", "")

# %%
ind_jd.head(10)

# %%
ind_jd[
    (ind_jd["industry"] == "Construction Property") & (ind_jd["green"] == "green")
].groupby(["job title", "green"]).size().reset_index().sort_values(
    by=0, ascending=False
).head(
    10
)

# %%
print(Counter(green).keys())
print(Counter(green).values())

# %%
(1318 / 40197) * 100

# %%
ind = pd.DataFrame(list(zip(industry, green)), columns=["industry", "green"])
ind["industry"] = ind["industry"].str.replace("&amp; ", "")

# %%
ind.head(10)

# %%
ind_green = ind.groupby(["industry", "green"]).size().reset_index()

# %%
ind_green = ind_green.pivot_table(values=0, index="industry", columns="green")
ind_green.fillna(0, inplace=True)

# %%
ind_green["count"] = ind_green["green"] + ind_green["not_green"]
ind_green["percent green"] = (ind_green["green"] / ind_green["count"]) * 100

# %%
ind_green.head(20)

# %%
ind_green_top = ind_green.sort_values(by="count", ascending=False).head(30)

# %%
import numpy as np

# %%
len(ind_green_top.index)

# %%
ind_green_top.sort_values(by="percent green", ascending=False, inplace=True)

# %%
ind_green_top.head(10)

# %%
x = ind_green_top["percent green"]
y = ind_green_top["count"]

# %%
fig, ax = plt.subplots(figsize=(35, 35))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
# ax.spines['left'].set_visible(False)
# ax.spines['bottom'].set_visible(False)

plt.scatter(
    x, y, s=ind_green_top["count"], c=ind_green_top["percent green"], cmap="Greens"
)

for i, txt in enumerate(list(ind_green_top.head(15).index)):
    plt.annotate(
        txt, (x[i] * 1.02, y[i]), rotation=25, ha="left", fontsize=40, color="black"
    )

plt.xticks(fontsize=30)
plt.yticks(fontsize=30)

plt.xlabel("Percentage green", fontsize=50, labelpad=20)
plt.ylabel("Count vacancies", fontsize=50, labelpad=20)

plt.title("Percentage of green jobs per industry", size=70, pad=100)

# %%
ind_green_top.sort_values(by="percent green", ascending=False)

# %%
