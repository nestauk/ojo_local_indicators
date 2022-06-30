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
# ### Which industries have experienced stronger/weaker growth?

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
ind_uk = uw.sector_df(uk_sample, "parent_sector", "industry")

# %%
# Set time periods
jun_aug = ind_uk["2021-06-01":"2021-08-31"]
sep_nov = ind_uk["2021-09-01":]

# %%
# Resample for value counts per day
ind_uk_day = ind_uk.resample("D")["industry"].value_counts().reset_index(name="count")
jun_aug_day = jun_aug.resample("D")["industry"].value_counts().reset_index(name="count")
sep_nov_day = sep_nov.resample("D")["industry"].value_counts().reset_index(name="count")

# %%
# Group by industry
jun_aug_sum = jun_aug_day.groupby(["industry"]).sum().reset_index()
sep_nov_sum = sep_nov_day.groupby(["industry"]).sum().reset_index()

# %%
# Column names for time periods
sep_nov_sum["time_period"] = "September to November"
jun_aug_sum["time_period"] = "June to August"

# %%
# Adjust for the difference in days
sep_nov_sum["count"] = (sep_nov_sum["count"] / 83) * 86
# Monthly sum df
months_sum = sep_nov_sum.append(jun_aug_sum, ignore_index=True).reset_index(drop=True)

# %%
# Reset indexe
ind_uk_day.set_index("created", inplace=True)
# Groupby month
ind_uk_month = (
    ind_uk_day.groupby([pd.Grouper(freq="M"), "industry"]).sum().reset_index()
)

# %%
# Top industries to include in plot
industries_top = [
    "Accountancy",
    "Accountancy (Qualified)",
    "Admin, Secretarial PA",
    "Construction Property",
    "Customer Service",
    "Education",
    "Engineering",
    "Health Medicine",
    "IT Telecoms",
    "Retail",
    "Sales",
    "Social Care",
    "Transport Logistics",
]
ind_uk_month_top = ind_uk_month[ind_uk_month["industry"].isin(industries_top)]

# %%
# Monthly totals per industry
ind_uk_month = ind_uk_month.pivot_table(
    index=["created"], columns="industry", values="count"
)
ind_uk_month.fillna(0, inplace=True)
ind_totals = ind_uk_month.T
ind_totals["total count"] = ind_totals[list(ind_totals.columns)].sum(axis=1)
ind_totals["Percent vacancies"] = (ind_totals["total count"] / 41515) * 100

# %%
# Percent change in time periods
time_periods = months_sum.pivot_table(
    index=["time_period"], columns="industry", values="count"
)
time_periods = time_periods.pct_change()
time_periods.drop(time_periods.index[:1], inplace=True)
time_periods = time_periods.T
time_periods.columns = ["Percent change"]
# Merge x2 dfs
time_periods = time_periods.merge(
    ind_totals["Percent vacancies"].to_frame(), left_index=True, right_index=True
)
time_periods = time_periods.reset_index().sort_values(
    by="Percent change", ascending=False
)
time_periods["Percent change"] = time_periods["Percent change"] * 100

# %%
# Plot growth of top industries
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params, font_scale=1.2)


# Plot each year's time series in its own facet
g = sns.relplot(
    data=ind_uk_month_top,
    x="created",
    y="count",
    col="industry",
    color="#0000FF",
    kind="line",
    linewidth=4,
    zorder=5,
    col_wrap=3,
    height=4,
    aspect=1.6,
    legend=False,
)

# Iterate over each subplot to customize further
for ind, ax in g.axes_dict.items():

    # Add the title as an annotation within the plot
    ax.text(0.6, 0.9, ind, transform=ax.transAxes, fontweight="bold", fontsize=20)

    # Plot every year's time series in the background
    sns.lineplot(
        data=ind_uk_month_top,
        x="created",
        y="count",
        units="industry",
        estimator=None,
        color=".7",
        linewidth=1,
        ax=ax,
    )

# Reduce the frequency of the x axis ticks
ax.set_xticks(ax.get_xticks()[::2])

# Tweak the supporting aspects of the plot
g.set_titles("")
g.set_axis_labels("", "Vacancies", fontsize=25)
g.tight_layout()

g.fig.subplots_adjust(top=0.9)
g.fig.suptitle(
    "Count of monthly vacancies per industry - June to Nov 2021", fontsize=37
)


# %%
chart = (
    alt.Chart(time_periods, title="Industry growth/decline June-Aug vs Sep-Nov")
    .mark_circle(opacity=0.5, stroke="#0000FF", color="#0000FF", strokeWidth=1)
    .encode(
        alt.X("Percent change:Q", axis=alt.Axis(labelAngle=0, grid=True)),
        alt.Y(
            "industry:N",
            sort=alt.SortField(field="Percent change", order="ascending"),
            axis=alt.Axis(grid=False),
        ),
        alt.Size(
            "Percent vacancies:Q",
            scale=alt.Scale(range=[0, 2000]),
            legend=alt.Legend(title="Percent of vacancies"),
        ),
    )
    .properties(width=850, height=570)
    .configure_axisX(labelAngle=90, labelFontSize=14, title=" ")
    .configure_axisY(labelFontSize=14, title=" ")
    .configure_title(fontSize=24, dy=-5)
    .configure_legend(titleColor="black", titleFontSize=14)
)

save(
    chart,
    f"{project_directory}/outputs/figures/uk_wide/Growth_decline_periods_industry.html",
)
chart
