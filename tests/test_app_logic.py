from __future__ import annotations

import unittest

import numpy as np

from reefguard.charts import (
    actual_vs_predicted_chart,
    annual_bleaching,
    bleaching_distribution,
    temporal_validation_chart,
)
from reefguard.config import FEATURES, PREDICTIONS_PATH, TEMPORAL_VALIDATION_PATH
from reefguard.data import (
    filter_historical_data,
    load_csv,
    load_pilot_data,
)
from reefguard.model import (
    load_saved_pipeline,
    predict_bleaching,
    validate_feature_values,
)


class ApplicationLogicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_pilot_data()
        cls.values = {
            feature: float(cls.data[feature].median())
            for feature in FEATURES
        }

    def test_historical_filters_apply_both_ranges(self) -> None:
        filtered = filter_historical_data(self.data, 2010, 2011, 10, 20)
        self.assertFalse(filtered.empty)
        self.assertTrue(filtered["Date_Year"].between(2010, 2011).all())
        self.assertTrue(filtered["Percent_Bleached"].between(10, 20).all())
        self.assertEqual(len(self.data), 2394)

    def test_historical_filters_reject_invalid_bounds(self) -> None:
        with self.assertRaises(ValueError):
            filter_historical_data(self.data, 2011, 2010, 0, 100)
        with self.assertRaises(ValueError):
            filter_historical_data(self.data, 2010, 2011, 25, 10)

    def test_assessment_checks_values_and_preserves_feature_order(self) -> None:
        reversed_values = dict(reversed(list(self.values.items())))
        ordered = validate_feature_values(reversed_values)
        self.assertEqual(ordered, [self.values[name] for name in FEATURES])

        invalid_cases = [
            {**self.values, "Depth_m": None},
            {**self.values, "Depth_m": "not numeric"},
            {**self.values, "Depth_m": float("inf")},
            {**self.values, "Depth_m": 1000},
        ]
        for values in invalid_cases:
            with self.subTest(values=values["Depth_m"]), self.assertRaises(ValueError):
                validate_feature_values(values)

    def test_saved_pipeline_predicts_finite_result(self) -> None:
        pipeline = load_saved_pipeline()
        self.assertEqual(tuple(pipeline.feature_names_in_), FEATURES)
        result = predict_bleaching(self.values)
        self.assertTrue(np.isfinite(result))

    def test_data_and_evaluation_charts_render(self) -> None:
        filtered = filter_historical_data(self.data, 2010, 2011, 0, 100)
        prediction_rows = load_csv(str(PREDICTIONS_PATH))
        temporal = load_csv(str(TEMPORAL_VALIDATION_PATH))
        figures = [
            bleaching_distribution(filtered),
            annual_bleaching(filtered),
            actual_vs_predicted_chart(prediction_rows),
            temporal_validation_chart(temporal),
        ]
        for figure in figures:
            with self.subTest(figure=figure):
                self.assertTrue(figure.to_json())


if __name__ == "__main__":
    unittest.main()
