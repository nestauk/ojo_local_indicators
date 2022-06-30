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
occupation = [d["sector"] for d in gr_sample if "sector" in d]

# %%
green = [d["gr_job"] for d in gr_sample if "gr_job" in d]

# %%
j_title = [d["job_title_raw"] for d in gr_sample if "job_title_raw" in d]
descr = [d["description"] for d in gr_sample if "description" in d]

# %%
len(descr)

# %%
print(Counter(green).keys())
print(Counter(green).values())

# %%
(1318 / 40197) * 100

# %%
occ_jd = pd.DataFrame(
    list(zip(occupation, green, j_title, descr)),
    columns=["occupation", "green", "job title", "description"],
)
occ_jd["occupation"] = occ_jd["occupation"].str.replace("&amp; ", "")

# %%
occ_jd.head(1)

# %%
pd.options.display.max_colwidth = 4000
occ_jd[(occ_jd["occupation"] == "Driving") & (occ_jd["green"] == "green")].tail(10)

# %%
occ_jd[(occ_jd["occupation"] == "Driving") & (occ_jd["green"] == "green")].groupby(
    ["job title", "green"]
).size().reset_index().sort_values(by=0, ascending=False).head(10)

# %%
occ = pd.DataFrame(list(zip(occupation, green)), columns=["occupation", "green"])
occ["occupation"] = occ["occupation"].str.replace("&amp; ", "")

# %%
occ_green = occ.groupby(["occupation", "green"]).size().reset_index()

# %%
occ_green = occ_green.pivot_table(values=0, index="occupation", columns="green")
occ_green.fillna(0, inplace=True)

# %%
occ_green["count"] = occ_green["green"] + occ_green["not_green"]
occ_green["percent green"] = (occ_green["green"] / occ_green["count"]) * 100

# %%
occ_green.shape

# %%
occ_green_top = occ_green.sort_values(by="count", ascending=False).head(30)

# %%
occ_green_top = occ_green_top.iloc[2:]

# %%
occ_green_top.head(2)

# %%
import numpy as np

# %%
# occ_green_top = occ_green_top.sort_values(by='percent green', ascending=False).head(20)

# %%
# occ_green_top = occ_green_top.head(20)

# %%
occ_green_top.sort_values(by="percent green", ascending=False, inplace=True)

# %%
y = occ_green_top["count"]
x = occ_green_top["percent green"]

# %%
fig, ax = plt.subplots(figsize=(40, 25))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
# ax.spines['left'].set_visible(False)
# ax.spines['bottom'].set_visible(False)

plt.scatter(
    x, y, s=occ_green_top["count"] * 2, c=occ_green_top["percent green"], cmap="Greens"
)


for i, txt in enumerate(
    list(occ_green_top.sort_values(by="percent green", ascending=False).head(15).index)
):
    plt.annotate(
        txt, (x[i] * 1.01, y[i]), rotation=15, ha="left", fontsize=40, color="black"
    )

plt.xticks(fontsize=30)
plt.yticks(fontsize=30)

plt.xlabel("Percentage green", fontsize=50, labelpad=20)
plt.ylabel("Count vacancies", fontsize=50, labelpad=20)

plt.title("Percent of green jobs per occupation", size=70, pad=150)

# %%
occ_green_top

# %%
