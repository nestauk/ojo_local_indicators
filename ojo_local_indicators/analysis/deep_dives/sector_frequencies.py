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
# Look at industry frequencies first

# %%
# Import libraries
import ojo_local_indicators
import ojo_local_indicators.getters.open_data as od
from collections import Counter
import pandas as pd

# %%
# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# Get data
sussex = od.sussex
uk_sample = od.uk_sample

# %%
len(sussex)

# %%
sector_list = [d["parent_sector"] for d in sussex if "parent_sector" in d]
ind = pd.DataFrame.from_dict(
    Counter(sector_list), orient="index", columns=["industry_count"]
).reset_index()

# %%
sector_list_uk = [d["parent_sector"] for d in uk_sample if "parent_sector" in d]
ind_uk = pd.DataFrame.from_dict(
    Counter(sector_list_uk), orient="index", columns=["industry_count"]
).reset_index()

# %%
ind_uk

# %%
d = {
    "key_sector": [
        "Engineering and Manufacturing + Construction",
        "Visitor and Cultural Industries (includes Hospitality, Cultural & Arts)",
        "Land-based (includes Agriculture and Viticulture)",
        "Health and Care (includes Bio Life Sciences and Pharmaceutical)",
    ],
    "count_sussex": [2925, 915, 0, 2675],
    "industries": [
        "Manufacturing, Construction & Property, Engineering",
        "Hospitality & Catering, Leisure & Tourism",
        "-",
        "Health & Medicine, Social Care, Scientific",
    ],
}
df = pd.DataFrame(data=d)

# %%
d = {
    "key_sector": [
        "Engineering and Manufacturing + Construction",
        "Visitor and Cultural Industries (includes Hospitality, Cultural & Arts)",
        "Land-based (includes Agriculture and Viticulture)",
        "Health and Care (includes Bio Life Sciences and Pharmaceutical)",
    ],
    "industries": [
        "Manufacturing, Construction & Property, Engineering",
        "Hospitality & Catering, Leisure & Tourism",
        "-",
        "Health & Medicine, Social Care, Scientific",
    ],
    "count_uk_sample": [4932, 1069, 0, 4642],
}
df_uk = pd.DataFrame(data=d)

# %%
df

# %%
df_uk["count_sussex"] = list(df.count_sussex)

# %%
df_uk

# %%
print(len(sussex))
print(len(uk_sample))

# %%
