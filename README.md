# FRRP Coral Bleaching Pilot v0.1

This directory contains a small, reproducible extraction for an initial baseline experiment.

## Files

- `extract_frrp_baseline_v0_1.sql`: read-only SQLite extraction used to create the pilot.
- `frrp_baseline_pilot_v0_1.csv`: 2,394 rows and 17 columns.
- `baseline.py`: a dependency-light median baseline with a temporal 2016 test holdout.

## Source and extraction

The source database is `Global_Coral_Bleaching_Database_SQLite_11_24_21.db` in the user's Downloads directory. The source was only read; it was not modified.

The extraction:

- selects `Data_Source_LUT.Data_Source = 'FRRP'` (database ID 2);
- restricts observations to `2005 <= Date_Year <= 2016`;
- requires a non-null `Percent_Bleached` target;
- joins sample, site, environmental, and bleaching tables by `Sample_ID`/`Site_ID`;
- produces one row per sample. The extraction currently yields 2,394 unique samples.

The SQLite database joins are one-to-one for this selected pilot: 2,394 bleach rows, 2,394 unique bleach IDs, 2,394 unique sample IDs, and 2,394 joined rows.

## Data-quality observations

- No `Sample_ID` is duplicated in the CSV.
- 2,299 unique FRRP sites appear among 2,394 observations, so site repeated-measures are present.
- The target ranges from 0 to 100, with mean 15.3055 and median 10.26.
- 201 observations have target value 0; 2 have target value 100.
- `Reef_ID` is empty for all 2,394 rows and was therefore not useful for this pilot.
- Depth ranges from 1.2 to 29.9 m.
- Latitude ranges from 24.4348 to 27.1784; longitude ranges from -83.0360 to -80.0136.
- No missing values occur in the retained numeric columns.

Missing values were not replaced with zero.

## Variables and leakage precautions

`ClimSST` and temperature fields are stored in Kelvin according to the database schema. `Degree Heating Weeks`-named fields and `TSA` should have their units and temporal windows confirmed against original database documentation before interpretation.

The extraction intentionally excludes outcome-derived bleaching fields and severity/prevalence fields. For a baseline, identifiers (`Sample_ID`, `Site_ID`, `Reef_ID`) and the target itself should not be used as predictors.

## Honest baseline scope

`baseline.py` predicts the 2016 observations using the target median learned from 2005-2015 observations. It does not add environmental predictors or claim that observed bleaching can be forecast into the future. This is a reproducibility and difficulty benchmark, not a calibrated conservation alert system.
