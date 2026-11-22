import csv
import math
from pathlib import Path


DATA_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "frrp_baseline_pilot_v0_1.csv"
)
TARGET = "Percent_Bleached"


def median(values):
    values = sorted(values)
    n = len(values)
    if n == 0:
        raise ValueError("Cannot calculate a median from an empty set")
    middle = n // 2
    if n % 2:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2


def metrics(actual, predicted):
    errors = [a - p for a, p in zip(actual, predicted)]
    mae = sum(abs(error) for error in errors) / len(errors)
    rmse = math.sqrt(sum(error * error for error in errors) / len(errors))
    bias = sum(errors) / len(errors)
    return mae, rmse, bias


with DATA_PATH.open(newline="") as source:
    rows = list(csv.DictReader(source))

train = [row for row in rows if int(float(row["Date_Year"])) < 2016]
test = [row for row in rows if int(float(row["Date_Year"])) == 2016]

train_target = [float(row[TARGET]) for row in train]
test_target = [float(row[TARGET]) for row in test]
baseline = median(train_target)
mae, rmse, bias = metrics(test_target, [baseline] * len(test_target))

print(f"Rows: {len(rows)}")
print(f"Temporal train: 2005-2015 ({len(train)} rows)")
print(f"Temporal test: 2016 ({len(test)} rows)")
print(f"Training target median: {baseline:.4f}")
print(f"MAE: {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"Mean error (actual - predicted): {bias:.4f}")
