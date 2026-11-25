from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PILOT_DATA_PATH = PROJECT_ROOT / "data" / "frrp_baseline_pilot_v0_1.csv"
MODELING_DATA_PATH = PROJECT_ROOT / "data" / "modeling" / "modeling_dataset_v1.csv"
TRAIN_DATA_PATH = PROJECT_ROOT / "data" / "modeling" / "train_v1.csv"
TEST_DATA_PATH = PROJECT_ROOT / "data" / "modeling" / "test_v1.csv"
PREDICTIONS_PATH = PROJECT_ROOT / "data" / "modeling" / "model_predictions_v1.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "random_forest_v1.joblib"
COMPARISON_PATH = PROJECT_ROOT / "reports" / "model_comparison_v1.csv"
FEATURE_IMPORTANCE_PATH = PROJECT_ROOT / "reports" / "random_forest_feature_importance_v1.csv"
TEMPORAL_VALIDATION_PATH = PROJECT_ROOT / "reports" / "time_aware_validation_summary_v1.csv"
HERO_IMAGE_PATH = PROJECT_ROOT / "reefguard" / "assets" / "coral-reef-hero.jpg"

TARGET = "Percent_Bleached"
FEATURES = (
    "Depth_m",
    "ClimSST",
    "Temperature_Mean",
    "SSTA",
    "SSTA_DHW",
    "TSA",
    "TSA_DHW",
    "Windspeed",
)

FEATURE_UNITS = {
    "Depth_m": "m",
    "ClimSST": "K",
    "Temperature_Mean": "K",
}

FEATURE_LABELS = {
    "Depth_m": "Depth",
    "ClimSST": "ClimSST",
    "Temperature_Mean": "Temperature mean",
    "SSTA": "SSTA",
    "SSTA_DHW": "SSTA_DHW",
    "TSA": "TSA",
    "TSA_DHW": "TSA_DHW",
    "Windspeed": "Windspeed",
}

NAV_ITEMS = (
    ("overview", "Overview"),
    ("data", "Data Explorer"),
    ("assessment", "Bleaching Assessment"),
    ("insights", "Environmental Insights"),
    ("evaluation", "Model Evaluation"),
    ("methodology", "Methodology"),
)
