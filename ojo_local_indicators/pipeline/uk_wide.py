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
import ojo_local_indicators
import ojo_local_indicators.pipeline.clean_data as cd
from ojd_daps.dqa.data_getters import get_cached_job_ads

# %%
# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR


# %%
def get_uk_ads():
    """Get UK ads for June-Nov 2021 OJO list of dictionaries."""
    # Get cached jobs for period
    job_ads1 = get_cached_job_ads("07-06-2021", "19-07-2021")
    job_ads2 = get_cached_job_ads("19-07-2021", "30-08-2021")
    job_ads3 = get_cached_job_ads("30-08-2021", "11-10-2021")
    job_ads4 = get_cached_job_ads("11-10-2021", "22-11-2021")
    job_ads = job_ads1 + job_ads2 + job_ads3 + job_ads4  # Combine
    # Remove duplicates
    filtered_dict = {(d["id"]): d for d in job_ads}
    job_ads_de_dup = [value for value in filtered_dict.values()]
    # Apply fixes
    fixes = pd.read_excel(f"{project_directory}/inputs/data/nuts_2_fixes.xlsx")
    fixes = fixes[["job_location_raw", "Code"]].copy()
    # Locations list (correct names)
    locations_n = cd.get_location_fields(job_ads, "nuts_2_name")
    locations_c = cd.get_location_fields(job_ads, "nuts_2_code")
    locations_n = list(dict.fromkeys(locations_n))
    locations_c = list(dict.fromkeys(locations_c))
    locations_n = [i for i in locations_n if i]
    locations_c = [i for i in locations_c if i]
    locations = pd.DataFrame(
        list(zip(locations_n, locations_c)), columns=["Name", "Code"]
    )
    fixes = fixes.merge(locations, on="Code", how="left")
    # Takes about 5 mins...
    for index, row in fixes.iterrows():
        for my_dict in job_ads_de_dup:
            if all(k in my_dict for k in ("job_location_raw", "features")):
                if my_dict["job_location_raw"] == row["job_location_raw"]:
                    if "location" in my_dict["features"]:
                        my_dict["features"]["location"]["nuts_2_code"] = row["Code"]
                        my_dict["features"]["location"]["nuts_2_name"] = row["Name"]
    return job_ads_de_dup  # Return job ads


# %%
def sussex_fix():
    """Temporary split of Sussex and surrey from Nuts 2"""

    sussex = cd.open_data_dump(
        f"{project_directory}/outputs/data/sussex_07-06-2021_22-11-2021_surrey_rem.json"
    )
    for my_dict in sussex:
        my_dict["features"]["location"]["nuts_2_code"] = "Sussex"
        my_dict["features"]["location"]["nuts_2_name"] = "Sussex"
    j_id = [d["id"] for d in sussex if "id" in d]
    job_ads_de_dup = [d for d in job_ads_de_dup if d["id"] not in j_id]
    job_ads_de_dup = job_ads_de_dup + sussex
    return job_ads_de_dup  # Return job ads


# %%
def create_nuts_map_divergent(
    df, col_val, col_la, col_range, min_scale, max_scale, sort, mid_scale
):
    """Diverging colours nuts map of the uk"""
    # Creating configs for color,selection,hovering
    geo_select = alt.selection_single(fields=["reach_area"])
    color = alt.condition(
        geo_select,
        alt.Color(
            col_val + ":Q",
            scale=alt.Scale(
                range=col_range, domain=[min_scale, max_scale], domainMid=0
            ),
            sort=sort,
        ),
        alt.value("lightgray"),
    )
    # Creating an altair map layer
    choro = (
        alt.Chart(df)
        .mark_geoshape(stroke="black")
        .encode(
            color=color,
            tooltip=[
                alt.Tooltip(col_la + ":N", title="Area Name"),
                alt.Tooltip(
                    col_val + ":Q",
                    title=col_val,
                    format="1.2f",
                ),
            ],
        )
        .add_selection(geo_select)
        .properties(width=650, height=800)
    ).configure_view(strokeWidth=0)
    return choro


# %%
def sector_df(uk_sample, sector, sec_name):
    """industry or occupations df from job ads"""
    sector_uk = [d[sector] for d in uk_sample if sector in d]
    created_uk = [d["created"] for d in uk_sample if "created" in d]
    sec_uk = pd.DataFrame(
        list(zip(sector_uk, created_uk)), columns=[sec_name, "created"]
    )
    sec_uk["created"] = pd.to_datetime(sec_uk["created"], format="%Y-%m-%d")
    sec_uk[sec_name] = sec_uk[sec_name].str.replace("&amp; ", "")
    sec_uk.set_index("created", inplace=True)
    sec_uk.sort_index(inplace=True)
    return sec_uk
