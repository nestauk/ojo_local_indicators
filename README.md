<!-- #region -->

# Exploring skill demands in Sussex

**_A public repository containing code for the OJO Local Indicators project._**

## Welcome!

This repository contains the code for a short project which aimed to understand <b>the skill needs of employers in Sussex</b>. These skills were identified from job adverts (for positions based in Sussex), which were collected in Nesta’s [Open Jobs Observatory](https://www.nesta.org.uk/data-visualisation-and-interactive/open-jobs-observatory/) (OJO). [The insights from our analysis are available in this slide deck](https://www.sussexchamberofcommerce.co.uk/storage/resources/annex-11-1649415160.pdf). The project was conducted in collaboration with the Sussex Chamber of Commerce and the insights fed into their [Local Skills Improvement Plan](https://www.sussexchamberofcommerce.co.uk/Education%20Skills).

The project examined both the mix of skill needs within Sussex as well as the differences in skill demands between Sussex and other regions. As part of the project we created this [interactive data visualisation](https://observablehq.com/@cath/2202_sussex_jobs_skills) which shows the skills required for frequently advertised jobs within the region. The project also contained a number of deep dives into digital skills, transversal skills and green jobs.  

## Contents
The code to produce the figures within the slide deck can be found within the [analysis folder](https://github.com/nestauk/ojo_local_indicators/tree/dev/ojo_local_indicators/analysis).

- [**Sussex spotlight**](https://github.com/nestauk/ojo_local_indicators/tree/dev/ojo_local_indicators/analysis): Examines the skills in demand across Sussex.
- [**UK wide**](https://github.com/nestauk/ojo_local_indicators/tree/dev/ojo_local_indicators/analysis): Analyses the changes in job adverts overtime and by region, industry, occupation and broad skill group.
- [**Deep dives**](https://github.com/nestauk/ojo_local_indicators/tree/dev/ojo_local_indicators/analysis): Visuals for the deep dives relating to healthcare and engineering skills.
- [**Green jobs**](https://github.com/nestauk/ojo_local_indicators/tree/dev/ojo_local_indicators/analysis): Examines the mix of job adverts for positions in green industries. The methodology for identifying ‘green jobs’ is [available here](https://www.nesta.org.uk/project-updates/finding-jobs-green-industries-methodology/).
- [**Transversal skills**](https://github.com/nestauk/ojo_local_indicators/tree/dev/ojo_local_indicators/analysis): Visuals for the deep-dive into transversal skills.
- [**Digital skills**](https://github.com/nestauk/ojo_local_indicators/tree/dev/ojo_local_indicators/analysis/digital_skills): Visuals for the deep-dive into digital skills.
- [**Occupations**](): Creates the dataset that drives the [interactive visualisation](https://observablehq.com/@cath/2202_sussex_jobs_skills).

## Installation (internal)

To access the ojd_daps codebase and job ads data from the database, you will need to clone the ojd_daps repo by following instructions [here](https://github.com/nestauk/ojd_daps#for-contributors). Make sure you have run `export PYTHONPATH=\$PWD` at the repository's root to access the codebase. You will need to either be on Nesta HQ's wifi or have your VPN turned on to access data from the database.

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
