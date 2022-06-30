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
#       jupytext_version: 1.13.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Analyses digital skills (for the UK and Sussex) and produces three charts

# %% [markdown]
# ### Libraries

# %%
# General
import sys

sys.path.append("..")
import json
from ojo_local_indicators import get_yaml_config, Path, PROJECT_DIR
from ojo_local_indicators.analysis.utils import annualises_salary
import numpy as np
import matplotlib.pyplot as plt

# Libraries for collecting processed adverts
from ojd_daps.dqa.data_getters import get_cached_job_ads
from ojd_daps.dqa.data_getters import get_valid_cache_dates


# %% [markdown]
# ### Globals

# %%
# Path to adverts in Sussex
PATH_TO_SUSSEX_DATA = (
    str(PROJECT_DIR) + "/inputs/data/sussex_07-06-2021_22-11-2021.json"
)

# Path to charts
PATH_TO_CHARTS = str(PROJECT_DIR) + "/outputs/figures/digital_skills/"

# No of digital skills to consider
NO_DIGITAL_SKILLS = 30

# No of occupations
NO_OCCUPATIONS = 40

# Selection of colours from Nesta's brand
COLORS = ["#69E0C5", "#97D9E3", "#FDB633", "#981BBE"]

# Excluded recruiters - because they include the phrase 'database' in all their adverts
# which distorts the results
EXCLUDED_RECRUITERS = ["Engage Partners"]

# Major settlements in Surrey that should be excluded
MAJOR_SURREY_SETTLEMENTS = [
    "Surrey",
    "Addlestone",
    "Ash",
    "Ashford",
    "Banstead",
    "Camberley",
    "Caterham",
    "Chertsey",
    "Cranleigh",
    "Dorking",
    "Egham",
    "Epsom",
    "Esher",
    "Farnham",
    "Frimley",
    "Godalming",
    "Great Bookham",
    "Guildford",
    "Haslemere",
    "Horley",
    "Leatherhead",
    "Oxted",
    "Redhill",
    "Reigate",
    "Staines-upon-Thames",
    "Sunbury-on-Thames",
    "Virginia Water",
    "Walton-on-Thames",
    "Weybridge",
    "Woking",
]
major_surrey_settlements = [
    each_string.lower() for each_string in MAJOR_SURREY_SETTLEMENTS
]


## CHART 2
# Scale parameter for bubble chart (affects size of bubbles)
SCALE_BUBBLE = 10


## CHART 3
# Selected skill to focus on (in third chart)
CHOSEN_SKILL = "SQL"

# Drop occupations that require chosen skill in less than 5% of job adverts
MINIMUM_PERCENT = 5

# Drop occupations that were advertised less than 10 times
MINIMUM_JOB_COUNT = 10

# %% [markdown]
# # 1. What salary ranges are associated with popular digital skills?

# %% [markdown]
# ### Load UK adverts

# %%
job_ads_uk = get_cached_job_ads("06-09-2021", "18-10-2021")
job_ads_uk += get_cached_job_ads("18-10-2021", "29-11-2021")

# %% [markdown]
# ### Extract digital skills (and salaries) from UK adverts

# %%
# Dictionary of digital skills
digital_skills = {}

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
            if (
                one_skill["label_cluster_0"]
                == "Information & Communication Technologies"
            ):

                # Name of the skill
                one_digital_skill = one_skill["preferred_label"]

                # If it's a new digital skill
                if one_digital_skill not in digital_skills:
                    digital_skills[one_digital_skill] = {
                        "skill_count": 0,
                        "label": one_digital_skill,
                        "min_salaries": [],
                        "max_salaries": [],
                    }

                # Add one to the count of that skill
                digital_skills[one_digital_skill]["skill_count"] += 1

                # Capture salaries (if present) and annualise
                salaries = annualises_salary(one_job)
                if salaries[0] is not None:
                    digital_skills[one_digital_skill]["min_salaries"].append(
                        salaries[0]
                    )
                    digital_skills[one_digital_skill]["max_salaries"].append(
                        salaries[1]
                    )


# %% [markdown]
# ### Identify most common digital skills and their salary ranges

# %%
# Number of digital skills
print("Number of digital skills: " + str(len(digital_skills)))

# Sort digital skills by frequency
digital_skills_sorted = sorted(
    digital_skills.values(), key=lambda k: k["skill_count"], reverse=True
)

# The top 30 digital skills account for what percentage of all mentions (of digital skills)
top_skills_percent = (
    100
    * sum(
        [value["skill_count"] for value in digital_skills_sorted[0:NO_DIGITAL_SKILLS]]
    )
    / sum([value["skill_count"] for value in digital_skills_sorted])
)
print(
    "The top "
    + str(NO_DIGITAL_SKILLS)
    + " digital skills account for "
    + str(round(top_skills_percent, 2))
    + "% of all digital skills mentioned"
)

# Extract the names of all digital skills
digital_skills_names = [value["label"] for value in digital_skills_sorted]

# Identify the most common digital skills
common_digital_skills = digital_skills_names[0:NO_DIGITAL_SKILLS]

# Find the median of the min and max salaries associated with each digital skill
for value in digital_skills_sorted:

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
# ### Chart the most frequently mentioned digital skills and their associated salaries

# %%
# Figure
fig, ax = plt.subplots(figsize=(12, 15))

# Data for chart
y = list(range(NO_DIGITAL_SKILLS))
y.reverse()
x_median_min = [value["median_min_salaries"] for value in digital_skills_sorted][
    0:NO_DIGITAL_SKILLS
]
x_median_max = [value["median_max_salaries"] for value in digital_skills_sorted][
    0:NO_DIGITAL_SKILLS
]

# Horizontal line and scatter points
plt.hlines(y, x_median_min, x_median_max, colors="black", linewidth=1, alpha=0.5)
plt.scatter(x_median_min, y, s=30, c=COLORS[2])
plt.scatter(x_median_max, y, s=30, c=COLORS[3])

# Add name of each digital skill
label_pos = [
    0.5 * (value["median_min_salaries"] + value["median_max_salaries"])
    for value in digital_skills_sorted[0:NO_DIGITAL_SKILLS]
]
for index, one_skill in enumerate(digital_skills_sorted[0:NO_DIGITAL_SKILLS]):
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
plt.ylabel("Most-mentioned digital skills", fontsize=18, rotation=0, weight="bold")
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
    PATH_TO_CHARTS + "digital_skills_and_salaries.png", dpi=200, bbox_inches="tight"
)


# %% [markdown]
# # 2. Which popular digital skills are required in frequently-advertised occupations (in Sussex)?

# %% [markdown]
# ### Load Sussex and Surrey job adverts

# %%
with open(PATH_TO_SUSSEX_DATA) as json_file:
    job_ads_sussex_surrey = json.load(json_file)

# %%
# Remove non-Sussex locations

# To store all Sussex (i.e. non Surrey) jobs
job_ads_sussex = []

# Loop over adverts
for one_advert in job_ads_sussex_surrey:

    # If the advert contains a location
    if "job_location_raw" in one_advert:

        # Extract location data
        split_location = one_advert["job_location_raw"].lower().split(",")
        narrow_location = split_location[0]
        broad_location = split_location[1]

        # If the advert's location does not mention Surrey or a major settlement within Surrey
        if (
            narrow_location not in major_surrey_settlements
            and broad_location not in major_surrey_settlements
        ):

            # Save job advert
            job_ads_sussex.append(one_advert)

# %% [markdown]
# ### Find all occupation names

# %%
occupation_names = []

# Loop over job ads
for one_job in job_ads_sussex:

    # If it's a new occupation name
    if one_job["sector"] not in occupation_names:

        # Add it to list
        occupation_names.append(one_job["sector"])

# %% [markdown]
# ### Create a dictionary of occupations, containing the digital skills and their counts

# %%
# Dictionary of occupations and the digital skills they rely on
occup_by_digital = {
    value: {
        "job_count": 0,
        "job_count_digital": 0,  # No. of adverts that require at least one digital skill
        "skill_counts": [0 for value in range(0, len(digital_skills_names))],
        "label": value,
    }
    for value in occupation_names
}

# Loop over job ads
for one_job in job_ads_sussex:

    # If the job advert contains skills and is not an excluded recruiter:
    if (
        "skills" in one_job["features"]
        and one_job["company_raw"] not in EXCLUDED_RECRUITERS
    ):

        # Name of occupation (called 'sector')
        one_occupation = one_job["sector"]

        # Count job (only those that have skills)
        occup_by_digital[one_occupation]["job_count"] += 1

        # Start by assuming that no digital skills are required
        requires_one_digital_skill = False

        # Loop over skills
        for one_skill in one_job["features"]["skills"]["skills"]:

            # If the skill lives in the digital cluster
            if (
                one_skill["label_cluster_0"]
                == "Information & Communication Technologies"
            ):

                # The job requires at least one digital skill
                requires_one_digital_skill = True

                # Name of the skill
                one_digital_skill = one_skill["preferred_label"]

                # Add one to the count of that skill for that occupation
                occup_by_digital[one_occupation]["skill_counts"][
                    digital_skills_names.index(one_digital_skill)
                ] += 1

        # If the job requires at least one digital skill
        if requires_one_digital_skill == True:
            occup_by_digital[one_occupation]["job_count_digital"] += 1


# %% [markdown]
# ### For each occupation and digital skill, calculate the percentage of job adverts in that occupation which mention that specific digital skill

# %%
# Loop over occupations
for key_occupation, value_occupation in occup_by_digital.items():

    # Percentage of job adverts that require at least one digital skill
    if value_occupation["job_count"] > 0:
        value_occupation["percent_digital_jobs"] = (
            100 * value_occupation["job_count_digital"] / value_occupation["job_count"]
        )
    else:
        value_occupation["percent_digital_jobs"] = 0

    # If at least one job advert in that occupation required a digital skill
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
# Sort occupations by those that most frequently require at least one digital skill
occupations_sorted = sorted(
    occup_by_digital.values(), key=lambda k: k["percent_digital_jobs"], reverse=True
)

# Identify the names of digitally-intensive, and non-small, occupations ONLY
digital_occupation_names = [
    value["label"]
    for value in occupations_sorted
    if value["job_count"] >= MINIMUM_JOB_COUNT
][0:NO_OCCUPATIONS]

# Reverse so that digitally-intensive occupations are shown at the top of the chart
digital_occupation_names.reverse()

# %% [markdown]
# ### Chart showing the percentage of adverts for a given occupation that require a specific digital skill
# ##### (Digitally-intensive occupations and most mentioned digital skills only)

# %%
# Figure
fig, ax = plt.subplots(figsize=(12, 12))

# Plot scatter points for each occupation
for index_occupation, one_occupation in enumerate(digital_occupation_names):

    # Alternative colors so the chart is easier to read
    color_bubble = COLORS[0] if index_occupation % 2 == 0 else COLORS[1]

    # Only retrieve 'percents' for the most common digital skills
    sizes = [
        value * SCALE_BUBBLE
        for index, value in enumerate(
            occup_by_digital[one_occupation]["skill_percents"]
        )
        if digital_skills_names[index] in common_digital_skills
    ]

    # Plot digital skills
    sc = ax.scatter(
        list(range(NO_DIGITAL_SKILLS)),
        [index_occupation] * NO_DIGITAL_SKILLS,
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
plt.xlabel("Most-mentioned digital skills", fontsize=18, weight="bold")
ax.xaxis.set_label_coords(0.35, 1.36)
plt.ylabel("Digital occupations", fontsize=18, rotation=0, weight="bold")
ax.yaxis.set_label_coords(-0.15, 0.97)

# Y axis labels
ax.set_yticks(list(range(NO_OCCUPATIONS)))
ax.set_yticklabels(
    [value.replace("&amp;", "&") for value in digital_occupation_names], fontsize=16
)

# X axis labels
ax.xaxis.tick_top()
ax.set_xticks(list(range(NO_DIGITAL_SKILLS)))
ax.set_xticklabels(
    [value.title() for value in common_digital_skills],
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
    PATH_TO_CHARTS + "digital_skills_and_occupations.png", dpi=200, bbox_inches="tight"
)

# %% [markdown]
# # 3. Which occupations rely on one particular digital skill (in Sussex): SQL?

# %%
# Exclude occupations where the chosen skill is required in less than 5% of adverts for the occupation
# and exclude occupations with very few adverts
occupations_one_skill = [
    value
    for value in occupations_sorted
    if value["skill_percents"][digital_skills_names.index(CHOSEN_SKILL)]
    >= MINIMUM_PERCENT
    and value["job_count"] >= MINIMUM_JOB_COUNT
]
occupations_one_skill.reverse()

# %%
# Figure
fig, ax = plt.subplots(figsize=(15, 12))

x = [
    one_occupation["skill_percents"][digital_skills_names.index(CHOSEN_SKILL)]
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
    PATH_TO_CHARTS + "one_digital_skill_and_occupations.png",
    dpi=200,
    bbox_inches="tight",
)
