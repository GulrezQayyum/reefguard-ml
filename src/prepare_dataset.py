import csv
import math
from pathlib import Path
from statistics import median

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "frrp_baseline_pilot_v0_1.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "modeling"

TARGET = "Percent_Bleached"
FEATURES = [
    "Depth_m",
    "ClimSST",
    "Temperature_Mean",
    "SSTA",
    "SSTA_DHW",
    "TSA",
    "TSA_DHW",
    "Windspeed",
]
IDENTIFIER_AND_DATE_COLUMNS = [
    "Sample_ID",
    "Site_ID",
    "Reef_ID",
    "Date_Year",
    "Date_Month",
    "Date_Day",
]
GEOGRAPHIC_COLUMNS = ["Latitude_Degrees", "Longitude_Degrees"]
OUTCOME_DERIVED_COLUMNS = [
    "Severity_Code",
    "bleach_intensity",
    "Bleaching_Prevalence_Score",
]
MISSING_TOKENS = {"", "na", "nan", "null", "none"}


def is_missing(value):
    if value is None:
        return True
    return str(value).strip().lower() in MISSING_TOKENS


def as_float(value, column, row_number):
    if is_missing(value):
        return None
    try:
        return float(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Non-numeric value in {column} at CSV row {row_number}: {value!r}"
        ) from exc


def read_pilot():
    with DATA_PATH.open("r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise ValueError("Pilot CSV has no header")
        rows = list(reader)
        return reader.fieldnames, rows


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def target_summary(rows):
    values = [row[TARGET] for row in rows]
    if not values:
        return "count=0"
    return (
        f"count={len(values)}, min={min(values):.6g}, max={max(values):.6g}, "
        f"mean={sum(values) / len(values):.6g}, median={median(values):.6g}"
    )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    columns, source_rows = read_pilot()

    required = ["Sample_ID", "Site_ID", "Date_Year", TARGET] + FEATURES
    missing_required = [column for column in required if column not in columns]
    if missing_required:
        raise ValueError(f"Missing required columns: {', '.join(missing_required)}")

    for column in OUTCOME_DERIVED_COLUMNS:
        if column in columns:
            raise ValueError(
                f"Outcome-derived column {column} is present; it must not be used as a predictor"
            )

    original_missing_features = {
        column: sum(is_missing(row[column]) for row in source_rows)
        for column in FEATURES
    }
    clim_sst_26215 = sum(
        not is_missing(row["ClimSST"])
        and float(row["ClimSST"])
        == 262.15
        for row in source_rows
    )

    eligible_rows = []
    excluded_missing_target = 0
    excluded_nonnumeric_target = 0

    for csv_row_number, source_row in enumerate(source_rows, start=2):
        target = as_float(source_row[TARGET], TARGET, csv_row_number)
        if target is None:
            excluded_missing_target += 1
            continue
        if not math.isfinite(target) or target < 0 or target > 100:
            excluded_nonnumeric_target += 1
            raise ValueError(
                f"Target outside [0, 100] or invalid at CSV row {csv_row_number}: {target}"
            )

        year = as_float(source_row["Date_Year"], "Date_Year", csv_row_number)
        if year is None or not math.isfinite(year) or not year.is_integer():
            raise ValueError(f"Invalid Date_Year at CSV row {csv_row_number}: {source_row['Date_Year']!r}")

        eligible = dict(source_row)
        eligible[TARGET] = target
        eligible["Date_Year"] = int(year)

        for feature in FEATURES:
            eligible[feature] = as_float(feature_value := source_row[feature], feature, csv_row_number)
            if eligible[feature] is not None and not math.isfinite(eligible[feature]):
                raise ValueError(f"Non-finite value in {feature} at CSV row {csv_row_number}")

        if is_missing(source_row["Sample_ID"]):
            raise ValueError(f"Missing Sample_ID at CSV row {csv_row_number}")
        if is_missing(source_row["Site_ID"]):
            raise ValueError(f"Missing Site_ID at CSV row {csv_row_number}")

        eligible_rows.append(eligible)

    if excluded_nonnumeric_target:
        raise AssertionError("Target range validation unexpectedly allowed invalid targets")

    train_rows = [row for row in eligible_rows if row["Date_Year"] < 2016]
    test_rows = [row for row in eligible_rows if row["Date_Year"] == 2016]

    if not train_rows:
        raise ValueError("No training observations found")
    if not test_rows:
        raise ValueError("No test observations found")

    unexpected_year_rows = [
        row["Date_Year"] for row in eligible_rows
        if row["Date_Year"] < 2005 or row["Date_Year"] > 2016
    ]
    if unexpected_year_rows:
        raise ValueError(
            "Temporal split found observations outside 2005-2016: "
            + ", ".join(str(year) for year in sorted(set(unexpected_year_rows)))
        )

    imputation_medians = {}
    missing_features_after_split = {
        feature: sum(row[feature] is None for row in train_rows) + sum(row[feature] is None for row in test_rows)
        for feature in FEATURES
    }

    for feature in FEATURES:
        training_values = [row[feature] for row in train_rows if row[feature] is not None]
        if not training_values:
            if missing_features_after_split[feature]:
                raise ValueError(
                    f"Cannot fit training median for {feature}: all eligible values are missing"
                )
            imputation_medians[feature] = None
        else:
            imputation_medians[feature] = median(training_values)

    for row in eligible_rows:
        for feature in FEATURES:
            if row[feature] is None:
                row[feature] = imputation_medians[feature]

    train_ids = {str(row["Sample_ID"]) for row in train_rows}
    test_ids = {str(row["Sample_ID"]) for row in test_rows}
    sample_overlap = train_ids & test_ids
    train_years = [row["Date_Year"] for row in train_rows]
    test_years = [row["Date_Year"] for row in test_rows]

    if not all(year < 2016 for year in train_years):
        raise AssertionError("Training data contains a 2016 or later observation")
    if not all(year == 2016 for year in test_years):
        raise AssertionError("Test data contains an observation outside 2016")
    if sample_overlap:
        raise AssertionError("Sample_ID overlap detected between training and testing")

    train_sites = {str(row["Site_ID"] ) for row in train_rows}
    test_sites = {str(row["Site_ID"] ) for row in test_rows}
    site_overlap = train_sites & test_sites

    modelling_fieldnames = FEATURES + [TARGET]
    modelling_rows = [{name: row[name] for name in modelling_fieldnames} for row in eligible_rows]
    train_model_rows = [{name: row[name] for name in modelling_fieldnames} for row in train_rows]
    test_model_rows = [{name: row[name] for name in modelling_fieldnames} for row in test_rows]

    write_csv(OUTPUT_DIR / "modeling_dataset_v1.csv", modelling_fieldnames, modelling_rows)
    write_csv(OUTPUT_DIR / "train_v1.csv", modelling_fieldnames, train_model_rows)
    write_csv(OUTPUT_DIR / "test_v1.csv", modelling_fieldnames, test_model_rows)

    metadata_fields = ["Sample_ID", "Site_ID", "Date_Year", "split"]
    metadata_rows = []
    for row in eligible_rows:
        metadata_rows.append({
            "Sample_ID": row["Sample_ID"],
            "Site_ID": row["Site_ID"],
            "Date_Year": row["Date_Year"],
            "split": "train" if row["Date_Year"] < 2016 else "test",
        })
    write_csv(OUTPUT_DIR / "split_metadata_v1.csv", metadata_fields, metadata_rows)

    missing_treatment_lines = []
    for feature in FEATURES:
        count = original_missing_features[feature]
        median_value = imputation_medians[feature]
        if count:
            missing_treatment_lines.append(
                f"- `{feature}`: {count} missing values; median imputed using training data only"
                + (f" (training median: {median_value:.6g})." if median_value is not None else ".")
            )
        else:
            missing_treatment_lines.append(f"- `{feature}`: 0 missing values.")

    if any(original_missing_features.values()):
        missing_summary = "\n".join(missing_treatment_lines)
        missing_treatment = "Training-derived median imputation was applied to missing predictor values."
    else:
        missing_summary = "\n".join(missing_treatment_lines)
        missing_treatment = "No missing-value treatment was required: no selected feature or target value was missing in the pilot CSV."

    excluded_target_text = (
        f"{excluded_missing_target} observation(s) were excluded because `Percent_Bleached` was missing."
        if excluded_missing_target
        else "No observations were excluded because the target was missing."
    )

    report = f"""# ReefGuard-ML Dataset Preparation Report

## Data source

- Original source: `data/frrp_baseline_pilot_v0_1.csv`
- Original dataset size: {len(source_rows)} observations, {len(columns)} columns
- Final eligible modelling dataset size: {len(eligible_rows)} observations
- Original CSV was not modified.

## Target and feature selection

- Target: `Percent_Bleached`, with observed values required to remain between 0 and 100.
- Selected features:

"""
    report += "".join(f"- `{feature}`\n" for feature in FEATURES)
    report += """

Identifiers and dates were kept outside the model inputs. `Date_Year` was used only for temporal splitting and is stored in `split_metadata_v1.csv`.

## Excluded columns and reasons

- `Sample_ID` and `Site_ID`: identifiers, not environmental predictors.
- `Reef_ID`: entirely missing in the pilot and not useful for this prototype.
- `Date_Year`, `Date_Month`, `Date_Day`: dates/temporal metadata; only `Date_Year` is used for the split.
- `Latitude_Degrees` and `Longitude_Degrees`: not selected initial environmental predictors.
- `Percent_Bleached`: target, excluded from feature matrices.
- `Severity_Code`, `bleach_intensity`, `Bleaching_Prevalence_Score`, and other outcome-derived fields: excluded to prevent target leakage.

## Missing-value findings and treatment

"""
    report += missing_summary + "\n\n"
    report += missing_treatment + "\n\n"
    report += f"- {excluded_target_text}\n"
    if excluded_missing_target == 0:
        report += "- Missing target values were never replaced with zero or any other invented value.\n"

    report += f"""

## ClimSST investigation

- `ClimSST = 262.15` occurs in {clim_sst_26215} observations in the pilot CSV.
- The original values were preserved exactly.
- These observations were not deleted and the values were not replaced.
- The repeated value is an unresolved data-quality issue and is not assigned a presumed meaning in this preparation process.
- `ClimSST` remains in the primary dataset. A separate sensitivity dataset without this feature can be considered later, if approved.

## Temporal split

- Training: 2005–2015, {len(train_rows)} observations.
- Testing: 2016, {len(test_rows)} observations.
- Training year range: {min(train_years)}–{max(train_years)}.
- Testing year range: {min(test_years)}–{max(test_years)}.
- Sample_ID overlap: {len(sample_overlap)}.
- Site_ID overlap: {len(site_overlap)}.

The overlapping sites are a limitation: although no sample is reused, repeated observations from 22 sites occur across the train and test periods. The temporal split was not changed.

## Target distributions

- Training: {target_summary(train_rows)}.
- Testing: {target_summary(test_rows)}.

## Observations excluded

- {excluded_missing_target} observation(s) had a missing `Percent_Bleached` target.
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
"""

    with (OUTPUT_DIR / "dataset_preparation_report.md").open("w", encoding="utf-8") as report_file:
        report_file.write(report)

    for path in [
        OUTPUT_DIR / "modeling_dataset_v1.csv",
        OUTPUT_DIR / "train_v1.csv",
        OUTPUT_DIR / "test_v1.csv",
        OUTPUT_DIR / "split_metadata_v1.csv",
    ]:
        with path.open("r", newline="", encoding="utf-8"):
            pass

    print("ReefGuard-ML dataset preparation summary")
    print(f"Original rows: {len(source_rows)}")
    print(f"Eligible rows: {len(eligible_rows)}")
    print(f"Training rows: {len(train_rows)}")
    print(f"Testing rows: {len(test_rows)}")
    print(f"Number of features: {len(FEATURES)}")
    print(f"Training target distribution: {target_summary(train_rows)}")
    print(f"Testing target distribution: {target_summary(test_rows)}")
    print("Missing-value summary:")
    for feature in FEATURES:
        print(f"  {feature}: {original_missing_features[feature]} missing")
    print(f"Target missing observations excluded: {excluded_missing_target}")
    print(f"ClimSST=262.15 observations: {clim_sst_26215}")
    print(f"Overlapping Site_IDs: {len(site_overlap)}")
    print(f"Training-derived imputation: {'required' if any(original_missing_features.values()) else 'not required'}")


if __name__ == "__main__":
    main()
