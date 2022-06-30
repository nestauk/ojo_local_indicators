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
# # Analyses health skills by occupations (for the UK) and produces three charts

# %% [markdown]
# ### Libraries

# %%
# General
import sys

sys.path.append("..")
import json
from ojo_local_indicators import get_yaml_config, Path, PROJECT_DIR
from ojo_local_indicators.pipeline.utils import annualises_salary
import numpy as np
import matplotlib.pyplot as plt

# Libraries for collecting processed adverts
from ojd_daps.dqa.data_getters import get_cached_job_ads
from ojd_daps.dqa.data_getters import get_valid_cache_dates


# %%
import ojo_local_indicators.getters.open_data as od

# Get data
sussex = od.sussex
uk_sample = od.uk_sample

# %% [markdown]
# ### Globals

# %%
# Path to charts
PATH_TO_CHARTS = str(PROJECT_DIR) + "/outputs/figures/deep_dive/"

# No of digital skills to consider
NO_health_SKILLS = 30

# No of occupations
NO_OCCUPATIONS = 40

# Selection of colours from Nesta's brand
COLORS = ["#69E0C5", "#97D9E3", "#FDB633", "#981BBE"]

# Exclude because they include the phrase 'database' in all their adverts
# which distorts the results
EXCLUDED_RECRUITERS = ["Engage Partners"]

## CHART 2
# Scale parameter for bubble chart (affects size of bubbles)
SCALE_BUBBLE = 10

# Drop occupations that require chosen skill in less than 5% of job adverts
MINIMUM_PERCENT = 5

# Drop occupations that were advertised less than 10 times
MINIMUM_JOB_COUNT = 10

# %% [markdown]
# # 1. What salary ranges are associated with popular health skills?

# %% [markdown]
# ### Load UK adverts

# %%
job_ads_uk = get_cached_job_ads("06-09-2021", "18-10-2021")
job_ads_uk += get_cached_job_ads("18-10-2021", "29-11-2021")

# %%
len(job_ads_uk)

# %%
filtered_dict = {(d["id"]): d for d in job_ads_uk}
job_ads_uk = [value for value in filtered_dict.values()]


# %% [markdown]
# ### Temp start

# %%
def get_skills(data):
    """Get field from location dictionary within list of dictionaries.
    Fields are nut2 name and code."""
    skills = [
        d["features"].get("skills", {}).get("skills") for d in data if "features" in d
    ]
    return skills


# %%
from collections import Counter


def skill_count(skills, label):
    """Returns a dictionary with which counts where a job advert mentions each skill."""
    count_list = []
    # Loop through skills per advert and count if occurance is >=1
    for skill in skills:
        if skill is None:
            unique_counts = {}
        else:
            unique_counts = Counter(s[label] for s in skill)
            unique_counts = {x: 1 for x in dict(unique_counts)}
        count_list.append(unique_counts)
    # Return count list of skills per advert
    return count_list


# %%
skills = get_skills(job_ads_uk)

# %%
cluster_2 = skill_count(skills, "preferred_label")

# %%
next(
    (i for i, item in enumerate(cluster_2) if "perform health assessment" in item), None
)

# %%
perform_health_assess = [i for i, d in enumerate(cluster_2) if "surgery" in d]

# %%
perform_health_assess[900]

# %%
len(perform_health_assess)

# %%
cluster_2[3]

# %%
job_ads_uk[279829]

# %% [markdown]
# ### Temp end

# %%
len(job_ads_uk)

# %%
job_ads_uk[0]

# %% [markdown]
# ### Extract digital skills (and salaries) from UK adverts

# %%
health = [
    "Psychology & Mental Health",
    "Scientific Research",
    "Care & Social Work",
    "Medical Specialist Skills",
]

# %%
# Dictionary of health skills
health_skills = {}

# Loop over job ads
for one_job in job_ads_uk:

    # If the job advert contains skills and is not an excluded recruiter:
    if (
        "skills" in one_job["features"]
        and one_job["company_raw"] not in EXCLUDED_RECRUITERS
    ):

        # Loop over skills
        for one_skill in one_job["features"]["skills"]["skills"]:

            # If the skill lives in the digital cluster
            if one_skill["label_cluster_2"] in health:

                # Name of the skill
                one_health_skill = one_skill["preferred_label"]

                # If it's a new digital skill
                if one_health_skill not in health_skills:
                    health_skills[one_health_skill] = {
                        "skill_count": 0,
                        "label": one_health_skill,
                        "min_salaries": [],
                        "max_salaries": [],
                    }

                # Add one to the count of that skill
                health_skills[one_health_skill]["skill_count"] += 1

                # Capture salaries (if present)
                salaries = annualises_salary(one_job)
                if salaries[0] is not None:
                    health_skills[one_health_skill]["min_salaries"].append(salaries[0])
                    health_skills[one_health_skill]["max_salaries"].append(salaries[1])


# %%
health_skills["perform health assessment"]

# %% [markdown]
# ### Identify most common health skills and their salary ranges

# %%
# Number of health skills
print("Number of health skills: " + str(len(health_skills)))

# Sort health skills by frequency
health_skills_sorted = sorted(
    health_skills.values(), key=lambda k: k["skill_count"], reverse=True
)

# The top 30 health skills account for what percentage of all mentions (of health skills)
top_skills_percent = (
    100
    * sum([value["skill_count"] for value in health_skills_sorted[0:NO_health_SKILLS]])
    / sum([value["skill_count"] for value in health_skills_sorted])
)
print(
    "The top "
    + str(NO_health_SKILLS)
    + " health skills account for "
    + str(round(top_skills_percent, 2))
    + "% of all health skills mentioned"
)

# Extract the names of all health skills
health_skills_names = [value["label"] for value in health_skills_sorted]

# Identify the most common health skills
common_health_skills = health_skills_names[0:NO_health_SKILLS]

# Find the median of the min and max salaries associated with each health skill
for value in health_skills_sorted:

    # If some salaries have been captured:
    if value["min_salaries"]:

        # Medians
        value["median_min_salaries"] = np.median(value["min_salaries"])
        value["median_max_salaries"] = np.median(value["max_salaries"])

    else:

        # Medians
        value["median_min_salaries"] = None
        value["median_max_salaries"] = None


# %% [markdown]
# ### Chart the most frequently mentioned engineering skills and their associated salaries

# %%
# Figure
fig, ax = plt.subplots(figsize=(12, 15))

# Data for chart
y = list(range(NO_health_SKILLS))
y.reverse()
x_median_min = [value["median_min_salaries"] for value in health_skills_sorted][
    0:NO_health_SKILLS
]
x_median_max = [value["median_max_salaries"] for value in health_skills_sorted][
    0:NO_health_SKILLS
]

# Horizontal line and scatter points
plt.hlines(y, x_median_min, x_median_max, colors="black", linewidth=1, alpha=0.5)
plt.scatter(x_median_min, y, s=30, c=COLORS[2])
plt.scatter(x_median_max, y, s=30, c=COLORS[3])

# Add name of each health skill
label_pos = [
    0.5 * (value["median_min_salaries"] + value["median_max_salaries"])
    for value in health_skills_sorted[0:NO_health_SKILLS]
]
for index, one_skill in enumerate(health_skills_sorted[0:NO_health_SKILLS]):
    ax.annotate(
        one_skill["label"].title(),
        (label_pos[index], y[index] + 0.15),
        ha="center",
        fontsize=16,
    )

# Hide y axis
ax.axes.get_yaxis().set_ticks([])

# Add commas to x axis
ax.set_xticklabels(
    ["{:,}".format(int(x)) for x in ax.get_xticks().tolist()], fontsize=16
)

# Hide some borders
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["top"].set_visible(False)

# Titles of axes
plt.xlabel("Annualised advertised salaries (£)", fontsize=18, weight="bold")
ax.xaxis.set_label_coords(0.5, -0.05)
plt.ylabel("Most-mentioned health skills", fontsize=18, rotation=0, weight="bold")
ax.yaxis.set_label_coords(0.5, 1)

# Legend
for index, label_each_dot in enumerate(
    ["Median of all minimum salaries", "Median of all maximum salaries"]
):
    plt.scatter([], [], c=COLORS[index + 2], alpha=0.75, s=80, label=label_each_dot)
legend = ax.legend(
    scatterpoints=1,
    frameon=True,
    labelspacing=1,
    title="Salaries",
    bbox_to_anchor=(0.2, 1.15),
    borderpad=1.5,
    fontsize=16,
)
legend.get_title().set_fontsize("18")
legend.get_title().set_fontweight("bold")

# Save
plt.savefig(
    PATH_TO_CHARTS + "health_skills_and_salaries.png", dpi=200, bbox_inches="tight"
)


# %% [markdown]
# # 2. Which popular digital skills are required in frequently-advertised occupations (in UK sample)?

# %% [markdown]
# ### Find all occupation names

# %%
occupation_names = []

# Loop over job ads
for one_job in uk_sample:

    # If it's a new occupation name
    if one_job["sector"] not in occupation_names:

        # Add it to list
        occupation_names.append(one_job["sector"])

# %% [markdown]
# ### Create a dictionary of occupations, containing the health skills and their counts

# %%
health

# %%
health_skills_names.index("biology")

# %%
# Dictionary of occupations and the health skills they rely on
occup_by_health = {
    value: {
        "job_count": 0,
        "job_count_health": 0,  # No. of adverts that require at least one health skill
        "skill_counts": [0 for value in range(0, len(health_skills_names))],
        "label": value,
    }
    for value in occupation_names
}

# Loop over job ads
for one_job in uk_sample:

    # If the job advert contains skills and is not an excluded recruiter:
    if (
        "skills" in one_job["features"]
        and one_job["company_raw"] not in EXCLUDED_RECRUITERS
    ):

        # Name of occupation (called 'sector' by Reed)
        one_occupation = one_job["sector"]

        # Count job (only those that have skills)
        occup_by_health[one_occupation]["job_count"] += 1

        # Start by assuming that no health skills are required
        requires_one_health_skill = False

        # Loop over skills
        for one_skill in one_job["features"]["skills"]["skills"]:

            # If the skill lives in the health cluster
            if (
                one_skill["label_cluster_2"] in health
                and one_skill["preferred_label"] in health_skills_names
            ):

                # The job requires at least one health skill
                requires_one_health_skill = True

                # Name of the skill
                one_health_skill = one_skill["preferred_label"]

                # Add one to the count of that skill for that occupation
                occup_by_health[one_occupation]["skill_counts"][
                    health_skills_names.index(one_health_skill)
                ] += 1

        # If the job requires at least one health skill
        if requires_one_health_skill == True:
            occup_by_health[one_occupation]["job_count_health"] += 1


# %% [markdown]
# ### For each occupation and digital skill, calculate the percentage of job adverts in that occupation which mention that specific health skill

# %%
# Loop over occupations
for key_occupation, value_occupation in occup_by_health.items():

    # Percentage of job adverts that require at least one health skill
    if value_occupation["job_count"] > 0:
        value_occupation["percent_health_jobs"] = (
            100 * value_occupation["job_count_health"] / value_occupation["job_count"]
        )
    else:
        value_occupation["percent_health_jobs"] = 0

    # If at least one job advert in that occupation required a health skill
    if value_occupation["job_count"] > 0:
        value_occupation["skill_percents"] = [
            100 * value_skill / value_occupation["job_count"]
            for value_skill in value_occupation["skill_counts"]
        ]

    # Otherwise, set to zero
    else:
        value_occupation["skill_percents"] = [0] * len(value_occupation["skill_counts"])

# %% [markdown]
# ### Find the occupations that most frequently rely on digital skills

# %%
# Sort occupations by those that most frequently require at least one health skill
occupations_sorted = sorted(
    occup_by_health.values(), key=lambda k: k["percent_health_jobs"], reverse=True
)

# Identify the names of healthly-intensive, and non-small, occupations ONLY
health_occupation_names = [
    value["label"]
    for value in occupations_sorted
    if value["job_count"] >= MINIMUM_JOB_COUNT
][0:NO_OCCUPATIONS]

# Reverse so that healthly-intensive occupations are shown at the top of the chart
health_occupation_names.reverse()

# %% [markdown]
# ### Chart showing the percentage of adverts for a given occupation that require a specific health skill
# ##### (health-intensive occupations and most mentioned health skills only)

# %%
common_health_skills

# %%
# Figure
fig, ax = plt.subplots(figsize=(12, 12))

# Plot scatter points for each occupation
for index_occupation, one_occupation in enumerate(health_occupation_names):

    # Alternative colors so the chart is easier to read
    color_bubble = COLORS[0] if index_occupation % 2 == 0 else COLORS[1]

    # Only retrieve 'percents' for the most common health skills
    sizes = [
        value * SCALE_BUBBLE
        for index, value in enumerate(occup_by_health[one_occupation]["skill_percents"])
        if health_skills_names[index] in common_health_skills
    ]

    # Plot health skills
    sc = ax.scatter(
        list(range(NO_health_SKILLS)),
        [index_occupation] * NO_health_SKILLS,
        s=sizes,
        c=color_bubble,
        alpha=0.75,
    )

# Hide borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_visible(False)

# Titles of axes
plt.xlabel("Most-mentioned health skills", fontsize=18, weight="bold")
ax.xaxis.set_label_coords(0.35, 1.36)
plt.ylabel("health occupations", fontsize=18, rotation=0, weight="bold")
ax.yaxis.set_label_coords(-0.15, 0.97)

# Y axis labels
ax.set_yticks(list(range(NO_OCCUPATIONS)))
ax.set_yticklabels(
    [value.replace("&amp;", "&") for value in health_occupation_names], fontsize=16
)

# X axis labels
ax.xaxis.tick_top()
ax.set_xticks(list(range(NO_health_SKILLS)))
ax.set_xticklabels(
    [value.title() for value in common_health_skills],
    rotation=45,
    ha="left",
    fontsize=16,
)
ax.tick_params(axis=u"both", which=u"both", length=0)

# Grid
ax.set_axisbelow(True)
ax.grid(color="lightgray", linestyle="dashed")

# Legend
for percent in [5, 25, 50, 75]:
    plt.scatter(
        [],
        [],
        c=COLORS[0],
        alpha=0.75,
        s=percent * SCALE_BUBBLE,
        label=str(percent) + "%",
    )
legend = ax.legend(
    scatterpoints=1,
    frameon=True,
    labelspacing=1,
    title="Adverts requiring skill",
    bbox_to_anchor=(0, 1.35),
    borderpad=1.5,
    fontsize=16,
)
legend.get_title().set_fontsize("18")
legend.get_title().set_fontweight("bold")

# Save
plt.savefig(
    PATH_TO_CHARTS + "health_skills_and_occupations.png", dpi=200, bbox_inches="tight"
)

# %% [markdown]
# # 3. Which occupations rely on one particular health skill (in UK sample): advise on mental health?

# %%
CHOSEN_SKILL = "advise on mental health"

# %%
# Exclude occupations where the chosen skill is required in less than 5% of adverts for the occupation
# and exclude occupations with very few adverts
occupations_one_skill = [
    value
    for value in occupations_sorted
    if value["skill_percents"][health_skills_names.index(CHOSEN_SKILL)] >= 10
    and value["job_count"] >= MINIMUM_JOB_COUNT
]
occupations_one_skill.reverse()

# %%
# Figure
fig, ax = plt.subplots(figsize=(15, 16))

x = [
    one_occupation["skill_percents"][health_skills_names.index(CHOSEN_SKILL)]
    for one_occupation in occupations_one_skill
]
y = [index for index, one_occupation in enumerate(occupations_one_skill)]
labels = [
    one_occupation["label"].replace("&amp;", "&")
    for one_occupation in occupations_one_skill
]

# Plot transversal skills
sc = ax.scatter(x, y, s=100, c=COLORS[0], label=labels, alpha=0.75)

# Labels
for i, txt in enumerate(occupations_one_skill):
    ax.annotate(labels[i], (x[i] + 1, y[i] - 0.2), fontsize=16)

# Hide some borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

# Axis labels
ax.axes.get_yaxis().set_ticks([])
ax.tick_params(axis="both", which="major", labelsize=18)

# Titles of axes
plt.xlabel(
    "Percentage of job adverts requiring " + CHOSEN_SKILL, fontsize=23, weight="bold"
)
ax.xaxis.set_label_coords(0.5, -0.05)
plt.ylabel("Occupations (largest to smallest)", fontsize=18, rotation=0, weight="bold")
ax.yaxis.set_label_coords(0.5, 0.99)

# Save
plt.savefig(
    PATH_TO_CHARTS + "one_health_skill_and_occupations1.png",
    dpi=200,
    bbox_inches="tight",
)

# %%
# Testing a different skill
CHOSEN_SKILL = "medicines"

# %%
# Exclude occupations where the chosen skill is required in less than 5% of adverts for the occupation
# and exclude occupations with very few adverts
occupations_one_skill = [
    value
    for value in occupations_sorted
    if value["skill_percents"][health_skills_names.index(CHOSEN_SKILL)]
    >= MINIMUM_PERCENT
    and value["job_count"] >= MINIMUM_JOB_COUNT
]
occupations_one_skill.reverse()

# %%
# Figure
fig, ax = plt.subplots(figsize=(16, 15))

x = [
    one_occupation["skill_percents"][health_skills_names.index(CHOSEN_SKILL)]
    for one_occupation in occupations_one_skill
]
y = [index for index, one_occupation in enumerate(occupations_one_skill)]
labels = [
    one_occupation["label"].replace("&amp;", "&")
    for one_occupation in occupations_one_skill
]

# Plot transversal skills
sc = ax.scatter(x, y, s=100, c=COLORS[0], label=labels, alpha=0.75)

# Labels
for i, txt in enumerate(occupations_one_skill):
    ax.annotate(labels[i], (x[i] + 1, y[i] - 0.2), fontsize=16)

# Hide some borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

# Axis labels
ax.axes.get_yaxis().set_ticks([])
ax.tick_params(axis="both", which="major", labelsize=16)

# Titles of axes
plt.xlabel(
    "Percentage of job adverts requiring " + CHOSEN_SKILL, fontsize=18, weight="bold"
)
ax.xaxis.set_label_coords(0.5, -0.05)
plt.ylabel("Occupations (largest to smallest)", fontsize=18, rotation=0, weight="bold")
ax.yaxis.set_label_coords(0.5, 0.99)

# Save
plt.savefig(
    PATH_TO_CHARTS + "one_health_skill_and_occupations2.png",
    dpi=200,
    bbox_inches="tight",
)

# %%
