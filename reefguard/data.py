from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from reefguard.config import (
    COMPARISON_PATH,
    FEATURE_IMPORTANCE_PATH,
    FEATURES,
    PILOT_DATA_PATH,
    PREDICTIONS_PATH,
    TARGET,
    TEMPORAL_VALIDATION_PATH,
    TEST_DATA_PATH,
    TRAIN_DATA_PATH,
)


@st.cache_data(show_spinner=False)
def load_pilot_data() -> pd.DataFrame:
    data = pd.read_csv(PILOT_DATA_PATH)
    required = {"Date_Year", TARGET, *FEATURES}
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"Pilot dataset is missing required columns: {', '.join(missing)}")

    for column in ["Date_Year", TARGET, *FEATURES]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
        if data[column].isna().any() or not np.isfinite(data[column].to_numpy(dtype=float)).all():
            raise ValueError(f"Pilot dataset contains missing or nonnumeric values in {column}")

    if not data[TARGET].between(0, 100).all():
        raise ValueError("Pilot dataset contains Percent_Bleached values outside 0–100")
    return data


@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Required project artifact was not found: {source}")
    return pd.read_csv(source)


def load_evaluation_artifacts() -> dict[str, pd.DataFrame]:
    return {
        "comparison": load_csv(str(COMPARISON_PATH)),
        "predictions": load_csv(str(PREDICTIONS_PATH)),
        "test": load_csv(str(TEST_DATA_PATH)),
        "importance": load_csv(str(FEATURE_IMPORTANCE_PATH)),
        "temporal": load_csv(str(TEMPORAL_VALIDATION_PATH)),
        "train": load_csv(str(TRAIN_DATA_PATH)),
    }


@lru_cache(maxsize=1)
def feature_ranges() -> dict[str, tuple[float, float]]:
    data = load_pilot_data()
    return {
        feature: (float(data[feature].min()), float(data[feature].max()))
        for feature in FEATURES
    }


def filter_historical_data(
    data: pd.DataFrame,
    start_year: int,
    end_year: int,
    minimum_bleaching: float,
    maximum_bleaching: float,
) -> pd.DataFrame:
    if start_year > end_year:
        raise ValueError("The start year must not be after the end year.")
    if not 0 <= minimum_bleaching <= maximum_bleaching <= 100:
        raise ValueError("Bleaching filters must be ordered within 0–100.")
    return data.loc[
        data["Date_Year"].between(start_year, end_year)
        & data[TARGET].between(minimum_bleaching, maximum_bleaching)
    ].copy()


def environmental_summary(data: pd.DataFrame) -> pd.DataFrame:
    summary = data.loc[:, FEATURES].describe().T
    return summary.loc[:, ["count", "mean", "std", "min", "50%", "max"]].rename(
        columns={"50%": "median"}
    )
