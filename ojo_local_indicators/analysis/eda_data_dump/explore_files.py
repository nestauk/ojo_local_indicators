# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     comment_magics: true
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.2
#   kernelspec:
#     display_name: ojo_local_indicators
#     language: python
#     name: ojo_local_indicators
# ---

# ## EDA of open jobs data dumps

# Exploratory data analysis of the April and July data-dumps. These are extracts of jobs from the Open-Jobs observatory collected in July and April 2021.

# Import libraries
import pandas as pd
import ojo_local_indicators
import ojo_local_indicators.pipeline.clean_data as cd
import json
import matplotlib.pyplot as plt
import missingno as msno

# %matplotlib inline

# Set directory
project_directory = ojo_local_indicators.PROJECT_DIR

# ### Create dataframe

# Calling the 'open data dump' and 'create_df' functions in the clean_data file. The create_df function transforms the list of dicts into dataframes and pulls some information from the features dictionary held within each dictionary.

# File names
july_json = "job_ads_no_descriptions-15-07-2021.json"
april_json = "job_ads_no_descriptions-15-04-2021.json"

# Read in JSON files
data_july = cd.open_data_dump(f"{project_directory}/inputs/data/" + july_json)
data_april = cd.open_data_dump(f"{project_directory}/inputs/data/" + april_json)

# Create dataframes using clean_data function
df_july = cd.create_df(data_july)  # July
df_april = cd.create_df(data_april)  # April

# ### Handling duplicate values

# Duplicated job ads are picked up by the open jobs algorthm and held in the is_duplicate field. Using value counts we look at the percentage of duplicate jobs per dataframes and then remove them.

# +
# Concatenating value counts of the duplicated columns in both dataframes and plotting results
pd.concat(
    {
        "July data": df_july["duplicated"].value_counts(normalize=True).mul(100),
        "April data": df_april["duplicated"].value_counts(normalize=True).mul(100),
    },
    axis=1,
).plot.bar()

# Setting titles and x/y labels
plt.title("Percent job title duplicated - July/April data dumps")
plt.xlabel("Is duplicated")
plt.ylabel("Percent")
# -

# Remove duplicated jobs for July
df_july.drop(df_july[df_july["duplicated"] == True].index, inplace=True)
# Remove duplicated jobs for April
df_april.drop(df_april[df_april["duplicated"] == True].index, inplace=True)

# Removing un-needed columns (completely empty or features - where results have already been pulled)
cd.remove_cols(df_july)
cd.remove_cols(df_april)

# ### Re-assign incorrect label for Brighton location

# During an initial quality check on the raw location field I found that the Brighton in Sussex local was incorrectly assigned to Merseyside. The re_assign_brighton function finds these cases and updates them to the correct Nuts 2 code and name.

# Applying the re-assign brighton function to both datasets
cd.re_assign_brighton(df_july)
cd.re_assign_brighton(df_july)

# ### Jobs by Nuts 2 region

# Looking at the number of jobs posted (comparing July and April) per Nuts 2 region.

# +
# Concatenating value counts of the nuts 2 name columns in both dataframes and plotting results
pd.concat(
    {
        "July data": df_july["nuts_2_name"].value_counts(normalize=True).mul(100),
        "April data": df_april["nuts_2_name"].value_counts(normalize=True).mul(100),
    },
    axis=1,
).plot(kind="barh", figsize=(10, 12))

# Setting titles and x/y labels
plt.title("Percentage of jobs by Nuts 2 region")
plt.xlabel("Percent")
plt.ylabel("Nuts 2 Regions")
# -

# ### Checking for missing values

# Looking at missingness in the datframes. First use the missingno library to check how missingness compares across columns. For the April dataset it looks like missing values are the same across the nuts 2 names and codes and the salary fields. For for the July dataset there is some difference in missingness across the salary features, although min and max and unit and currency are the same.

# Calling the matrix function in the missingno library
msno.matrix(df_july)

# Calling the matrix function in the missingno library
msno.matrix(df_april)

# Calling the percent_missing function to create a percent missing dataframe
percent_missing_july = cd.percent_missing(df_july)
percent_missing_april = cd.percent_missing(df_april)

# +
# Concatenating percent missing dataframes and plotting results
pd.concat(
    {
        "July data": percent_missing_july.tail(10),
        "April data": percent_missing_april.tail(10),
    },
    axis=1,
).plot(kind="barh", figsize=(7, 5))

# Setting titles and x/y labels
plt.title("Percent missing - July/April data")
plt.xlabel("Percent")
plt.ylabel("Columns")
# -

# ### Checking for unique values

# Looking at the count of unique values in each columns across both dataframes.

# +
# Concatenating nunique count in both dataframes and plotting results
pd.concat(
    {
        "July data": df_july.nunique().sort_values().head(8),
        "April data": df_april.nunique().sort_values().head(8),
    },
    axis=1,
).plot(kind="barh", figsize=(7, 5))

# Setting titles and x/y labels
plt.title("Number of unique values - July/April data (lower)")
plt.xlabel("Unique values")
plt.ylabel("Columns")
# -

pd.concat(
    {
        "July data": df_july.nunique().sort_values().tail(8),
        "April data": df_april.nunique().sort_values().tail(8),
    },
    axis=1,
).plot(kind="barh", figsize=(7, 5))
plt.title("No unique values - July/April data (upper)")
plt.xlabel("Unique values")
plt.ylabel("Columns")

# ### Time variation

# Looking at number of job posts over time (daily and weekly).

# Calling the time_index function to prepare the data for timeseries plots
df_july = cd.time_index(df_july)
df_april = cd.time_index(df_april)

# Plot of weekly jobs in July data-dump
df_july["jobs"].resample("W").sum().plot(style="-o", figsize=(10, 5))
plt.title("Count of weekly jobs posted - July data dump")
plt.xlabel("Created date")
plt.ylabel("Job count")

# Plot of daily jobs in July data-dump
df_july["jobs"].resample("D").sum().plot(style="-o", figsize=(10, 5))
plt.title("Count of daily jobs posted - July data dump")
plt.xlabel("Created date")
plt.ylabel("Job count")

# Plot of weekly jobs in April data-dump
df_april["jobs"].resample("W").sum().plot(style="-o", figsize=(10, 5))
plt.title("Count of weekly jobs posted - April data dump")
plt.xlabel("Created date")
plt.ylabel("Job count")

# Plot of daily jobs in April data-dump
df_april["jobs"].resample("D").sum().plot(style="-o", figsize=(10, 5))
plt.title("Count of daily jobs posted - April data dump")
plt.xlabel("Created date")
plt.ylabel("Job count")

# ### Save Sussex & non Sussex samples and export

# Slicing by sussex and non-sussex (random-sample of the same size) and saving csv files.

# Slice for Sussex and non-sussex
df_ukj2 = df_july.loc[
    df_july["nuts_2_code"] == "UKJ2"
].copy()  # Slice by UKJ2 - Surrey, East and West Sussex
df_uk = df_july.loc[df_july["nuts_2_code"] != "UKJ2"].copy()  # Slice by not UKJ2
# Non Sussex random sample
df_uk_sample = df_uk.sample(n=9158, random_state=2)

# Save csv files to data outputs folder
df_july.to_csv(f"{project_directory}/outputs/data/july_data_dump.csv", index=True)
df_ukj2.to_csv(f"{project_directory}/outputs/data/ukj2_july.csv", index=False)
df_uk_sample.to_csv(f"{project_directory}/outputs/data/uk_sample_july.csv", index=False)
