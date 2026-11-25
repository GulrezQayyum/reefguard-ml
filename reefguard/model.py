from __future__ import annotations

from collections.abc import Mapping

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from reefguard.config import FEATURES, MODEL_PATH
from reefguard.data import feature_ranges


@st.cache_resource(show_spinner="Loading the saved Random Forest pipeline...")
def load_saved_pipeline():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Saved model pipeline was not found: {MODEL_PATH}")
    pipeline = joblib.load(MODEL_PATH)
    actual_features = tuple(getattr(pipeline, "feature_names_in_", ()))
    if actual_features != FEATURES:
        raise ValueError(
            "Saved pipeline features do not match the required feature names and order. "
            f"Expected {FEATURES}; found {actual_features}."
        )
    return pipeline


def saved_model_parameters(pipeline) -> dict[str, object]:
    estimator = pipeline.named_steps.get("model")
    if estimator is None or not hasattr(estimator, "get_params"):
        raise ValueError("Saved pipeline does not contain a compatible model step")
    parameters = estimator.get_params()
    return {
        "n_estimators": parameters.get("n_estimators"),
        "max_depth": parameters.get("max_depth"),
        "min_samples_leaf": parameters.get("min_samples_leaf"),
        "random_state": parameters.get("random_state"),
    }


def validate_feature_values(values: Mapping[str, object]) -> list[float]:
    missing_keys = [feature for feature in FEATURES if feature not in values]
    if missing_keys:
        raise ValueError(f"Missing required inputs: {', '.join(missing_keys)}")

    observed_ranges = feature_ranges()
    ordered_values: list[float] = []
    for feature in FEATURES:
        raw_value = values[feature]
        if raw_value is None or isinstance(raw_value, bool):
            raise ValueError(f"{feature} is required and must be numeric.")
        try:
            value = float(raw_value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{feature} must be a numeric value.") from error
        if not np.isfinite(value):
            raise ValueError(f"{feature} must be a finite numeric value.")

        lower, upper = observed_ranges[feature]
        if value < lower or value > upper:
            raise ValueError(
                f"{feature} must be within its observed pilot-data range "
                f"({lower:g} to {upper:g}). No values are clipped."
            )
        ordered_values.append(value)
    return ordered_values


def predict_bleaching(values: Mapping[str, object]) -> float:
    ordered_values = validate_feature_values(values)
    pipeline = load_saved_pipeline()
    features = pd.DataFrame([ordered_values], columns=FEATURES)
    predictions = np.asarray(pipeline.predict(features), dtype=float)
    if predictions.shape != (1,) or not np.isfinite(predictions[0]):
        raise ValueError("The saved pipeline returned an invalid prediction.")
    return float(predictions[0])
