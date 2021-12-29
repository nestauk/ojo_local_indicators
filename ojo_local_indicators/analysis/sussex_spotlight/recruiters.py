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

# %%
# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# %% [markdown]
# ###  Who are the largest recruiters in Sussex?

# %%
sussex = cd.open_data_dump(
    f"{project_directory}/outputs/data/sussex_07-06-2021_22-11-2021.json"
)

# %%
created = [d["created"] for d in sussex if "created" in d]
company = [d["company_raw"] for d in sussex if "company_raw" in d]

# %%
rec = pd.DataFrame(list(zip(company, created)), columns=["recruiter", "created"])

# %%
rec.head(5)

# %%
type_rec = [
    "r",
    "r",
    "organisation",
    "r",
    "organisation",
    "r",
    "organisation",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
]

# %%
test = rec["recruiter"].value_counts(normalize=True).mul(100).head(20).reset_index()
test["type"] = type_rec
test.set_index("index", inplace=True)

# %%
test["recruiter"].plot(kind="bar", figsize=(15, 7), color=["#18A48C"], alpha=0.7)
plt.title("Top 30 companies posting vacancies - Sussex Nuts 2 region", fontsize=14)

# %% [markdown]
# UK

# %%
uk_sample = cd.open_data_dump(
    f"{project_directory}/outputs/data/uk_sample_07-06-2021_22-11-2021.json"
)

# %%
sussex[2]

# %%
created = [d["created"] for d in uk_sample if "created" in d]
company = [d["company_raw"] for d in uk_sample if "company_raw" in d]

# %%
rec = pd.DataFrame(list(zip(company, created)), columns=["recruiter", "created"])

# %%
rec.head(10)

# %%
type_rec = [
    "r",
    "r",
    "organisation",
    "r",
    "organisation",
    "r",
    "organisation",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
    "recruiter",
]

# %%
test = rec["recruiter"].value_counts(normalize=True).mul(100).head(20).reset_index()
# test['type'] = type_rec
test.set_index("index", inplace=True)

# %%
test["recruiter"].plot(kind="bar", figsize=(15, 7), color=["#0000FF"], alpha=0.7)
plt.title("Top 30 companies posting vacancies - UK", fontsize=14)

# %%
