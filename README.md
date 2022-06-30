<!-- #region -->

# OJO Local Indicators - Sussex

**_Public repository for hosting the outputs of the OJO local indicators project working with the Sussex Chamber of Commerce._**

## Welcome!

This repository contains the code for a short project using the Open Jobs Observatory to better understand skills demand in Sussex for the Sussex Chamber of Commerce.

In this project we produced a series of visualisations based on indicators that describe:

- Growth in vacancies across the UK
- Skills demand in Sussex compared to the Rest of the UK
- The occupations and indistries most advertised in Sussex compared to the rest of the UK
- A deep dives for skill groups that correspond to the Chamber’s key sectors
- What percent of a UK sample of jobs are green (includes non-green jobs in green industries and green jobs in non-green industries)
- A deep dive into transversal skills across the UK and in Sussex

The insights from this project can be found on the [Local Skills Improvement Plan](https://www.sussexchamberofcommerce.co.uk/Education%20Skills) on the Sussex Chamber of Commerce website.

## Contents

The code to produce the visualisations can be found in sub-folders in the [analysis folder](https://github.com/nestauk/ojo_local_indicators/tree/uk_wide/ojo_local_indicators/analysis).

- [**Sussex spotlight**](https://github.com/nestauk/ojo_local_indicators/tree/uk_wide/ojo_local_indicators/analysis): Looking at skills demand in Sussex (based on a sample of job ads.
- [**UK wide**](https://github.com/nestauk/ojo_local_indicators/tree/uk_wide/ojo_local_indicators/analysis): Looking at growth in job ads, industries and skill across the UK.
- [**Deep dives**](https://github.com/nestauk/ojo_local_indicators/tree/uk_wide/ojo_local_indicators/analysis): Focusing on digital, healthcare and engineering skill groups.
- [**Green jobs**](https://github.com/nestauk/ojo_local_indicators/tree/uk_wide/ojo_local_indicators/analysis): Visualisations produced to show percent of green jobs per industry and occupations.
- [**Transversal skills**](https://github.com/nestauk/ojo_local_indicators/tree/uk_wide/ojo_local_indicators/analysis): Visuals for the deep-dive into transversal skills.

## Installation (internal)

To access the ojd_daps codebase and job ads data from the database, you will need to clone the ojd_daps repo by following instructions [here](https://github.com/nestauk/ojd_daps#for-contributors). Make sure you have run export PYTHONPATH=\$PWD at the repository's root to access the codebase. You will need to either be on Nesta HQ's wifi or have your VPN turned on to access data from the database.

### Clone and set up the repo

```shell
$ git clone https://github.com/nestauk/ojo_local_indicators
$ cd cci_ojo_local_indicators
```

- Meet the data science cookiecutter [requirements](http://nestauk.github.io/ds-cookiecutter/quickstart), in brief:
  - Install: `git-crypt` and `conda`
  - Have a Nesta AWS account configured with `awscli`
- Run `make install` to configure the development environment:
  - Setup the conda environment
  - Configure pre-commit
  - Configure metaflow to use AWS

<!-- #endregion -->
