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
# from ojd_daps.dqa.data_getters import get_cached_job_ads
# from ojd_daps.dqa.data_getters import fetch_descriptions
# from ojd_daps.dqa.data_getters import get_valid_cache_dates
import ojo_local_indicators
import ojo_local_indicators.pipeline.sussex_spotlight as ss
from collections import Counter
import pandas as pd


# %%
def locations_skills_df(area, cluster):
    """Creates a dataframe of the percentage of ads requiring each skill type from a
    selected area and skill group"""
    clusters = ss.combine(cluster)
    skills = []
    for skill in list(clusters.keys()):
        skills.append(sum(clusters[skill]))
    df_area = pd.DataFrame(
        {"Skill": list(clusters.keys()), "Adverts requiring skill group": skills}
    )
    df_area = df_area[df_area["Skill"].notna()]
    return df_area


# %%
# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# %%
import ojo_local_indicators.getters.open_data as od

uk_ads = od.uk_sample

# %%
job_ads1 = get_cached_job_ads("07-06-2021", "19-07-2021")
job_ads2 = get_cached_job_ads("19-07-2021", "30-08-2021")
job_ads3 = get_cached_job_ads("30-08-2021", "11-10-2021")
job_ads4 = get_cached_job_ads("11-10-2021", "22-11-2021")

# %%
job_ads = job_ads1 + job_ads2 + job_ads3 + job_ads4

# %%
filtered_dict = {(d["id"]): d for d in job_ads}
uk_ads = [value for value in filtered_dict.values()]

# %%
print(len(job_ads), len(uk_ads))

# %%
uk_skills = ss.get_skills(uk_ads)

# %%
# uk_skills[0]

# %%
# Calling skills functions to create skills % df from Sussex dictionary
uk_skills = ss.get_skills(uk_ads)
cluster_2 = ss.skill_count(uk_skills, "label_cluster_2")

# %%
uk_skills_count = locations_skills_df(uk_ads, cluster_2)

# %% [markdown]
# - Engineering and Manufacturing + Construction
# - Visitor and Cultural Industries (includes Hospitality, Cultural & Arts)
# - Land-based (includes Agriculture and Viticulture)
# - Health and Care (includes Bio Life Sciences and Pharmaceutical)

# %%
construction = ["Construction"]

engineering = [
    "Electrical Engineering",
    "Manufacturing & Mechanical Engineering",
    "Construction",
    "Civil Engineering",
]
cultural = ["Food, Hospitality & Beauty Services", "Customer Services"]
health_care = [
    "Psychology & Mental Health",
    "Scientific Research",
    "Care & Social Work",
    "Medical Specialist Skills",
]

# %%
# uk_skills_count

# %%
sum(
    uk_skills_count[uk_skills_count.Skill.isin(construction)][
        "Adverts requiring skill group"
    ]
)

# %%
sum(
    uk_skills_count[uk_skills_count.Skill.isin(engineering)][
        "Adverts requiring skill group"
    ]
)

# %%
sum(
    uk_skills_count[uk_skills_count.Skill.isin(cultural)][
        "Adverts requiring skill group"
    ]
)

# %%
sum(
    uk_skills_count[uk_skills_count.Skill.isin(health_care)][
        "Adverts requiring skill group"
    ]
)

# %%
d = {
    "key_sector": [
        "Engineering and Manufacturing + Construction",
        "Visitor and Cultural Industries (includes Hospitality, Cultural & Arts)",
        "Land-based (includes Agriculture and Viticulture)",
        "Health and Care (includes Bio Life Sciences and Pharmaceutical)",
    ],
    "industries": [
        "Electrical Engineering, Manufacturing & Mechanical Engineering, 'Construction, Civil Engineering",
        "Food, Hospitality & Beauty Services, Customer Services",
        "-",
        "Psychology & Mental Health, Scientific Research, Care & Social Work, Medical Specialist Skills",
    ],
    "count_uk_sample": [277231, 318371, 0, 169591],
}
df_uk = pd.DataFrame(data=d)

# %%
df_uk.to_excel("key_sectors.xlsx", index=False)

# %%
uk_skills[0]

# %% [markdown]
# ### Looking at surface forms

# %%
# Calling skills functions to create skills % df from Sussex dictionary
uk_skills = ss.get_skills(uk_ads)
surface_form = ss.skill_count(uk_skills, "surface_form")

# %%
uk_sf_count = locations_skills_df(uk_ads, surface_form)

# %% [markdown]
# - Engineering and Manufacturing + Construction
# - Visitor and Cultural Industries (includes Hospitality, Cultural & Arts)
# - Land-based (includes Agriculture and Viticulture)
# - Health and Care (includes Bio Life Sciences and Pharmaceutical)

# %%
# Visitor and Cultural Industries (includes Hospitality, Cultural & Arts)
uk_sf_count[uk_sf_count["Skill"].str.contains("visitor")]

# %%
# Visitor and Cultural Industries (includes Hospitality, Cultural & Arts)
uk_sf_count[uk_sf_count["Skill"].str.contains("hospitality")]

# %%
# Visitor and Cultural Industries (includes Hospitality, Cultural & Arts)
uk_sf_count[uk_sf_count["Skill"].str.contains("art")].sort_values(
    by=["Adverts requiring skill group"], ascending=False
)

# %%
# Land-based (includes Agriculture and Viticulture)
uk_sf_count[uk_sf_count["Skill"].str.contains("agriculture")].sort_values(
    by=["Adverts requiring skill group"], ascending=False
)

# %%
# Land-based (includes Agriculture and Viticulture)
uk_sf_count[uk_sf_count["Skill"].str.contains("viticulture")].sort_values(
    by=["Adverts requiring skill group"], ascending=False
)

# %%
uk_sf_count

# %%
