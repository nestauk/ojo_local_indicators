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

# %% [markdown]
# ### Which skill groups have experienced stronger/weaker growth?

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
# Update to full dataset later

# %%
uk_ads = cd.open_data_dump(
    f"{project_directory}/outputs/data/uk_sample_07-06-2021_22-11-2021.json"
)

# %%
job_ads1 = get_cached_job_ads("07-06-2021", "19-07-2021")
job_ads2 = get_cached_job_ads("19-07-2021", "30-08-2021")
job_ads3 = get_cached_job_ads("30-08-2021", "11-10-2021")
job_ads4 = get_cached_job_ads("11-10-2021", "22-11-2021")

# %%
job_ads = job_ads1 + job_ads2 + job_ads3 + job_ads4

# %%
filtered_dict = {(d["id"]): d for d in job_ads}
job_ads_de_dup = [value for value in filtered_dict.values()]

# %%
fixes = pd.read_excel(f"{project_directory}/inputs/data/nuts_2_fixes.xlsx")
fixes = fixes[["job_location_raw", "Code"]].copy()
# Locations list (correct names)
locations_n = cd.get_location_fields(job_ads, "nuts_2_name")
locations_c = cd.get_location_fields(job_ads, "nuts_2_code")
locations_n = list(dict.fromkeys(locations_n))
locations_c = list(dict.fromkeys(locations_c))
locations_n = [i for i in locations_n if i]
locations_c = [i for i in locations_c if i]
locations = pd.DataFrame(list(zip(locations_n, locations_c)), columns=["Name", "Code"])
fixes = fixes.merge(locations, on="Code", how="left")

# %%
# Takes about 5 mins...
for index, row in fixes.iterrows():
    for my_dict in job_ads_de_dup:
        if all(k in my_dict for k in ("job_location_raw", "features")):
            if my_dict["job_location_raw"] == row["job_location_raw"]:
                if "location" in my_dict["features"]:
                    my_dict["features"]["location"]["nuts_2_code"] = row["Code"]
                    my_dict["features"]["location"]["nuts_2_name"] = row["Name"]

# %%
uk_ads = job_ads_de_dup


# %% [markdown]
# - Difference in percent share or actual increase / decrease in overall count?
#     - Number of skill X vacancies has dropped by x%
#     - Percent of vacancies in xxx time period with skill x has dropped by x% compared to xxx time period

# %%
def get_skills(data):
    """Get field from location dictionary within list of dictionaries.
    Fields are nut2 name and code."""
    skills = [
        d["features"].get("skills", {}).get("skills") for d in data if "features" in d
    ]
    return skills


# %%
uk_skills = get_skills(uk_ads)
created_uk = [d["created"] for d in uk_ads if "created" in d]

# %%
uk_skills[100]

# %%
skills_uk = pd.DataFrame(
    list(zip(uk_skills, created_uk)), columns=["skills", "created"]
)

# %%
skills_uk["created"] = pd.to_datetime(skills_uk["created"], format="%Y-%m-%d")

# %%
skills_uk.set_index("created", inplace=True)
skills_uk.sort_index(inplace=True)

# %%
jun_aug = skills_uk["2021-06-01":"2021-08-31"]
sep_nov = skills_uk["2021-09-01":]
print("June-aug Dataset:", jun_aug.shape)
print("Sep-nov Dataset:", sep_nov.shape)

# %%
jun_aug_skills = list(jun_aug["skills"])
sep_nov_skills = list(sep_nov["skills"])


# %%
def skill_map(skills, label1, label2):
    l1 = []
    l2 = []
    for skill in skills:
        if skill is None:
            unique_counts = {}
        else:
            for s in skill:
                l1.append(s[label1])
                l2.append(s[label2])
    return l1, l2


# %%
def skill_count(skills, label):
    count_list = []
    for skill in skills:
        if skill is None:
            unique_counts = {}
        # else:
        # if s[label] is None:
        #       unique_counts = {}
        else:
            unique_counts = Counter(s[label] for s in skill)
            unique_counts = {x: 1 for x in dict(unique_counts)}
        count_list.append(unique_counts)
    return count_list


# %%
def combine(dictionaries):
    combined_dict = {}
    for dictionary in dictionaries:
        for key, value in dictionary.items():
            combined_dict.setdefault(key, []).append(value)
    return combined_dict


# %%
l0, l2 = skill_map(uk_skills, "label_cluster_0", "label_cluster_2")
skill_groups = pd.DataFrame({"Skill_0": l0, "Skill_2": l2})
skill_groups.drop_duplicates(inplace=True)
skill_groups.reset_index(drop=True, inplace=True)

# %%
skill_groups.head(1)

# %%
len(skills_uk)

# %%
len(jun_aug_skills) + len(sep_nov_skills)

# %%
print(len(jun_aug_skills))
print(len(sep_nov_skills))

# %%
jun_aug_2 = skill_count(jun_aug_skills, "label_cluster_2")
jun_aug_0 = skill_count(jun_aug_skills, "label_cluster_0")
sep_nov_2 = skill_count(sep_nov_skills, "label_cluster_2")
sep_nov_0 = skill_count(sep_nov_skills, "label_cluster_0")

# %%
jun_aug_2s = combine(jun_aug_2)
jun_aug_2s = combine(jun_aug_0)
sep_nov_2s = combine(sep_nov_2)
sep_nov_2s = combine(sep_nov_0)

# %%
list(jun_aug_2s.keys())[0]

# %%
skills_2 = []
for skill in list(jun_aug_2s.keys()):
    # skills_2.append((sum(jun_aug_2s[skill]) / 22146)*100)
    skills_2.append(sum(jun_aug_2s[skill]))

df2_jun_aug = pd.DataFrame(
    {"Skill": list(jun_aug_2s.keys()), "Jun-Aug count": skills_2}
)

# %%
skills_2 = []
for skill in list(sep_nov_2s.keys()):
    # skills_2.append((sum(sep_nov_2s[skill]) / 19369)*100)
    skills_2.append(round((sum(sep_nov_2s[skill]) / 83) * 86))

df2_sep_nov = pd.DataFrame(
    {"Skill": list(sep_nov_2s.keys()), "Sep-Nov count": skills_2}
)

# %%
df2_jun_aug = df2_jun_aug[df2_jun_aug.Skill.notna()]
df2_sep_nov = df2_sep_nov[df2_sep_nov.Skill.notna()]

# %%
skills2_total = df2_jun_aug.merge(df2_sep_nov, how="inner", on="Skill")

# %%
skills2_total.set_index("Skill", inplace=True)

# %%
skills2_total["Jun-Aug percent vacancies"] = (
    skills2_total["Jun-Aug count"] / 22146
) * 100
skills2_total["Sep-Nov percent vacancies"] = (
    skills2_total["Sep-Nov count"] / 19369
) * 100

# %%
skills2_total

# %%
percent_share_change = list(
    skills2_total[
        ["Jun-Aug percent vacancies", "Sep-Nov percent vacancies"]
    ].pct_change(axis="columns")["Sep-Nov percent vacancies"]
)

# %%
percent_share_change = [element * 100 for element in percent_share_change]

# %%
percent_share_change

# %%
skills2_total["Percent share difference"] = (
    skills2_total["Sep-Nov percent vacancies"]
    - skills2_total["Jun-Aug percent vacancies"]
)

# %%
skills2_total.drop(
    ["Jun-Aug percent vacancies", "Sep-Nov percent vacancies"], axis=1, inplace=True
)

# %%
percent_growth = list(
    skills2_total[["Jun-Aug count", "Sep-Nov count"]].pct_change(axis="columns")[
        "Sep-Nov count"
    ]
)

# %%
percent_growth = [element * 100 for element in percent_growth]

# %%
skills2_total.drop(["Jun-Aug count", "Sep-Nov count"], axis=1, inplace=True)

# %%
skills2_total["percent_growth"] = percent_growth
skills2_total["percent_share_change"] = percent_share_change

# %%
skills2_total

# %%
x = list(skills2_total["Percent share difference"])
y = list(skills2_total["percent_growth"])
n = list(skills2_total.index)

# %%
import numpy as np

# %%
skills2_total.reset_index(inplace=True)

# %%
skills2_total["Color"] = np.where(
    skills2_total["Percent share difference"] < 0, "#9A1BBE", "#18A48C"
)

# %%
import plotly

# %%
labels = {
    "Percent share difference": "<b>Percentage of vacancies increase/decrease</b>",
    "percent_growth": "<b>Percent growth/decline in vancancies</b>",
}

# %%
import plotly.express as px

fig = px.scatter(
    skills2_total,
    x="Percent share difference",
    y="percent_growth",
    color="Color",
    color_discrete_sequence=["#18A48C", "#9A1BBE"],
    width=1000,
    height=600,
)

fig.update_traces(
    textposition="bottom center",
    marker=dict(size=12, opacity=0.9, line=dict(width=2, color="DarkSlateGrey")),
)

fig.add_annotation(
    x=0.85,
    y=-1.875756,
    text="Information & Communication Technologies",
    showarrow=False,
    font=dict(family="Arial Black", size=13),
)

fig.add_annotation(
    x=-1.2,
    y=-15,
    text="Engineering, Construction & Maintenance",
    showarrow=False,
    font=dict(family="Arial Black", size=13),
)

fig.add_annotation(
    x=1.4,
    y=-13.632515,
    text="Healthcare, Social Work & Research",
    showarrow=False,
    font=dict(family="Arial Black", size=13),
)

fig.add_annotation(
    x=2.7,
    y=-10.408742,
    text="Transversal skills",
    showarrow=False,
    font=dict(family="Arial Black", size=13),
)

fig.add_annotation(
    x=1,
    y=-12.692590,
    text="Sales & Communication",
    showarrow=False,
    font=dict(family="Arial Black", size=13),
)

fig.add_annotation(
    x=1.078787,
    y=-6.3,
    text="Education",
    showarrow=False,
    font=dict(family="Arial Black", size=13),
)

fig.add_annotation(
    x=1.38,
    y=-11.578947,
    text="Food, Cleaning & Hospitality",
    showarrow=False,
    font=dict(family="Arial Black", size=13),
)

fig.add_annotation(
    x=4.1,
    y=-2.856410,
    text="Business Administration, Finance & Law",
    showarrow=False,
    font=dict(family="Arial Black", size=13),
)


fig.update_layout(
    paper_bgcolor="rgba(255,255,255,1)",
    plot_bgcolor="rgba(255,255,255,1)",
    showlegend=False,
    title=dict(
        text="<b>Broad skill groups - Growth / decline</b>",
        x=0.7,
        y=0.95,
        font=dict(family="Arial", size=20, color="#000000"),
    ),
    xaxis_title="<b>Percentage of vacancies increase/decrease</b>",
    yaxis_title="<b>Growth/decline</b>",
    font=dict(family="Arial", size=15, color="#000000"),
)

fig.update_yaxes(tickfont_family="Arial")
fig.update_xaxes(tickfont_family="Arial")

fig.update_xaxes(showline=True, linewidth=1, linecolor="black")
fig.update_yaxes(showline=True, linewidth=1, linecolor="black")


import plotly.io as pio

pio.write_image(fig, "growth_broad_skill_groups.svg", width=1000, height=600, scale=2)
fig.show()
