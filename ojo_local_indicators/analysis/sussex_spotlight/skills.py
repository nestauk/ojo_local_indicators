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
import numpy as np

from ojd_daps.dqa.data_getters import get_cached_job_ads
from ojd_daps.dqa.data_getters import fetch_descriptions
from ojd_daps.dqa.data_getters import get_valid_cache_dates

import ojo_local_indicators
import ojo_local_indicators.pipeline.clean_data as cd

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import altair as alt
import plotly.express as px
import collections
from collections import Counter

# %%
# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# %% [markdown]
# ### What skills are in greatest demand in Sussex? How do these differ from the rest of the UK?

# %% [markdown]
# - % of adverts requiring skill
#     - ads with skill / total adverts

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
def get_skills(data):
    """Get field from location dictionary within list of dictionaries.
    Fields are nut2 name and code."""
    skills = [
        d["features"].get("skills", {}).get("skills") for d in data if "features" in d
    ]
    return skills


# %%
sussex_skills = get_skills(sussex)
uk_skills = get_skills(uk_sample)


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

# %%
skill_groups.head(1)

# %%
sussex[200]

# %%
cluster_2 = skill_count(sussex_skills, "label_cluster_2")
cluster_uk_2 = skill_count(uk_skills, "label_cluster_2")

# %%
cluster_0 = skill_count(sussex_skills, "label_cluster_0")
cluster_uk_0 = skill_count(uk_skills, "label_cluster_0")

# %%
cluster_0s = combine(cluster_0)
cluster_2s = combine(cluster_2)

cluster_uk_0s = combine(cluster_uk_0)
cluster_uk_2s = combine(cluster_uk_2)

# %%
list(cluster_uk_2s.keys())[0]

# %%
skills_2 = []
for skill in list(cluster_2s.keys()):
    skills_2.append(sum(cluster_2s[skill]) / 41515)

df2_sussex = pd.DataFrame(
    {"Skill": list(cluster_2s.keys()), "Adverts requiring skill group": skills_2}
)

# %%
df2_sussex.head(3)

# %%
skills_2 = []
for skill in list(cluster_uk_2s.keys()):
    skills_2.append(sum(cluster_uk_2s[skill]) / 39819)

df2_uk = pd.DataFrame(
    {"Skill": list(cluster_uk_2s.keys()), "Adverts requiring skill group": skills_2}
)

# %%
df2_uk.head(5)

# %%
# Build a dataset
df_uk = pd.DataFrame(
    {
        "Skill": [
            "Information & Communication Technologies",
            "Engineering, Construction & Maintenance",
            "Healthcare, Social Work & Research",
            "Transversal skills",
            "Sales & Communication",
            "Education",
            "Food, Cleaning & Hospitality",
            "Business Administration, Finance & Law",
        ],
        "Adverts requiring skill group": [
            0.24,
            0.35,
            0.16,
            0.74,
            0.48,
            0.14,
            0.06,
            0.55,
        ],
    }
)

# Show 3 first rows
df_uk.head(3)

# %%
for skill in list(cluster_0s.keys()):
    print(skill)
    print(sum(cluster_0s[skill]) / 41515)

# %%
# Build a dataset
df = pd.DataFrame(
    {
        "Skill": [
            "Transversal skills",
            "Sales & Communication",
            "Engineering, Construction & Maintenance",
            "Business Administration, Finance & Law",
            "Food, Cleaning & Hospitality",
            "Healthcare, Social Work & Research",
            "Information & Communication Technologies",
            "Education",
        ],
        "Adverts requiring skill group": [
            0.74,
            0.49,
            0.33,
            0.55,
            0.07,
            0.15,
            0.23,
            0.14,
        ],
    }
)

# Show 3 first rows
df.head(3)

# %%
import numpy as np

# %% [markdown]
# https://www.python-graph-gallery.com/circular-barplot-basic

# %%
# import pandas for data wrangling
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = df.sort_values(by=["Adverts requiring skill group"])
df["Adverts requiring skill group"] = df["Adverts requiring skill group"] * 100

# Build a dataset
df["Name"] = df["Skill"]
df["Value"] = df["Adverts requiring skill group"]

# Reorder the dataframe
df = df.sort_values(by=["Value"])

# initialize the figure
plt.figure(figsize=(20, 10))
ax = plt.subplot(111, polar=True)
plt.axis("off")

# Constants = parameters controling the plot layout:
upperLimit = 100
lowerLimit = 30
labelPadding = 4

# Compute max and min in the dataset
max = df["Value"].max()

# Let's compute heights: they are a conversion of each item value in those new coordinates
# In our example, 0 in the dataset will be converted to the lowerLimit (10)
# The maximum will be converted to the upperLimit (100)
slope = (max - lowerLimit) / max
heights = slope * df.Value + lowerLimit

# Compute the width of each bar. In total we have 2*Pi = 360°
width = 2 * np.pi / len(df.index)

# Compute the angle each bar is centered on:
indexes = list(range(1, len(df.index) + 1))
angles = [element * width for element in indexes]
angles

# Draw bars
bars = ax.bar(
    x=angles,
    height=heights,
    width=width,
    bottom=lowerLimit,
    linewidth=2,
    edgecolor="white",
    color="#18A48C",
)

# Add labels
for bar, angle, height, label in zip(bars, angles, heights, df["Name"]):

    # Labels are rotated. Rotation must be specified in degrees :(
    rotation = np.rad2deg(angle)

    # Flip some labels upside down
    alignment = ""
    if angle >= np.pi / 2 and angle < 3 * np.pi / 2:
        alignment = "right"
        rotation = rotation + 180
    else:
        alignment = "left"

    # Finally add the labels
    ax.text(
        x=angle,
        y=lowerLimit + bar.get_height() + labelPadding,
        s=label,
        ha=alignment,
        va="center",
        rotation=rotation,
        rotation_mode="anchor",
        # weight = 'bold'
    )

plt.title(
    "Percent of Sussex adverts that belong to skill groups",
    fontsize=17,
    weight="bold",
    pad=5,
)

# %%
# import pandas for data wrangling
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = df_uk

df = df.sort_values(by=["Adverts requiring skill group"])
df["Adverts requiring skill group"] = df["Adverts requiring skill group"] * 100

# Build a dataset
df["Name"] = df["Skill"]
df["Value"] = df["Adverts requiring skill group"]

# Reorder the dataframe
df = df.sort_values(by=["Value"])

# initialize the figure
plt.figure(figsize=(20, 10))
ax = plt.subplot(111, polar=True)
plt.axis("off")

# Constants = parameters controling the plot layout:
upperLimit = 100
lowerLimit = 30
labelPadding = 4

# Compute max and min in the dataset
max = df["Value"].max()

# Let's compute heights: they are a conversion of each item value in those new coordinates
# In our example, 0 in the dataset will be converted to the lowerLimit (10)
# The maximum will be converted to the upperLimit (100)
slope = (max - lowerLimit) / max
heights = slope * df.Value + lowerLimit

# Compute the width of each bar. In total we have 2*Pi = 360°
width = 2 * np.pi / len(df.index)

# Compute the angle each bar is centered on:
indexes = list(range(1, len(df.index) + 1))
angles = [element * width for element in indexes]
angles

# Draw bars
bars = ax.bar(
    x=angles,
    height=heights,
    width=width,
    bottom=lowerLimit,
    linewidth=2,
    edgecolor="white",
    color="#18A48C",
)

# Add labels
for bar, angle, height, label in zip(bars, angles, heights, df["Name"]):

    # Labels are rotated. Rotation must be specified in degrees :(
    rotation = np.rad2deg(angle)

    # Flip some labels upside down
    alignment = ""
    if angle >= np.pi / 2 and angle < 3 * np.pi / 2:
        alignment = "right"
        rotation = rotation + 180
    else:
        alignment = "left"

    # Finally add the labels
    ax.text(
        x=angle,
        y=lowerLimit + bar.get_height() + labelPadding,
        s=label,
        ha=alignment,
        va="center",
        rotation=rotation,
        rotation_mode="anchor",
        # weight = 'bold'
    )

plt.title(
    "Percent of UK adverts that belong to skill groups",
    fontsize=17,
    weight="bold",
    pad=5,
)

# %%
skill_groups.head(1)

# %%
df2_uk = pd.merge(df2_uk, skill_groups, how="left", left_on="Skill", right_on="Skill_2")
df2_uk["color"] = df2_uk["Skill_0"]
df2_uk = df2_uk[df2_uk["Skill"].notna()]

# %%
df2_sussex = pd.merge(
    df2_sussex, skill_groups, how="left", left_on="Skill", right_on="Skill_2"
)
df2_sussex["color"] = df2_sussex["Skill_0"]
df2_sussex = df2_sussex[df2_sussex["Skill"].notna()]

# %%
df2_uk["color"].replace(
    [
        "Engineering, Construction & Maintenance",
        "Sales & Communication",
        "Business Administration, Finance & Law",
        "Healthcare, Social Work & Research",
        "Information & Communication Technologies",
        "Education",
        "Transversal skills",
        "Food, Cleaning & Hospitality",
    ],
    [
        "#18A48C",
        "#9A1BBE",
        "#EB003B",
        "#FF6E47",
        "#97D9E3",
        "#A59BEE",
        "#F6A4B7",
        "#FDB633",
    ],
    inplace=True,
)

# %%
df2_sussex["color"].replace(
    [
        "Engineering, Construction & Maintenance",
        "Sales & Communication",
        "Business Administration, Finance & Law",
        "Healthcare, Social Work & Research",
        "Information & Communication Technologies",
        "Education",
        "Transversal skills",
        "Food, Cleaning & Hospitality",
    ],
    [
        "#18A48C",
        "#9A1BBE",
        "#EB003B",
        "#FF6E47",
        "#97D9E3",
        "#A59BEE",
        "#F6A4B7",
        "#FDB633",
    ],
    inplace=True,
)

# %%
df2_uk["label"] = (
    df2_uk["Skill"]
    + " "
    + ((df2_uk["Adverts requiring skill group"]) * 100).round().astype(int).astype(str)
    + "%"
)

# %%
df2_uk.head(5)

# %%
df = df2_uk

df = df.sort_values(by=["Adverts requiring skill group"])
df["Adverts requiring skill group"] = df["Adverts requiring skill group"] * 100

# Build a dataset
df["Name"] = df["label"]
df["Value"] = df["Adverts requiring skill group"]

# Reorder the dataframe
df = df.sort_values(by=["Value"])

# initialize the figure
plt.figure(figsize=(20, 10))
ax = plt.subplot(111, polar=True)
plt.axis("off")

# Constants = parameters controling the plot layout:
upperLimit = 100
lowerLimit = 20
labelPadding = 4

# Compute max and min in the dataset
max = df["Value"].max()

# Let's compute heights: they are a conversion of each item value in those new coordinates
# In our example, 0 in the dataset will be converted to the lowerLimit (10)
# The maximum will be converted to the upperLimit (100)
slope = (max - lowerLimit) / max
heights = slope * df.Value + lowerLimit

# Compute the width of each bar. In total we have 2*Pi = 360°
width = 2 * np.pi / len(df.index)

# Compute the angle each bar is centered on:
indexes = list(range(1, len(df.index) + 1))
angles = [element * width for element in indexes]
angles

# Draw bars
bars = ax.bar(
    x=angles,
    height=heights,
    width=width,
    bottom=lowerLimit,
    linewidth=2,
    edgecolor="white",
    color=df["color"],
)

# map names to colors
cmap = dict(zip(list(df["Skill_0"]), list(df["color"])))

# create the rectangles for the legend
patches = [Patch(color=v, label=k) for k, v in cmap.items()]

# add the legend
plt.legend(
    handles=patches,
    bbox_to_anchor=(1.3, 0.5),
    loc="center left",
    borderaxespad=0,
    fontsize=11,
    frameon=False,
)

# Add labels
for bar, angle, height, label in zip(bars, angles, heights, df["Name"]):

    # Labels are rotated. Rotation must be specified in degrees :(
    rotation = np.rad2deg(angle)

    # Flip some labels upside down
    alignment = ""
    if angle >= np.pi / 2 and angle < 3 * np.pi / 2:
        alignment = "right"
        rotation = rotation + 180
    else:
        alignment = "left"

    # Finally add the labels
    ax.text(
        x=angle,
        y=lowerLimit + bar.get_height() + labelPadding,
        s=label,
        ha=alignment,
        va="center",
        rotation=rotation,
        rotation_mode="anchor",
        # weight = 'bold'
    )

plt.title(
    "Percent of vacancies belonging to skill group - Rest of UK",
    fontsize=17,
    weight="bold",
    pad=50,
)

plt.tight_layout()

# Do the plot code
plt.savefig(
    "percent_uk_ads_skill_group.jpg", format="jpg", dpi=1200, bbox_inches="tight"
)

# %%
df2_sussex["label"] = (
    df2_sussex["Skill"]
    + " "
    + ((df2_sussex["Adverts requiring skill group"]) * 100)
    .round()
    .astype(int)
    .astype(str)
    + "%"
)

# %%
df2_sussex.head(5)

# %%
df = df2_sussex

df = df.sort_values(by=["Adverts requiring skill group"])
df["Adverts requiring skill group"] = df["Adverts requiring skill group"] * 100

# Build a dataset
df["Name"] = df["label"]
df["Value"] = df["Adverts requiring skill group"]

# Reorder the dataframe
df = df.sort_values(by=["Value"])

# initialize the figure
plt.figure(figsize=(20, 10))
ax = plt.subplot(111, polar=True)
plt.axis("off")

# Constants = parameters controling the plot layout:
upperLimit = 100
lowerLimit = 20
labelPadding = 4

# Compute max and min in the dataset
max = df["Value"].max()

# Let's compute heights: they are a conversion of each item value in those new coordinates
# In our example, 0 in the dataset will be converted to the lowerLimit (10)
# The maximum will be converted to the upperLimit (100)
slope = (max - lowerLimit) / max
heights = slope * df.Value + lowerLimit

# Compute the width of each bar. In total we have 2*Pi = 360°
width = 2 * np.pi / len(df.index)

# Compute the angle each bar is centered on:
indexes = list(range(1, len(df.index) + 1))
angles = [element * width for element in indexes]
angles

# Draw bars
bars = ax.bar(
    x=angles,
    height=heights,
    width=width,
    bottom=lowerLimit,
    linewidth=2,
    edgecolor="white",
    color=df["color"],
)

# map names to colors
cmap = dict(zip(list(df["Skill_0"]), list(df["color"])))

# create the rectangles for the legend
patches = [Patch(color=v, label=k) for k, v in cmap.items()]

# add the legend
plt.legend(
    handles=patches,
    bbox_to_anchor=(1.5, 0.5),
    loc="center left",
    borderaxespad=0,
    fontsize=11,
    frameon=False,
)

# Add labels
for bar, angle, height, label in zip(bars, angles, heights, df["Name"]):

    # Labels are rotated. Rotation must be specified in degrees :(
    rotation = np.rad2deg(angle)

    # Flip some labels upside down
    alignment = ""
    if angle >= np.pi / 2 and angle < 3 * np.pi / 2:
        alignment = "right"
        rotation = rotation + 180
    else:
        alignment = "left"

    # Finally add the labels
    ax.text(
        x=angle,
        y=lowerLimit + bar.get_height() + labelPadding,
        s=label,
        ha=alignment,
        va="center",
        rotation=rotation,
        rotation_mode="anchor",
        # weight = 'bold'
    )

plt.title(
    "Percent of vacancies belonging to skill group - Sussex",
    fontsize=17,
    weight="bold",
    pad=150,
)

plt.tight_layout()

# Do the plot code
plt.savefig(
    "percent_sussex_ads_skill_group.jpg", format="jpg", dpi=1200, bbox_inches="tight"
)

# %%
# percent vacancies vs increase to UK
# Colour by broad skill group...

# %%
df2_sussex.head(3)

# %%
df2_sussex.shape

# %%
df2_sussex.set_index("Skill", inplace=True)

# %%
df2_sussex = pd.merge(
    df2_sussex,
    df2_uk[["Skill", "Adverts requiring skill group"]],
    how="left",
    left_on="Skill",
    right_on="Skill",
)

# %%
df2_sussex.rename(
    {
        "Adverts requiring skill group_x": "percent adverts Sussex",
        "Adverts requiring skill group_y": "percent adverts UK",
    },
    axis=1,
    inplace=True,
)

# %%
df_sussex_TS_remove = df2_sussex.iloc[1:, :]

# %%
df_sussex_10 = df_sussex_TS_remove.sort_values(
    by="percent adverts Sussex", ascending=False
).head(10)

# %%
df_sussex_10["percent adverts Sussex"] = df_sussex_10["percent adverts Sussex"] * 100
df_sussex_10["percent adverts UK"] = df_sussex_10["percent adverts UK"] * 100

# %%
df_sussex_10

# %%
domain = [
    "Engineering, Construction & Maintenance",
    "Sales & Communication",
    "Business Administration, Finance & Law",
    "Information & Communication Technologies",
    "Education",
]
source = df_sussex_10

range_ = ["#18A48C", "#9A1BBE", "#EB003B", "#FF6E47", "#0000FF"]

base = (
    alt.Chart(
        source, title="Percentage of vacancies by top 10 Sussex skills compared to UK"
    )
    .encode(
        x=alt.X(
            "percent adverts Sussex",
            scale=alt.Scale(domain=[8, 35]),
            axis=alt.Axis(title="% of Sussex vacancies", grid=False, titleFontSize=12),
        ),
        y=alt.Y(
            "percent adverts UK",
            scale=alt.Scale(domain=[8, 30]),
            axis=alt.Axis(title="% of UK vacancies", grid=False, titleFontSize=12),
        ),
        color=alt.Color(
            "Skill_0",
            legend=alt.Legend(title="Skill group"),
            scale=alt.Scale(domain=domain, range=range_),
        ),
        text="Skill_2",
        tooltip=["Skill_2", "Skill_0", "percent adverts Sussex", "percent adverts UK"],
    )
    .properties(width=650, height=500)
)

test = base.mark_point() + base.mark_text(dx=15, dy=2, align="left")

test  # .save("uk_vs_sussex_skills_top.html", scale_factor=2.0)

# %% [markdown]
# ### What salaries are associated with the largest (or fastest-growing) skill groups in Sussex?

# %%
list(df_sussex_10["Skill"].head(8))


# %%
def get_salary_fields(data, field):
    """Get field from location dictionary within list of dictionaries.
    Fields are nut2 name and code."""
    salary_field = [
        d["features"].get("salary", {}).get(field) for d in data if "features" in d
    ]
    return salary_field


# %%
salary = get_salary_fields(sussex, "max_annualised_salary")
salary_min = get_salary_fields(sussex, "min_annualised_salary")

# %%
len(salary_min)

# %%
skills_sussex = pd.DataFrame(cluster_2)

# %%
skills_sussex.shape

# %%
skills_sussex_max = pd.DataFrame(cluster_2)
skills_sussex_max["salary"] = salary
skills_sussex_max.dropna(subset=["salary"], inplace=True)
skills_sussex_max.fillna(0, inplace=True)
skills_sussex_max["type"] = "max annualised salary"

# %%
skills_sussex_min = pd.DataFrame(cluster_2)
skills_sussex_min["salary"] = salary_min
skills_sussex_min.dropna(subset=["salary"], inplace=True)
skills_sussex_min.fillna(0, inplace=True)
skills_sussex_min["type"] = "min annualised salary"

# %%
skills_sussex = pd.concat([skills_sussex_max, skills_sussex_min], axis=0)

# %%
skills_sussex.shape

# %%
skills_sussex = skills_sussex[
    [
        "Customer Services",
        "Business & Project Management",
        "Financial Services",
        "Sales",
        "Data Analytics",
        "Office Adminstration",
        "Accounting",
        "Workplace Safety Management",
        "salary",
        "type",
    ]
]

# %%
skills_sussex.head(5)

# %%
cs = skills_sussex[["Customer Services", "salary", "type"]]
bp = skills_sussex[["Business & Project Management", "salary", "type"]]
fs = skills_sussex[["Financial Services", "salary", "type"]]
sl = skills_sussex[["Sales", "salary", "type"]]
da = skills_sussex[["Data Analytics", "salary", "type"]]
oa = skills_sussex[["Office Adminstration", "salary", "type"]]
a = skills_sussex[["Accounting", "salary", "type"]]
wp = skills_sussex[["Workplace Safety Management", "salary", "type"]]

# %%
cs = cs[cs["Customer Services"] != 0]
bp = bp[bp["Business & Project Management"] != 0]
fs = fs[fs["Financial Services"] != 0]
sl = sl[sl["Sales"] != 0]
da = da[da["Data Analytics"] != 0]
oa = oa[oa["Office Adminstration"] != 0]
a = a[a["Accounting"] != 0]
wp = wp[wp["Workplace Safety Management"] != 0]

# %%
cs.drop(["Customer Services"], axis=1, inplace=True)
bp.drop(["Business & Project Management"], axis=1, inplace=True)
fs.drop(["Financial Services"], axis=1, inplace=True)
sl.drop(["Sales"], axis=1, inplace=True)
da.drop(["Data Analytics"], axis=1, inplace=True)
oa.drop(["Office Adminstration"], axis=1, inplace=True)
a.drop(["Accounting"], axis=1, inplace=True)
wp.drop(["Workplace Safety Management"], axis=1, inplace=True)

# %%
cs.head(1)

# %%
cs["skill group"] = "Customer Services"
bp["skill group"] = "Business & Project Management"
fs["skill group"] = "Financial Services"
sl["skill group"] = "Sales"
da["skill group"] = "Data Analytics"
oa["skill group"] = "Office Adminstration"
a["skill group"] = "Accounting"
wp["skill group"] = "Workplace Safety Management"

# %%
skill_salary = pd.concat([cs, bp, fs, sl, da, oa, a, wp], axis=0)

# %%
skill_salary.reset_index(inplace=True)

# %%
import seaborn as sns

# %%
sl["salary"].max()

# %%
df_sussex_10.head(1)

# %%
skill_salary.head(2)

# %%
rank = (
    skill_salary.groupby("skill group")["salary"].mean().fillna(0).sort_values().index
)

# %%
fig_dims = (18, 10)
fig, ax = plt.subplots(figsize=fig_dims)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)


# Turns off grid on the left Axis.
ax.grid(False)


ax = sns.boxplot(
    x="skill group",
    y="salary",
    data=skill_salary,
    hue="type",
    palette=["#F6A4B7", "#EB003B"],
    showfliers=False,
    order=rank,
    hue_order=["min annualised salary", "max annualised salary"],
)

from matplotlib.lines import Line2D

ax.legend(fontsize="18")

ax.set_title(
    "Salary distributions of the most common Sussex skills", fontsize=25, pad=25
)
ax.tick_params(axis="x", rotation=90)

plt.xticks(rotation=45, ha="right", fontsize=18)
plt.yticks(fontsize=18)
plt.xlabel("")
plt.ylabel("")


# plt.tight_layout()

# Do the plot code
plt.savefig(
    "salary_distributions_top_5_skills_sussex_outliers_rem.jpg",
    format="jpg",
    dpi=1200,
    bbox_inches="tight",
)

# %%
sns.set(font_scale=1.2)
sns.set_style("whitegrid")
g = sns.FacetGrid(skill_salary).set(
    title="Distribution of salaries by top 5 skills in Sussex"
)
g.map(sns.violinplot, "skill group", "salary", color="#18A48C")

g.fig.set_size_inches(25, 8)
g.set_xticklabels(rotation=90)

g.figure.savefig("distribution_salaries_sussex_skills.jpg")


# %% [markdown]
# ### Look at top surface forms per skill group

# %%
def skill_count_sf(skills, label1, label2):
    l1_list = []
    l2_list = []
    for skill in skills:
        if skill is None:
            unique_counts = {}
        else:
            l1 = [s[label1] for s in skill]
            l2 = [s[label2] for s in skill]
        l1_list.extend(l1)
        l2_list.extend(l2)
    return l1_list, l2_list


# %%
sf_list, c2_list = skill_count_sf(sussex_skills, "surface_form", "label_cluster_2")

# %%
surface_forms = pd.DataFrame(
    list(zip(sf_list, c2_list)), columns=["surface forms", "skill"]
)

# %%
surface_forms.head(1)

# %%
surface_forms.head(1)

# %%
surface_forms = (
    surface_forms.groupby(["skill", "surface forms"])
    .size()
    .reset_index(name="count")
    .reset_index(drop=True)
)

# %%
surface_forms[surface_forms.skill == "Sales"].sort_values(
    by="count", ascending=False
).set_index("surface forms").head(20)[["count"]].plot(kind="bar", figsize=(12, 4))
plt.title("Top 20 surface forms for Sales skill")

# %%
surface_forms[surface_forms.skill == "Customer Services"].sort_values(
    by="count", ascending=False
).set_index("surface forms").head(20)[["count"]].plot(kind="bar", figsize=(12, 4))
plt.title("Top 20 surface forms for Customer Services skill")

# %%
surface_forms[surface_forms.skill == "Business & Project Management"].sort_values(
    by="count", ascending=False
).set_index("surface forms").head(20)[["count"]].plot(kind="bar", figsize=(12, 4))
plt.title("Top 20 surface forms for Business & Project Management skill")

# %%
surface_forms[surface_forms.skill == "Financial Services"].sort_values(
    by="count", ascending=False
).set_index("surface forms").head(20)[["count"]].plot(kind="bar", figsize=(12, 4))
plt.title("Top 20 surface forms for Financial Services skill")

# %%
surface_forms[surface_forms.skill == "Data Analytics"].sort_values(
    by="count", ascending=False
).set_index("surface forms").head(20)[["count"]].plot(kind="bar", figsize=(12, 4))
plt.title("Top 20 surface forms for Data Analytics skill")
