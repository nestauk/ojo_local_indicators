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
#     display_name: grjobs
#     language: python
#     name: grjobs
# ---

# %%
import nltk

nltk.download("wordnet")
from grjobs.pipeline.green_classifier import load_model
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %%
model = load_model("best_model")


# %%
def open_raw_jobs(file):
    with open(file) as json_file:
        data = json.load(json_file)
    return data


# %%
def save_raw_jobs(job_ad, file_path):
    with open(file_path, "w") as file:
        json.dump(job_ad, file)


# %%
def label_green(raw_ads):
    green_pred = model.predict(raw_ads)
    green_jobs = list(green_pred)
    green_adverts = [
        dict(advert, **{"gr_job": green}) for advert, green in zip(raw_ads, green_jobs)
    ]
    return green_adverts


# %%
uk_jds = open_raw_jobs(
    "../../../outputs/data/job_descriptions/uk_sample_07-06-2021_22-11-2021.json"
)

# %%
gr_uk_jds = label_green(uk_jds)

# %%
gr_uk_jds[0]

# %%
save_raw_jobs(gr_uk_jds, "../../../outputs/data/green_jobs_uk_sample.json")
