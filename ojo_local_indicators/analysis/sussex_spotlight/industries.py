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

# %%
print(len(sussex))
print(len(uk_sample))

# %% [markdown]
# ### Which industries have advertised the most vacancies in Sussex, and how does this compare to the rest of the UK?

# %%
industry = [d["parent_sector"] for d in sussex if "parent_sector" in d]
created = [d["created"] for d in sussex if "created" in d]

industry_uk = [d["parent_sector"] for d in uk_sample if "parent_sector" in d]
created_uk = [d["created"] for d in uk_sample if "created" in d]

# %%
ind = pd.DataFrame(list(zip(industry, created)), columns=["industry", "created"])
ind_uk = pd.DataFrame(
    list(zip(industry_uk, created_uk)), columns=["industry", "created"]
)

# %%
ind["created"] = pd.to_datetime(ind["created"], format="%Y-%m-%d")
ind["industry"] = ind["industry"].str.replace("&amp; ", "")

ind_uk["created"] = pd.to_datetime(ind_uk["created"], format="%Y-%m-%d")
ind_uk["industry"] = ind_uk["industry"].str.replace("&amp; ", "")

# %%
ind_uk_sussex = pd.concat(
    {
        "Sussex": ind["industry"].value_counts(normalize=True).mul(100),
        "UK": ind_uk["industry"].value_counts(normalize=True).mul(100),
    },
    axis=1,
)

# %%
ind_comb = ind["industry"].value_counts(normalize=True).mul(100).reset_index()
ind_uk_comb = ind_uk["industry"].value_counts(normalize=True).mul(100).reset_index()

# %%
ind_comb["area"] = "Sussex"
ind_uk_comb["area"] = "UK"

# %%
ind_comb.sort_values(by=["industry"], ascending=False, inplace=True)
ind_uk_comb.sort_values(by=["industry"], ascending=False, inplace=True)

# %%
indust_comb = ind_comb.append(ind_uk_comb)

# %%
indust_comb.columns = ["industry", "percentage share", "location"]

# %%
indust_comb.head(6)

# %%
# alt.themes.enable('none')

# %%
import numpy as np

# %%
from altair_saver import save

# %%
domain = ["Sussex", "UK"]
range_ = ["#18A48C", "#0000FF"]


chart = (
    alt.Chart(
        indust_comb,
        title="Percentage of vacancies by industry - Sussex compared to the rest of the UK",
    )
    .mark_tick(filled=True, thickness=3, opacity=0.7)
    .encode(
        # x='percentage share:Q',
        x=alt.X(
            "percentage share:Q",
            sort="-x",
            axis=alt.Axis(title="Percentage share", grid=False),
        ),
        y=alt.Y("industry:O", sort="-x", axis=alt.Axis(title="Industry", grid=True)),
        color=alt.Color(
            "location",
            legend=alt.Legend(title="Location"),
            scale=alt.Scale(domain=domain, range=range_),
        ),
    )
    .properties(width=650, height=1000)
    .configure_axis(labelFontSize=12, titleFontSize=14)
    .configure_title(fontSize=16)
    .configure_legend(titleFontSize=14, labelFontSize=12)
)

chart  # .resolve_scale(y='independent')

save(chart, "vacancies_industry_sussex_uk.html")

# %% [markdown]
# ### Time

# %%
ind.head(1)

# %%
ind_time = ind.copy()
ind_uk_time = ind_uk.copy()
ind_time["month"] = pd.DatetimeIndex(ind_time["created"]).month
ind_time["count"] = 1
ind_time.drop("created", axis=1, inplace=True)
# ind_time = ind_time.groupby(by=["month","industry"]).sum().reset_index()

# %%
ind_uk_time["month"] = pd.DatetimeIndex(ind_uk_time["created"]).month
ind_uk_time["count"] = 1
ind_uk_time.drop("created", axis=1, inplace=True)

# %%
ind_time = ind_time.groupby(by=["month", "industry"]).sum().reset_index()
ind_uk_time = ind_uk_time.groupby(by=["month", "industry"]).sum().reset_index()

# %%
from sklearn.preprocessing import MinMaxScaler

# %%
scaler = MinMaxScaler()
ind_uk_time["UK"] = scaler.fit_transform(ind_uk_time["count"].values.reshape(-1, 1))
ind_time["Sussex"] = scaler.fit_transform(ind_time["count"].values.reshape(-1, 1))

# %%
ind_uk_time.drop("count", axis=1, inplace=True)
ind_time.drop("count", axis=1, inplace=True)

# %%
ind_time_comb = pd.merge(
    ind_uk_time,
    ind_time,
    how="left",
    left_on=["month", "industry"],
    right_on=["month", "industry"],
)

# %%
ind_time_comb.head(5)

# %%
ind_time_6 = ind_time_comb[
    ind_time_comb["industry"].isin(
        [
            "Admin, Secretarial PA",
            "Education",
            "Social Care",
            "IT Telecoms",
            "Accountancy",
            "Construction Property",
        ]
    )
]

# %%
ind_time_6.head(5)

# %%
fig = px.area(
    ind_time_6.set_index("month"),
    facet_col="industry",
    facet_col_wrap=2,
    color_discrete_map={
        "UK": "#0000FF",
        "Sussex": "#18A48C",
    },
    title="Most frequent Sussex industries - Vacancies over time (compared to UK)",
)

fig.update_layout(
    xaxis=dict(
        tickmode="array",
        tickvals=[6, 7, 8, 9, 10, 11],
        ticktext=["Jun", "Jul", "Aug", "Sep", "Oct", "Nov"],
        tickangle=45,
    ),
    xaxis2=dict(
        tickmode="array",
        tickvals=[6, 7, 8, 9, 10, 11],
        ticktext=["Jun", "Jul", "Aug", "Sep", "Oct", "Nov"],
        tickangle=45,
    ),
    legend_title_text="Location",
    template=None,
    autosize=False,
    width=900,
    height=600,
)

fig["layout"]["yaxis"]["title"]["text"] = ""
fig["layout"]["yaxis5"]["title"]["text"] = ""
fig["layout"]["yaxis3"]["title"]["text"] = "Count of vacancies (standardised)"

fig.show()

# import plotly.offline as py

# py.iplot(fig, filename="test")

# %%
import plotly.io as pio

pio.write_image(fig, "sussex_uk_top_6_ind_over_time.png", scale=5)

# %%
