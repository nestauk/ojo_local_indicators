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
# ### Which occupations have experienced stronger/weaker growth?

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
import ojo_local_indicators.pipeline.uk_wide as uw

import matplotlib.pyplot as plt
import altair as alt
from altair_saver import save
import plotly.express as px
import seaborn as sns

# %%
# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# %%
# UK sample
uk_sample = cd.open_data_dump(
    f"{project_directory}/outputs/data/uk_sample_07-06-2021_22-11-2021.json"
)

# %%
occ_uk = uw.sector_df(uk_sample, "sector", "occupations")

# %%
# Set time periods
jun_aug = occ_uk["2021-06-01":"2021-08-31"]
sep_nov = occ_uk["2021-09-01":]

# %%
# Resample for value counts per day
occ_uk_day = (
    occ_uk.resample("D")["occupations"].value_counts().reset_index(name="count")
)
jun_aug_day = (
    jun_aug.resample("D")["occupations"].value_counts().reset_index(name="count")
)
sep_nov_day = (
    sep_nov.resample("D")["occupations"].value_counts().reset_index(name="count")
)

# %%
# Group by occupation
jun_aug_sum = jun_aug_day.groupby(["occupations"]).sum().reset_index()
sep_nov_sum = sep_nov_day.groupby(["occupations"]).sum().reset_index()
# Column names for time periods
sep_nov_sum["time_period"] = "September to November"
jun_aug_sum["time_period"] = "June to August"

# %%
# Adjust for difference in days
sep_nov_sum["count"] = (sep_nov_sum["count"] / 83) * 86
# Monthly sum df
months_sum = sep_nov_sum.append(jun_aug_sum, ignore_index=True).reset_index(drop=True)
# Total sum occupations per month
occ_uk_day.set_index("created", inplace=True)
occ_uk_month = (
    occ_uk_day.groupby([pd.Grouper(freq="M"), "occupations"]).sum().reset_index()
)
occ_uk_month = occ_uk_month.pivot_table(
    index=["created"], columns="occupations", values="count"
)
occ_uk_month.fillna(0, inplace=True)
occ_totals = occ_uk_month.T
occ_totals["total count"] = occ_totals[list(occ_totals.columns)].sum(axis=1)
occ_totals["Percent vacancies"] = (occ_totals["total count"] / 41515) * 100

# %%
# Occupations with a greater than 1% share
occupations_top = list(occ_totals[occ_totals["Percent vacancies"] > 1].index)

# %%
# Percent change per time period
time_periods = months_sum.pivot_table(
    index=["time_period"], columns="occupations", values="count"
)
time_periods = time_periods.pct_change()
time_periods.drop(time_periods.index[:1], inplace=True)
time_periods = time_periods.T
time_periods.columns = ["Percent change"]
# Merge dfs
time_periods = time_periods.merge(
    occ_totals["Percent vacancies"].to_frame(), left_index=True, right_index=True
)
time_periods = time_periods.reset_index().sort_values(
    by="Percent change", ascending=False
)
time_periods["Percent change"] = time_periods["Percent change"] * 100
time_periods_top = time_periods[time_periods["occupations"].isin(occupations_top)]

# %%
# Plot occupations growth / decline
chart = (
    alt.Chart(time_periods_top, title="Occupations growth/decline June-Aug vs Sep-Nov")
    .mark_circle(opacity=0.5, stroke="#FF6E47", color="#FF6E47", strokeWidth=1)
    .encode(
        alt.X("Percent change:Q", axis=alt.Axis(labelAngle=0, grid=True)),
        alt.Y(
            "occupations:N",
            sort=alt.SortField(field="Percent change", order="ascending"),
            axis=alt.Axis(grid=False),
        ),
        alt.Size(
            "Percent vacancies:Q",
            scale=alt.Scale(range=[0, 1000]),
            legend=alt.Legend(title="Percent of vacancies"),
        ),
    )
    .properties(width=850, height=520)
    .configure_axisX(labelAngle=90, labelFontSize=14, title=" ")
    .configure_axisY(labelFontSize=14, title=" ")
    .configure_title(fontSize=24, dy=-5)
    .configure_legend(titleColor="black", titleFontSize=14)
)
save(
    chart,
    f"{project_directory}/outputs/figures/uk_wide/Growth_decline_periods_occupations.html",
)
chart
