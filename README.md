# ReefGuard-ML

ReefGuard-ML is a coral-bleaching research prototype built around a small
Florida Reef Resilience Program (FRRP) pilot dataset. It combines a
conservation-focused public homepage with a separate scientific dashboard for
exploring historical observations, inspecting model results, and trying an
experimental assessment.

This is a research and learning tool, not a monitoring service, forecast,
early-warning system, or conservation alert platform.

## Run the application

Python 3.12 is the tested runtime. From the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Streamlit prints a local URL (usually `http://localhost:8501`). The app runs
on CPU; no GPU is required.

To run the application tests:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## What the application includes

The homepage introduces the project and links to the scientific dashboard.
Dashboard navigation includes:

- **Overview** — pilot dataset summary and historical bleaching patterns.
- **Data Explorer** — filter historical records by year and bleaching
  percentage, then explore the selected data with interactive charts.
- **Bleaching Assessment** — submit environmental values to the existing saved
  Random Forest pipeline.
- **Environmental Insights** — inspect environmental distributions,
  associations with bleaching, and reported feature importance.
- **Model Evaluation** — review the original test-set results and temporal
  validation results as separate evaluations.
- **Methodology** — read about the data, feature selection, temporal split,
  metrics, and limitations.

Historical measurements and model outputs are presented separately.
Associations in these data are descriptive and do not establish causation.

## Data and study scope

The included pilot, [`data/frrp_baseline_pilot_v0_1.csv`](data/frrp_baseline_pilot_v0_1.csv),
contains 2,394 observations from 2005–2016. The target is `Percent_Bleached`.
The extraction query is available at
[`data/extract_frrp_baseline_v0_1.sql`](data/extract_frrp_baseline_v0_1.sql).
The source SQLite database is not included in this repository.

The model-ready feature set, in the order expected by the saved pipeline, is:

1. `Depth_m`
2. `ClimSST`
3. `Temperature_Mean`
4. `SSTA`
5. `SSTA_DHW`
6. `TSA`
7. `TSA_DHW`
8. `Windspeed`

The initial temporal split uses 2005–2015 for training and 2016 for testing
(2,201 and 193 observations, respectively). In the pilot, the target median
is 10.26%. The repeated `ClimSST = 262.15` value appears in 187 observations
and remains an unresolved data-quality issue. `Reef_ID` is empty throughout
the pilot. These limitations should be considered when interpreting any
result.

Depth is documented in metres; `ClimSST` and `Temperature_Mean` are documented
in Kelvin. Units or temporal windows for the other environmental fields have
not been confirmed in the available project documentation.

## Model and interpretation

The assessment loads [`models/random_forest_v1.joblib`](models/random_forest_v1.joblib);
it does not train a model. This saved pipeline uses 300 trees and a minimum
leaf size of 2. It is **not** the RF-2 configuration (200 trees, minimum leaf
size 5) referenced in the temporal-validation report; no fitted RF-2 pipeline
is included.

The saved Random Forest performed worse than the historical-median baseline
on the 2016 test set (MAE 9.75 versus 7.37 percentage points). The RF-2
temporal validation also showed inconsistent performance across folds. The
dashboard reports these results separately and does not present them as proof
of a superior model or future forecasting ability.

Assessment inputs are checked against the observed pilot-data ranges and
must be numeric and finite. Out-of-range values are rejected, and predictions
are shown without clipping. A prediction is an experimental model output, not
a forecast or alert.

The serialized pipeline was created with scikit-learn 1.9.1, so the dependency
requirement in [`requirements.txt`](requirements.txt) sets that version as its
minimum.

## Reproduce the prepared dataset and baseline

The preparation script validates the pilot data and writes the model-ready
datasets, temporal split metadata, and preparation report:

```bash
.venv/bin/python src/prepare_dataset.py
```

The baseline script reads the pilot CSV and prints metrics for a constant
prediction based on the training-set median:

```bash
.venv/bin/python baseline.py
```

Only the preparation command writes derived files. The baseline command only
prints its results. The Streamlit application reads the saved datasets, model,
predictions, and evaluation artifacts; it does not retrain models or rewrite
them.

## Repository map

```text
app.py                         Streamlit entry point and page routing
reefguard/                     Data, model, styling, charts, and page modules
data/                          FRRP pilot and prepared modelling datasets
models/                        Saved model pipelines
reports/                       Evaluation reports, tables, and figures
src/prepare_dataset.py         Dataset validation and temporal split
baseline.py                    Historical-median baseline evaluation
notebooks/                      Exploratory data analysis
tests/                          Focused application logic tests
```

## Image asset

The homepage uses a remote reef photograph with a solid-color fallback, so an
image-loading failure does not prevent the app from running. To use a local
image, add `reefguard/assets/coral-reef-hero.jpg`; no local hero image is
currently included.
