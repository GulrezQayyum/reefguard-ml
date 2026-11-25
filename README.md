# FRRP Coral Bleaching Pilot

This project builds a small, reproducible FRRP coral-bleaching dataset and
documents a first, transparent baseline analysis. The work focuses on
understanding the data, checking its quality, preparing model-ready files, and
evaluating a simple time-based baseline without overstating what the data can
support.

## ReefGuard-ML application

The Streamlit application provides a public project homepage and a separate
scientific dashboard. To install its dependencies and run it from the project
root:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

The hero uses a remote reef photograph with a color fallback. To use a local
image instead, provide `reefguard/assets/coral-reef-hero.jpg`; image loading
failures do not prevent the application from starting.

The assessment loads the existing `models/random_forest_v1.joblib` artifact.
That saved pipeline uses 300 trees and a minimum leaf size of 2; it is not the
RF-2 configuration (200 trees, minimum leaf size 5) in the temporal-validation
report. No RF-2 fitted pipeline is present, and the application does not retrain
or alter saved models, datasets, predictions, or evaluation results.

## What we did

- Extracted FRRP observations from the Global Coral Bleaching Database for
  2005–2016.
- Joined sample, site, environmental, and bleaching records while preserving
  one row per `Sample_ID`.
- Explored the resulting data with checks for duplicates, missing values,
  distributions, geographic coverage, repeated sites, and descriptive
  relationships.
- Defined eight environmental predictors and kept identifiers, dates, and
  outcome-derived fields out of the model inputs to reduce leakage risk.
- Prepared a model-ready dataset with a temporal split: 2005–2015 for training
  and 2016 for testing.
- Investigated the repeated `ClimSST = 262.15` value without deleting or
  altering those observations.
- Evaluated a dependency-light median baseline on the 2016 holdout.

## Repository contents

- [`data/extract_frrp_baseline_v0_1.sql`](data/extract_frrp_baseline_v0_1.sql):
  read-only SQLite query used for the FRRP extraction.
- [`data/frrp_baseline_pilot_v0_1.csv`](data/frrp_baseline_pilot_v0_1.csv):
  the extracted pilot dataset with 2,394 rows and 17 columns.
- [`notebooks/01_data_exploration.ipynb`](notebooks/01_data_exploration.ipynb):
  read-only exploratory analysis and data-quality checks.
- [`src/prepare_dataset.py`](src/prepare_dataset.py):
  validates the pilot, selects predictors, checks target bounds, creates the
  temporal split, and writes model-ready files and a preparation report.
- [`baseline.py`](baseline.py): computes the training median and evaluates it
  on the 2016 holdout.
- `data/modeling/`: generated model-ready datasets, split metadata, and the
  preparation report.

## Dataset and extraction

The source database was
`Global_Coral_Bleaching_Database_SQLite_11_24_21.db` in the user's Downloads
directory. It was read only and was not modified.

The extraction:

- selects the FRRP data source (`Data_Source = 2`);
- restricts observations to `2005 <= Date_Year <= 2016`;
- requires a non-null `Percent_Bleached` target;
- joins `Sample_Event_tbl`, `Site_Info_tbl`, `Environmental_tbl`, and
  `Bleaching_tbl` by `Sample_ID` and `Site_ID`;
- orders the result chronologically and produces one row per sample.

The extracted pilot contains 2,394 unique samples from 2,299 sites. No exact
duplicate rows or duplicate `Sample_ID` values were found. `Reef_ID` is empty
for all rows, so it was not useful for this first pass.

## Data-quality findings

- `Percent_Bleached` ranges from 0 to 100; its overall mean is 15.3055 and
  median is 10.26.
- There are 201 observations with a target of 0 and 2 with a target of 100.
- Depth ranges from 1.2 to 29.9 m.
- Latitude ranges from 24.4348 to 27.1784; longitude ranges from -83.0360 to
  -80.0136.
- No missing values occur in the retained numeric columns.
- Missing values were not replaced with zero.
- `ClimSST = 262.15` occurs in 187 observations. The original values were
  preserved, and the repeated value remains an unresolved data-quality issue.

The notebook provides the detailed distributions, year counts, missing-value
checks, summary tables, and descriptive analyses.

## Features and leakage precautions

The selected environmental features are:

- `Depth_m`
- `ClimSST`
- `Temperature_Mean`
- `SSTA`
- `SSTA_DHW`
- `TSA`
- `TSA_DHW`
- `Windspeed`

`Sample_ID`, `Site_ID`, and `Reef_ID` are identifiers rather than predictors.
`Date_Year` is used only to create the temporal split. Latitude and longitude
are retained in the pilot CSV but are not part of the initial feature set.
Outcome-derived fields, severity/prevalence fields, and the target itself are
excluded to avoid target leakage.

The database schema stores `ClimSST` and temperature fields in Kelvin.
Degree Heating Weeks fields and `TSA` still require confirmation of their
units and temporal windows before scientific interpretation.

## Dataset preparation

Running [`src/prepare_dataset.py`](src/prepare_dataset.py) validates the
target and required columns, rejects invalid target values, preserves the
original pilot CSV, and writes:

- `data/modeling/modeling_dataset_v1.csv`: all 2,394 eligible rows with the
  eight features and target.
- `data/modeling/train_v1.csv`: 2,201 observations from 2005–2015.
- `data/modeling/test_v1.csv`: 193 observations from 2016.
- `data/modeling/split_metadata_v1.csv`: sample, site, year, and split
  assignments.
- `data/modeling/dataset_preparation_report.md`: detailed preparation report.

No observations were excluded for a missing target or predictor in this
version. The temporal split has no `Sample_ID` overlap, but 22 sites occur in
both periods, so repeated-site effects remain a limitation.

## Baseline result

Running [`baseline.py`](baseline.py) learns the median target from 2005–2015
and predicts that constant value for every 2016 observation:

- Training target median: `10.2600`
- 2016 MAE: `7.3684`
- 2016 RMSE: `10.0726`
- Mean error (`actual - predicted`): `1.3439`

This is an explainable reproducibility benchmark. It does not use the
environmental predictors and does not establish future forecasting ability,
causality, or a calibrated conservation alert system.

## Reproducing the preparation and baseline

From the project root:

```bash
.venv/bin/python src/prepare_dataset.py
.venv/bin/python baseline.py
```
