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
# # Data for a Sankey chart showing the skills needed for the most common job titles

# %%
# Libraries
import csv
import json
import os
import string
from ojo_local_indicators import get_yaml_config, Path, PROJECT_DIR
from ojo_local_indicators.analysis.utils import clean_titles

# Path to adverts in Sussex
PATH_TO_SUSSEX_DATA = (
    str(PROJECT_DIR) + "/inputs/data/sussex_07-06-2021_22-11-2021.json"
)

# Path to save data file
PATH_TO_OUTPUT_DATA = str(PROJECT_DIR) + "/outputs/data/data_occupations.json"

# List of broad skills (needed to get the order right)
BROAD_SKILLS = [
    "Business Administration, Finance & Law",
    "Sales & Communication",
    "Education",
    "Engineering, Construction & Maintenance",
    "Food, Cleaning & Hospitality",
    "Healthcare, Social Work & Research",
    "Information & Communication Technologies",
    "Transversal skills",
]

# When cleaning job titles remove these terms
EXCLUDED_TERMS = [
    "part",
    "time",
    "team",
    "member",
    "month",
    "ftc",
    "immediate",
    "start",
    "up",
    "to",
    "fixed",
    "term",
]

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

# Number of job titles to include
NO_JOB_TITLES = 12


# %% [markdown]
# ### Load data

# %%
# Collect adverts for Surrey, East and West Sussex
with open(PATH_TO_SUSSEX_DATA) as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

# %% [markdown]
# ### Remove non-Sussex locations

# %%
# Remove non-Sussex locations

# To store all Sussex (i.e. non-Surrey) jobs
sussex_jobs = []

# Loop over adverts
for one_advert in jsonObject:

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
            sussex_jobs.append(one_advert)

# %% [markdown]
# ### Find the most popular job titles associated with different broad skills groups

# %%
# Create a dictionary of job titles for each broad skill group
broad_skills_plus_all = BROAD_SKILLS + ["All"]
all_job_titles = {one_broad_skill: {} for one_broad_skill in broad_skills_plus_all}

# Loop over adverts
for one_advert in sussex_jobs:

    # Identify features
    features = one_advert["features"]

    # If it's not a duplicate
    if features["is_duplicate"] == False and "skills" in features:

        # Clean job title
        job_title = clean_titles(one_advert["job_title_raw"], EXCLUDED_TERMS)

        # Loop over each skill
        for one_skill in features["skills"]["skills"]:

            # Skill names and groups
            broad_skill_group = one_skill["label_cluster_0"]
            narrow_skill_group = one_skill["label_cluster_2"]

            # Ignore if broad_skill_group is None
            if broad_skill_group is not None:

                # Add job title to broad skills group if it's not already there
                if job_title not in all_job_titles[broad_skill_group]:
                    all_job_titles[broad_skill_group][job_title] = {
                        "count": 0,
                        "job_title": job_title,
                    }

                # Add job title to the 'All' group if it's not already there
                if job_title not in all_job_titles["All"]:
                    all_job_titles["All"][job_title] = {
                        "count": 0,
                        "job_title": job_title,
                    }

                # Add one to count
                all_job_titles[broad_skill_group][job_title]["count"] += 1
                all_job_titles["All"][job_title]["count"] += 1

# %%
# Find the most mentioned job titles in each broad skill group, and overall

# Space to store top job titles
all_top_titles = {}

# Loop over broad skill groups
for key, value in all_job_titles.items():

    # Sort job titles
    all_job_titles_sorted = sorted(
        all_job_titles[key].values(), key=lambda k: k["count"], reverse=True
    )

    # Top 12 titles
    top_titles = [
        value["job_title"] for value in all_job_titles_sorted[0:NO_JOB_TITLES]
    ]

    # Store
    all_top_titles[key] = top_titles


# %% [markdown]
# ### Extract broad skill groups for each top title

# %%
# Create space
top_titles_skills = {}

# Loop over broad skill groups
for broad_category, _ in all_top_titles.items():

    # Create space
    top_titles_skills[broad_category] = {
        value: {"job_title": value, "skills": {}}
        for value in all_top_titles[broad_category]
    }

    # Loop over adverts
    for one_advert in sussex_jobs:

        # Identify features
        features = one_advert["features"]

        # If it's not a duplicate and contains skills
        if features["is_duplicate"] == False and "skills" in features:

            # Clean job title
            job_title = clean_titles(one_advert["job_title_raw"], EXCLUDED_TERMS)

            # If job title is a top title
            if job_title in all_top_titles[broad_category]:

                # Loop over skills
                for one_skill in features["skills"]["skills"]:

                    # Skill names and groups
                    broad_skill_group = one_skill["label_cluster_0"]
                    narrow_skill_group = one_skill["label_cluster_2"]

                    # Exclude skills that are not part of the taxonomy
                    if narrow_skill_group is not None:

                        # If new skill
                        if (
                            broad_skill_group
                            not in top_titles_skills[broad_category][job_title][
                                "skills"
                            ]
                        ):
                            top_titles_skills[broad_category][job_title]["skills"][
                                broad_skill_group
                            ] = {"count": 0, "broad_skill_group": broad_skill_group}

                        # Add one to total count
                        top_titles_skills[broad_category][job_title]["skills"][
                            broad_skill_group
                        ]["count"] += 1


# %%
# Convert the 'counts' of each skill group (for a given job title)
# into percentages (across all the skills mentioned for that job title)
# Round to 2dp

# Loop over broad skill groups:
for broad_category, _ in top_titles_skills.items():

    # Loop over top job titles
    for one_job_title, value_job_title in top_titles_skills[broad_category].items():

        # Calculate the total number of skills mentioned
        total_skill_count = sum(
            [value["count"] for _, value in value_job_title["skills"].items()]
        )

        # Loop over broad skill groups
        for one_skill, value_skill in value_job_title["skills"].items():

            # Calculate percentage and round to 2dp
            value_skill["percent"] = round(
                100 * value_skill["count"] / total_skill_count, 2
            )

# %% [markdown]
# ### Create nodes and links

# %%
# Create nodes
nodes_job_titles = []

# Loop over broad skill groups
for broad_category, _ in top_titles_skills.items():

    # Need to ensure the 'name' field is unique and so we add the name of the skill category
    # where it was most populous
    nodes_job_titles.extend(
        [
            {
                "name": value["job_title"].title() + " " + broad_category,
                "actual_name": value["job_title"].title(),
                "category": broad_category,
            }
            for key, value in top_titles_skills[broad_category].items()
        ]
    )

# Add nodes for the broad skill groups
nodes_skills = [{"name": value, "category": "Skill"} for value in BROAD_SKILLS]
nodes = nodes_job_titles[::-1] + nodes_skills

# %%
# Create links
links = []

# Loop over broad categories
for broad_category, _ in top_titles_skills.items():

    # Loop over top job titles
    for one_job_title, value_job_title in top_titles_skills[broad_category].items():

        # Links
        job_title = value_job_title["job_title"].title()

        # Loop over broad skill groups
        for one_skill, value_skill in value_job_title["skills"].items():

            broad_skill_group = value_skill["broad_skill_group"]

            links.append(
                {
                    "source": job_title + " " + broad_category,
                    "target": broad_skill_group,
                    "value": value_skill["percent"],
                    "category": broad_category,
                }
            )


# %%
list_occupations = {"nodes": nodes, "links": links}

# %% [markdown]
# ### Save the nodes and links

# %%
# Save the data file
with open(PATH_TO_OUTPUT_DATA, "w") as fp:
    json.dump(list_occupations, fp)
