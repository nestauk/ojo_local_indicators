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
from collections import Counter
import pandas as pd


# %% [markdown]
# ### Skills / salaries

# %%
def get_skills(data):
    """Get skill field from OJO list of dictionaries."""
    skills = [
        d["features"].get("skills", {}).get("skills") for d in data if "features" in d
    ]
    # Return skills section of list of ditionaries
    return skills


# %%
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
def combine(dictionaries):
    """Combines the result of skill_count to give the list of 1s per skill group"""
    combined_dict = {}
    for dictionary in dictionaries:
        for key, value in dictionary.items():
            combined_dict.setdefault(key, []).append(value)
    return combined_dict


# %%
def get_salary_fields(data, field):
    """Gets the salary field from OJO list of dictionaries."""
    salary_field = [
        d["features"].get("salary", {}).get(field) for d in data if "features" in d
    ]
    return salary_field


# %%
def locations_skills_df(area, cluster):
    """Creates a dataframe of the percentage of ads requiring each skill type from a
    selected area and skill group"""
    clusters = combine(cluster)
    skills = []
    for skill in list(clusters.keys()):
        skills.append(sum(clusters[skill]) / len(area))
    df_area = pd.DataFrame(
        {"Skill": list(clusters.keys()), "Adverts requiring skill group": skills}
    )
    df_area = df_area[df_area["Skill"].notna()]
    return df_area


# %%
def min_max_dfs(cluster_2, salary_list, salary_type):
    """Creates a dataframe of salary mins/max values for each skill group."""
    salary_sussex = pd.DataFrame(cluster_2)
    salary_sussex["salary"] = salary_list
    salary_sussex.dropna(subset=["salary"], inplace=True)
    salary_sussex.fillna(0, inplace=True)
    salary_sussex["type"] = salary_type
    return salary_sussex


# %%
def skills_salary_df(skills_sussex, top_skills):
    """Creates a new df with salary and skill group listed per row."""
    skills_10 = []  # Empty list to store the dfs
    # Loop through skill groups and clean each subset
    for skill_name in top_skills:
        skill = skills_sussex[[skill_name, "salary", "type"]].copy()
        skill = skill[skill[skill_name] != 0]
        skill.drop([skill_name], axis=1, inplace=True)
        skill["skill group"] = skill_name
        skills_10.append(skill)
    # Concatenate dfs back together
    skill_salary = pd.concat(skills_10, axis=0)
    return skill_salary


# %% [markdown]
# ### Occupations & Industries

# %%
def remove_sussex_uk(sussex, uk_sample):
    """Removing vacancies in the Sussex dictionary for 'rest of UK sample'"""
    # Sussex ids
    j_id = [d["id"] for d in sussex if "id" in d]
    # Removing Sussex from UK sample
    uk_sample = [d for d in uk_sample if d["id"] not in j_id]
    return uk_sample


# %%
def pct_share_sector(area_dict, area_name, sector):
    """Creates a df with the percent share of vacancies per sector for area defined."""
    sector_list = [d[sector] for d in area_dict if sector in d]
    sec = pd.DataFrame.from_dict(
        Counter(sector_list), orient="index", columns=["sector"]
    ).reset_index()
    sec["sector"] = (sec["sector"] / sum(sec["sector"])) * 100
    sec["index"] = sec["index"].str.replace("&amp; ", "")
    sec["area"] = area_name
    return sec


# %%
def combine_pct_share(
    area_dict1, area_dict2, area_name1, area_name2, sector, sector_name
):
    """Combines the pct share results for two areas."""
    ind1 = pct_share_sector(area_dict1, area_name1, sector)
    ind2 = pct_share_sector(area_dict2, area_name2, sector)
    indust = ind1.append(ind2)
    indust.columns = [sector_name, "percentage share", "location"]
    return indust
