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
# ### What skills are in greatest demand in Sussex? How do these differ from the rest of the UK?

# %%
# Import libraries
import ojo_local_indicators
import ojo_local_indicators.getters.open_data as od
import ojo_local_indicators.pipeline.sussex_spotlight as ss
import pandas as pd

# from collections import Counter
import seaborn as sns
from textwrap import wrap
import matplotlib.pyplot as plt

# %%
# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# %%
# Get data
sussex = od.sussex

# %%
# Calling skills functions to create skills % df from Sussex dictionary
sussex_skills = ss.get_skills(sussex)
cluster_2 = ss.skill_count(sussex_skills, "label_cluster_2")
df_sussex = ss.locations_skills_df(sussex, cluster_2)

# %% [markdown]
# ### What salaries are associated with the largest (or fastest-growing) skill groups in Sussex?

# %%
# Get the top skills in Sussex by the ratio of adverts requiring the skills
top_skills = list(
    df_sussex.sort_values(by="Adverts requiring skill group", ascending=False)[
        "Skill"
    ].head(11)
)

# %%
top_skills.pop(0)  # removing General Workplace Skills

# %%
# Get lists for min and max dfs
salary_max = ss.get_salary_fields(sussex, "max_annualised_salary")
salary_min = ss.get_salary_fields(sussex, "min_annualised_salary")

# %%
# DFs for salary min and max groups
skills_sussex_max = ss.min_max_dfs(cluster_2, salary_max, "max annualised salary")
skills_sussex_min = ss.min_max_dfs(cluster_2, salary_min, "min annualised salary")
# Combine
skills_sussex = pd.concat([skills_sussex_max, skills_sussex_min], axis=0)

# %%
# Slice by top skills for Sussex
skills_sussex = skills_sussex[top_skills + ["salary", "type"]]

# %%
# Creating skill_salary dataframe
skill_salary = ss.skills_salary_df(skills_sussex, top_skills)

# %%
fig, ax = plt.subplots(figsize=(20, 12))

# Remove grid and top / right borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(False)

# Set the order of the boxes
rank = (
    skill_salary.groupby("skill group")["salary"].mean().fillna(0).sort_values().index
)

# x labels
labels = [
    "Manufacturing & Mechanical Engineering",
    "Customer Services",
    "Office Adminstration",
    "Learning Support",
    "Workplace Safety Management",
    "Sales",
    "Data Analytics",
    "Financial Services",
    "Accounting",
    "Business & Project Management",
]

# Build plot
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

# Format plot
ax.legend(fontsize=20)
ax.set_title(
    "Salary distributions of the most common Sussex skills", fontsize=25, pad=25
)
ax.tick_params(axis="x", rotation=90)
plt.xticks(rotation=45, ha="right", fontsize=22, wrap=True)
plt.yticks(fontsize=20)
plt.xlabel("")
plt.ylabel("")
xlabels = ["\n".join(wrap(l, 22)) for l in labels]
ax.set_xticklabels(xlabels)
plt.tight_layout()

# Save figure
plt.savefig(
    f"{project_directory}/outputs/figures/sussex_spotlight/salary_distributions_top_5_skills_sussex_outliers_rem.jpg",
    format="jpg",
    dpi=1200,
    bbox_inches="tight",
)
