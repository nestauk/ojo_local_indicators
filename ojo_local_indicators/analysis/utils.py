# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     comment_magics: true
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ### Function to clean job titles (lightly)

# %%
def clean_titles(raw_job_title, EXCLUDED_TERMS):

    # Make lower case
    job_title = raw_job_title.lower()

    # Remove punctuation, except /-'
    job_title = job_title.translate(
        str.maketrans("", "", '!"#$%&\()*+,.:;<=>?@[\\]^_`{|}~')
    )

    # Change '/' to a space and '-' to space
    job_title = job_title.replace("/", " ").replace("-", " ")

    # Drop EXCLUDED terms
    job_title = " ".join(
        [word for word in job_title.split() if word not in EXCLUDED_TERMS]
    )

    return job_title


# %% [markdown]
# ### Function to extract and annualise salaries

# %%
def annualises_salary(one_job):

    # Extract salary information
    salary_currency = one_job["raw_salary_currency"]
    salary_unit = one_job["raw_salary_unit"]

    # Ignore foreign currencies
    if salary_currency != "GBP":
        min_salary = None
        max_salary = None

    # If GBP
    else:

        # If only one salary is given, treat it as the
        # minimum and the maximum
        if one_job["raw_salary"] is not None:
            raw_min_salary = one_job["raw_salary"]
            raw_max_salary = one_job["raw_salary"]
        else:
            raw_min_salary = one_job["raw_min_salary"]
            raw_max_salary = one_job["raw_max_salary"]

        # If no salary is given
        if raw_min_salary is None:
            min_salary = None
            max_salary = None

        # Otherwise
        else:

            # Convert daily and hourly salaries to annual salaries
            if salary_unit == "YEAR":
                min_salary = raw_min_salary
                max_salary = raw_max_salary
            elif salary_unit == "DAY":
                min_salary = raw_min_salary * 5 * 52
                max_salary = raw_max_salary * 5 * 52
            elif salary_unit == "HOUR":
                min_salary = raw_min_salary * 37.5 * 52
                max_salary = raw_max_salary * 37.5 * 52

    return [min_salary, max_salary]
