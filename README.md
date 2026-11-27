# ReefGuard-ML

ReefGuard-ML is a biodiversity-focused machine-learning prototype exploring
whether environmental observations are associated with measured coral
bleaching. Coral bleaching is an important conservation concern because it is
a visible response to coral stress and can affect reef ecosystems; this
project investigates a small historical dataset rather than monitoring reefs.
It is a research and learning tool, not a validated forecast, early-warning
system, or operational conservation service.

## What the project does

The project packages an FRRP historical pilot dataset, a reproducible
preparation and modeling workflow, saved evaluation outputs, and a Streamlit
application for exploring observations and an experimental saved-model
assessment.

The current experiments compare:

- A constant median baseline calculated from the training targets.
- Linear Regression with median imputation.
- Random Forest v1 with median imputation, 300 trees, `random_state=42`, and
  `min_samples_leaf=2`.
- Four Random Forest configurations in a separate expanding-window validation.
  RF-2 (200 trees, unlimited depth, `min_samples_leaf=5`) is a validation
  configuration only; it is not the saved v1 pipeline used by the app.

On the existing 2016 test set (193 observations), the median baseline had the
lowest MAE and RMSE. The saved results are:

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Median baseline | 7.3684 | 10.0726 | -0.0181 |
| Linear Regression | 9.0416 | 11.4359 | -0.3124 |
| Random Forest v1 | 9.7521 | 13.1911 | -0.7461 |

These are results recorded in the repository’s saved artifacts. They have not
been regenerated as part of this documentation update. The 2016 results have
already been examined and must not be presented as an untouched final holdout.
The baseline matters: on this split, the more complex models did not improve
on the simple reference.

In the separate 2005–2015 expanding-window validation, the median baseline's
mean fold MAE was 13.9795. RF-2's mean fold MAE was 12.6002, but it beat the
baseline in only one of three folds. This inconsistent result is not evidence
of reliable generalization and is not the performance of the saved v1 model.
See the saved comparison and validation details in
[`reports/model_training_report_v1.md`](reports/model_training_report_v1.md)
and [`reports/time_aware_validation_v1.md`](reports/time_aware_validation_v1.md).

## Dataset, provenance, and licensing

The included
[`data/frrp_baseline_pilot_v0_1.csv`](data/frrp_baseline_pilot_v0_1.csv)
contains 2,394 sample observations and 17 columns, covering 2005–2016. The
project identifies the subset as Florida Reef Resilience Program (FRRP) data
from the Global Coral Bleaching Database. The extraction query is
[`data/extract_frrp_baseline_v0_1.sql`](data/extract_frrp_baseline_v0_1.sql).
It joins sample-event, site, environmental, and bleaching records; selects
`Data_Source = 2`, dates from 2005 through 2016, and non-missing bleaching
targets. The query comments identify the source SQLite file as
`Global_Coral_Bleaching_Database_SQLite_11_24_21.db`. That database is not
included, so the extraction cannot be independently rerun from this
repository alone.

The target is `Percent_Bleached`, an observed bleaching percentage on a
0–100 scale. The included CSV has no missing target values. `Reef_ID` is blank
for every observation. No selected predictor or target values are missing in
this pilot extract; if missing predictor values are encountered by dataset
preparation or training, the pipeline uses medians fitted on the applicable
training data only. It does not impute missing targets.

| Feature | Meaning/unit documented in this project |
|---|---|
| `Depth_m` | Depth in metres. |
| `ClimSST` | Label retained from source; project documentation identifies Kelvin. The repeated value 262.15 in 187 observations is unresolved. |
| `Temperature_Mean` | Label retained from source; project documentation identifies Kelvin. |
| `SSTA`, `SSTA_DHW`, `TSA`, `TSA_DHW`, `Windspeed` | Source field names retained. Units, definitions, and/or temporal windows are not confirmed in available project documentation. |

The source database itself, a full data dictionary, source citation details
beyond those recorded above, and licensing/redistribution terms are not
provided here. Public availability of an upstream dataset does not by itself
establish permission to redistribute this extract. Confirm and document the
applicable attribution and license before publishing or redistributing the
data; do not infer a license from the project’s inclusion of the CSV.

## Data preparation and evaluation design

[`src/prepare_dataset.py`](src/prepare_dataset.py) validates required columns
and numeric values, excludes identifiers and date/geographic fields from
model inputs, and uses `Date_Year` only to make a chronological split:

- Training: 2005–2015, 2,201 observations.
- Test: 2016, 193 observations.

The periods share 22 `Site_ID`s. This is a temporal split, not a site-held-out
or region-held-out evaluation; it does not demonstrate spatial
generalization. The target median is 10.26% in both the training and test
data. `ClimSST = 262.15` remains in the feature set without an assumed
interpretation. The 2016 set has previously been examined and must not be
treated as an untouched final holdout or used repeatedly for model selection.

The validation script evaluates Random Forest configurations on three
expanding-window folds within 2005–2015. Each fold holds out later full years
and fits preprocessing on that fold's training period. The fold results are
historical validation artifacts; the 2016 set is not part of those folds.
Details and limitations are in
[`data/modeling/dataset_preparation_report.md`](data/modeling/dataset_preparation_report.md)
and [`reports/time_aware_validation_v1.md`](reports/time_aware_validation_v1.md).

## Architecture

```text
data/frrp_baseline_pilot_v0_1.csv
  ├─ src/prepare_dataset.py ─> data/modeling/{train_v1,test_v1,split_metadata_v1,modeling_dataset_v1}.csv
  ├─ baseline.py ────────────> prints the 2016 training-median baseline metrics
  ├─ src/train_models.py ────> saved predictions, comparison, feature importance, model pipelines, report
  └─ src/validate_models.py ─> expanding-window validation CSV and report

saved data, models, and reports
  ├─ src/visualize_evaluation.py ─> reports/figures/*.png
  └─ app.py ─> reefguard/ ─> Streamlit overview, data explorer, assessment,
                            insights, evaluation, and methodology pages
```

The app loads the included historical data and saved artifacts; it does not
train models. The assessment page loads `models/random_forest_v1.joblib`, not
RF-2. Input range validation restricts requests to the observed pilot ranges;
it is not an uncertainty estimate or a test for realistic combinations of
measurements.

## Reproducibility

Python 3.12 is the documented tested runtime. From the repository root, create
an environment and install the declared dependencies:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The source SQLite database is not required for the commands below because
the pilot CSV is included. Run the workflow in order:

```bash
# Prepare model-ready files from the included pilot CSV.
.venv/bin/python src/prepare_dataset.py

# Train the initial median-baseline, Linear Regression, and Random Forest v1
# comparison on the saved 2005–2015 / 2016 split.
.venv/bin/python src/train_models.py

# Evaluate four Random Forest configurations on expanding-window folds
# within the training period. This does not read the 2016 test CSV.
.venv/bin/python src/validate_models.py

# Generate figures from the saved evaluation CSVs and predictions.
.venv/bin/python src/visualize_evaluation.py

# Optional standalone baseline calculation from the original pilot CSV.
.venv/bin/python baseline.py

# Run the Streamlit application.
.venv/bin/python -m streamlit run app.py

# In a separate terminal, run the application logic tests.
.venv/bin/python -m unittest discover -s tests -v
```

### Workflow inputs and outputs

| Step | Required inputs | Generated or updated artifacts |
|---|---|---|
| Preparation | `data/frrp_baseline_pilot_v0_1.csv` | `data/modeling/modeling_dataset_v1.csv`, `train_v1.csv`, `test_v1.csv`, `split_metadata_v1.csv`, and `dataset_preparation_report.md` |
| Initial training | `train_v1.csv`, `test_v1.csv`, `split_metadata_v1.csv` | `model_predictions_v1.csv`, `reports/model_comparison_v1.csv`, `random_forest_feature_importance_v1.csv`, `models/linear_regression_v1.joblib`, `models/random_forest_v1.joblib`, and `reports/model_training_report_v1.md` |
| Temporal validation | `train_v1.csv`, `split_metadata_v1.csv` | `reports/time_aware_validation_summary_v1.csv` and `reports/time_aware_validation_v1.md` |
| Visualization | Saved predictions, test data, split metadata, comparison, feature importance, and temporal-validation CSV | Five PNGs in `reports/figures/` |
| App/tests | Pilot CSV and saved model/evaluation artifacts | App reads existing files; tests exercise application logic and saved model inference. |

The preparation, training, validation, and visualization scripts write to the
paths above and replace same-named generated artifacts. Preserve a copy of
existing results before running them if you need to retain the current
artifacts. The baseline command only prints metrics. None of the saved
evaluation results were overwritten for this documentation update.

## Limitations and future work

- The data is observational and limited to one FRRP subset and historical
  years; it does not establish causal relationships.
- Sites occur in both temporal periods; no cross-region or site-held-out
  validation is included.
- `ClimSST = 262.15` is unresolved, `Reef_ID` is entirely missing, and several
  environmental units/definitions/windows are undocumented.
- The high-bleaching group in the 2016 test set is small. A single held-out
  year cannot establish stable performance.
- The baseline outperformed both initial ML models on the saved 2016 test
  comparison. RF-2's lower mean validation MAE is inconsistent across folds.
- The app supplies point estimates without uncertainty estimates, image
  quality checks, or expert review. It is not operational guidance.
- Model artifacts are serialized with scikit-learn 1.9.1; see
  [`requirements.txt`](requirements.txt) for the declared compatibility range.

Open research directions include cross-region validation (requiring
independent, comparable regional data), uncertainty and expert-reviewed
assessment, and a more traceable workflow connecting observations, data
versions, predictions, and reproducible assessments.

## Application features

- **Overview** — dataset summary and historical bleaching patterns.
- **Data Explorer** — filter records and inspect descriptive patterns.
- **Bleaching Assessment** — query the saved experimental Random Forest v1
  pipeline within observed feature ranges.
- **Environmental Insights** — explore feature distributions, associations,
  and model-specific importance.
- **Model Evaluation** — distinguish the 2016 comparison from temporal
  validation.
- **Methodology** — review data scope, methods, and limitations.

Associations and model outputs are descriptive/exploratory; they do not
establish causation, future bleaching, or reef-level outcomes.

## Homepage image

The homepage uses a remote reef photograph with a solid-color fallback. No
local hero image is included. Confirm asset licensing and attribution before
adding or redistributing a local image.
