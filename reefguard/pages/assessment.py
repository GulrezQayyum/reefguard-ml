from __future__ import annotations

import streamlit as st

from reefguard.config import FEATURES, FEATURE_LABELS, FEATURE_UNITS, TARGET
from reefguard.data import feature_ranges, load_pilot_data
from reefguard.model import (
    load_saved_pipeline,
    predict_bleaching,
    saved_model_parameters,
)


def render() -> None:
    data = load_pilot_data()
    ranges = feature_ranges()
    st.markdown('<div class="page-kicker">Experimental model</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Bleaching Assessment</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">Enter a set of environmental observations to query the '
        'existing saved Random Forest pipeline. This tool is exploratory only; it is not a forecast, '
        'early-warning system, or conservation alert.</p>',
        unsafe_allow_html=True,
    )

    try:
        pipeline = load_saved_pipeline()
        parameters = saved_model_parameters(pipeline)
    except (FileNotFoundError, ImportError, OSError, ValueError) as error:
        st.error(f"The saved assessment pipeline could not be loaded: {error}")
        return

    st.markdown(
        '<div class="callout warning-callout"><strong>Model artifact mismatch:</strong> '
        'The saved pipeline is Random Forest v1 (300 trees, minimum leaf size 2). It is not the '
        'RF-2 configuration (200 trees, minimum leaf size 5) in the temporal-validation report. '
        'RF-2 has no saved fitted pipeline here, so this assessment uses only the existing v1 artifact. '
        'RF-2 validation results are reported separately and are not this model\'s performance.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    form_values = {}
    with st.form("bleaching_assessment_form"):
        st.markdown("#### Environmental inputs")
        st.caption(
            "Input limits are the observed minimum and maximum in the pilot dataset. "
            "Values outside that range are rejected rather than clipped."
        )
        columns = st.columns(2, gap="large")
        for index, feature in enumerate(FEATURES):
            label = FEATURE_LABELS.get(feature, feature)
            unit = FEATURE_UNITS.get(feature, "unit not documented")
            lower, upper = ranges[feature]
            with columns[index % 2]:
                st.caption(f"Observed range: {lower:g}–{upper:g} · {unit}")
                form_values[feature] = st.number_input(
                    f"{label} ({feature})",
                    min_value=lower,
                    max_value=upper,
                    value=None,
                    step=max((upper - lower) / 100, 0.01),
                    format="%.4f",
                    key=f"assessment_{feature}",
                    help=(
                        f"Observed pilot range: {lower:g}–{upper:g}. "
                        f"Unit: {unit}. No extrapolation is allowed."
                    ),
                )
        submitted = st.form_submit_button(
            "Calculate experimental estimate",
            type="primary",
            width="stretch",
        )

    if submitted:
        try:
            prediction = predict_bleaching(form_values)
        except ValueError as error:
            st.error(str(error))
        except (FileNotFoundError, ImportError, OSError) as error:
            st.error(f"Could not run the saved model: {error}")
        else:
            result, baseline = st.columns(2, gap="large")
            with result:
                st.metric("Saved model output", f"{prediction:.2f}%")
            with baseline:
                st.metric("Historical median baseline", f"{data[TARGET].median():.2f}%")
            if not 0 <= prediction <= 100:
                st.warning(
                    "The model output is outside the physical target range of 0–100%. "
                    "It is shown unchanged; no clipping or correction has been applied."
                )
            st.caption(
                f"Pipeline parameters loaded: n_estimators={parameters['n_estimators']}, "
                f"max_depth={parameters['max_depth']}, "
                f"min_samples_leaf={parameters['min_samples_leaf']}, "
                f"random_state={parameters['random_state']}."
            )
            st.markdown(
                '<div class="callout warning-callout">This is an experimental estimate from a saved '
                'model trained for the project, not a prediction of future conditions. The initial '
                'Random Forest performed worse than the historical median baseline on the 2016 test '
                'set (MAE 9.75 vs 7.37 percentage points). Interpret with caution.</div>',
                unsafe_allow_html=True,
            )

    st.markdown("#### Units and data quality")
    st.write(
        "Depth is recorded in metres. Project notes identify ClimSST and Temperature_Mean as Kelvin. "
        "Units or temporal windows for the remaining environmental fields are not confirmed in the "
        "available project documentation; do not infer units from the field names."
    )
    st.caption(
        "The repeated ClimSST value 262.15 occurs in 187 pilot observations and remains an "
        "unresolved data-quality issue in the source files."
    )
