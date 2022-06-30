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
# ### Which industries and occupations have advertised the most vacancies in Sussex, and how does this compare to the rest of the UK?

# %%
# Import libraries
import ojo_local_indicators
import ojo_local_indicators.getters.open_data as od
import ojo_local_indicators.pipeline.sussex_spotlight as ss
import pandas as pd
import plotly.express as px
import plotly.io as pio
import matplotlib.pyplot as plt

# %%
# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# Get data
sussex = od.sussex
uk_sample = od.uk_sample

# %%
# Removing Sussex from UK sample
uk_sample = ss.remove_sussex_uk(sussex, uk_sample)

# %%
# Dataset for occupations visualisation
occup = ss.combine_pct_share(
    sussex, uk_sample, "Sussex", "Rest of UK", "sector", "occupation"
)
occup = pd.pivot_table(
    occup, values="percentage share", index=["occupation"], columns=["location"]
)
occup["Difference from the rest of the UK"] = occup["Sussex"] - occup["Rest of UK"]
bar_plot_occup = (
    occup.sort_values(by="Sussex", ascending=False)
    .head(30)[["Difference from the rest of the UK", "Sussex"]]
    .sort_values(by=["Sussex", "Difference from the rest of the UK"])
)

# %%
# Dataset for industries visualisation
indust = ss.combine_pct_share(
    sussex, uk_sample, "Sussex", "Rest of UK", "parent_sector", "industry"
)

# %%
# Building bar plot
bar_plot_occup.plot(
    kind="barh", color=["#0000FF", "#18A48C"], alpha=0.7, figsize=(10, 20)
)

# Formatting plot
plt.gca().yaxis.grid(True, color="#646363", linestyle="-", linewidth=0.2)
plt.title(
    "Top 30 occupations Sussex compared to the rest of the UK", fontsize=30, pad=35
)
plt.ylabel("Occupations")
plt.yticks(fontsize=22)
plt.xticks(fontsize=22)
plt.xlabel("Percentage of vacancies", fontsize=25)
plt.ylabel("")
plt.box(on=False)
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left", fontsize="16")

# Displaying and saving
plt.show()
plt.savefig(
    f"{project_directory}/outputs/figures/sussex_spotlight/top_occupations_sussex_uk.jpg",
    dpi=1200,
    bbox_inches="tight",
)

# %%
# Building scatter plot
fig = px.scatter(
    indust,
    y="industry",
    x="percentage share",
    color="location",
    symbol="location",
    width=950,
    height=1100,
    color_discrete_sequence=["#18A48C", "#0000FF"],
)

# Formatting plot
fig.update_traces(marker_size=10)
fig.update_layout(
    paper_bgcolor="rgba(255,255,255,1)",
    plot_bgcolor="rgba(255,255,255,1)",
    showlegend=True,
    legend=dict(font=dict(family="Arial", size=19, color="black")),
    legend_title=dict(text="<b>Location</b>", font=dict(family="Arial", size=20)),
    title=dict(
        text="<b>Percentage of vacancies by industry -  Sussex compared to the rest of the UK</b>",
        x=0.5,
        font=dict(family="Arial", size=20, color="#000000"),
    ),
    xaxis_title="<b>Percentage share of vacancies</b>",
    font=dict(family="Arial", size=19, color="#000000"),
)
fig.update_yaxes(
    categoryorder="sum ascending",
    tickfont_family="Arial",
    title="",
    showline=True,
    linewidth=1,
    linecolor="black",
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
)
fig.update_xaxes(tickfont_family="Arial", showline=True, linewidth=1, linecolor="black")

# Saving and displaying plot
pio.write_image(
    fig,
    f"{project_directory}/outputs/figures/sussex_spotlight/industries_sussex_uk.svg",
    width=900,
    height=1100,
    scale=2,
)
fig.show()
