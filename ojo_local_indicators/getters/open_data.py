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
import json
import ojo_local_indicators

# %%
# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# %%
sussex_file = "sussex_07-06-2021_22-11-2021_surrey_rem.json"
uk_sample_file = "uk_sample_07-06-2021_22-11-2021.json"


# %%
def open_json_data(file):
    """Loads and returns data from JSON file."""
    with open(file) as json_file:
        data = json.load(json_file)
    return data


# %%
sussex = open_json_data(f"{project_directory}/outputs/data/" + sussex_file)
uk_sample = open_json_data(f"{project_directory}/outputs/data/" + uk_sample_file)
