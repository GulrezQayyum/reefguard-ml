# ReefGuard-ML Dataset Preparation Report

## Data source

- Original source: `data/frrp_baseline_pilot_v0_1.csv`
- Original dataset size: 2394 observations, 17 columns
- Final eligible modelling dataset size: 2394 observations
- Original CSV was not modified.

## Target and feature selection

- Target: `Percent_Bleached`, with observed values required to remain between 0 and 100.
- Selected features:

- `Depth_m`
- `ClimSST`
- `Temperature_Mean`
- `SSTA`
- `SSTA_DHW`
- `TSA`
- `TSA_DHW`
- `Windspeed`


Identifiers and dates were kept outside the model inputs. `Date_Year` was used only for temporal splitting and is stored in `split_metadata_v1.csv`.

## Excluded columns and reasons

- `Sample_ID` and `Site_ID`: identifiers, not environmental predictors.
- `Reef_ID`: entirely missing in the pilot and not useful for this prototype.
- `Date_Year`, `Date_Month`, `Date_Day`: dates/temporal metadata; only `Date_Year` is used for the split.
- `Latitude_Degrees` and `Longitude_Degrees`: not selected initial environmental predictors.
- `Percent_Bleached`: target, excluded from feature matrices.
- `Severity_Code`, `bleach_intensity`, `Bleaching_Prevalence_Score`, and other outcome-derived fields: excluded to prevent target leakage.

## Missing-value findings and treatment

- `Depth_m`: 0 missing values.
- `ClimSST`: 0 missing values.
- `Temperature_Mean`: 0 missing values.
- `SSTA`: 0 missing values.
- `SSTA_DHW`: 0 missing values.
- `TSA`: 0 missing values.
- `TSA_DHW`: 0 missing values.
- `Windspeed`: 0 missing values.

No missing-value treatment was required: no selected feature or target value was missing in the pilot CSV.

- No observations were excluded because the target was missing.
- Missing target values were never replaced with zero or any other invented value.


## ClimSST investigation

- `ClimSST = 262.15` occurs in 187 observations in the pilot CSV.
- The original values were preserved exactly.
- These observations were not deleted and the values were not replaced.
- The repeated value is an unresolved data-quality issue and is not assigned a presumed meaning in this preparation process.
- `ClimSST` remains in the primary dataset. A separate sensitivity dataset without this feature can be considered later, if approved.

## Temporal split

- Training: 2005–2015, 2201 observations.
- Testing: 2016, 193 observations.
- Training year range: 2005–2015.
- Testing year range: 2016–2016.
- Sample_ID overlap: 0.
- Site_ID overlap: 22.

The overlapping sites are a limitation: although no sample is reused, repeated observations from 22 sites occur across the train and test periods. The temporal split was not changed.

## Target distributions

- Training: count=2201, min=0, max=100, mean=15.6301, median=10.26.
- Testing: count=193, min=0, max=77.78, mean=11.6039, median=10.26.

## Observations excluded

- 0 observation(s) had a missing `Percent_Bleached` target.
- No feature observations were discarded solely because of predictor missingness; the predictor strategy is training-derived median imputation.
- No exact duplicate rows were found in the original pilot.

## Output files

- `modeling_dataset_v1.csv`: complete eligible model-ready dataset.
- `train_v1.csv`: training features and target for 2005–2015.
- `test_v1.csv`: testing features and target for 2016.
- `split_metadata_v1.csv`: identifier, year, and split assignment audit trail.

## Known limitations

- This is an observational prototype, not an early-warning or future-forecasting system.
- The temporal split has repeated Site_ID values between periods.
- `ClimSST = 262.15` has unresolved meaning.
- Environmental units and temporal windows may require further documentation before scientific interpretation.
- This dataset is intended to support a simple, explainable submission prototype rather than publication-grade inference.
