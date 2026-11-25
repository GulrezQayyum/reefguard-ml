from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from reefguard.config import FEATURE_LABELS, TARGET


OCEAN = "#103F46"
TURQUOISE = "#42C9BA"
CORAL = "#FF806F"
SEAFOAM = "#EAF5F1"
MUTED = "#627A7B"
MODEL_COLORS = {
    "Median Baseline": "#627A7B",
    "Linear Regression": TURQUOISE,
    "Random Forest": CORAL,
}


def style_figure(figure, height: int = 380):
    figure.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#F7FAF8",
        font={"family": "Inter, sans-serif", "color": OCEAN, "size": 12},
        margin={"l": 22, "r": 18, "t": 28, "b": 26},
        legend={"orientation": "h", "y": 1.12, "x": 0},
        hoverlabel={"bgcolor": "#082B36", "font_color": "white"},
    )
    figure.update_xaxes(
        showgrid=True,
        gridcolor="#DDE9E4",
        zeroline=False,
        tickfont_color=OCEAN,
        title_font_color=OCEAN,
    )
    figure.update_yaxes(
        showgrid=True,
        gridcolor="#DDE9E4",
        zeroline=False,
        tickfont_color=OCEAN,
        title_font_color=OCEAN,
    )
    return figure


def bleaching_distribution(data: pd.DataFrame):
    figure = px.histogram(
        data,
        x=TARGET,
        nbins=28,
        color_discrete_sequence=[TURQUOISE],
        labels={TARGET: "Observed bleaching (%)", "count": "Observations"},
    )
    figure.update_traces(marker_line_width=0, opacity=0.9)
    figure.update_layout(bargap=0.08, showlegend=False)
    return style_figure(figure)


def annual_bleaching(data: pd.DataFrame):
    yearly = (
        data.groupby("Date_Year", as_index=False)
        .agg(median_bleaching=(TARGET, "median"), observations=(TARGET, "size"))
    )
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=yearly["Date_Year"],
            y=yearly["median_bleaching"],
            mode="lines+markers",
            name="Yearly median",
            line={"color": OCEAN, "width": 3},
            marker={"color": TURQUOISE, "size": 8},
            customdata=yearly[["observations"]],
            hovertemplate="Year %{x}<br>Median %{y:.2f}%<br>Records %{customdata[0]}<extra></extra>",
        )
    )
    figure.update_layout(yaxis_title="Median bleaching (%)", xaxis_title="Year")
    return style_figure(figure)


def selected_feature_scatter(data: pd.DataFrame, feature: str):
    figure = px.scatter(
        data,
        x=feature,
        y=TARGET,
        color="Date_Year",
        color_continuous_scale=["#B7E9DE", OCEAN],
        opacity=0.68,
        labels={
            feature: FEATURE_LABELS.get(feature, feature),
            TARGET: "Observed bleaching (%)",
            "Date_Year": "Year",
        },
        hover_data=["Date_Year"],
    )
    figure.update_traces(marker={"size": 7})
    return style_figure(figure, 420)


def feature_distribution(data: pd.DataFrame, feature: str):
    figure = px.histogram(
        data,
        x=feature,
        nbins=28,
        color_discrete_sequence=[TURQUOISE],
        labels={feature: FEATURE_LABELS.get(feature, feature), "count": "Observations"},
    )
    figure.update_traces(marker_line_width=0)
    figure.update_layout(showlegend=False, bargap=0.08)
    return style_figure(figure)


def model_comparison_chart(comparison: pd.DataFrame):
    metric_data = comparison.melt(
        id_vars="Model", value_vars=["MAE", "RMSE"], var_name="Metric", value_name="Error"
    )
    figure = px.bar(
        metric_data,
        x="Model",
        y="Error",
        color="Metric",
        barmode="group",
        color_discrete_map={"MAE": TURQUOISE, "RMSE": CORAL},
        labels={"Error": "Percentage points", "Model": ""},
    )
    return style_figure(figure, 360)


def actual_vs_predicted_chart(predictions: pd.DataFrame):
    names = {
        "Median baseline prediction": "Median Baseline",
        "Linear Regression prediction": "Linear Regression",
        "Random Forest prediction": "Random Forest",
    }
    figure = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=list(names.values()),
        shared_xaxes=True,
        shared_yaxes=True,
        horizontal_spacing=0.06,
    )
    actual = predictions["Actual Percent_Bleached"]
    maximum = max(float(actual.max()), 100.0)
    figure.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=maximum,
        y1=maximum,
        line={"color": MUTED, "dash": "dash", "width": 1},
        row="all",
        col="all",
    )
    for index, (column, label) in enumerate(names.items(), start=1):
        figure.add_trace(
            go.Scatter(
                x=actual,
                y=predictions[column],
                mode="markers",
                name=label,
                marker={"color": MODEL_COLORS[label], "size": 6, "opacity": 0.7},
                showlegend=False,
                hovertemplate="Actual %{x:.2f}%<br>Predicted %{y:.2f}%<extra></extra>",
            ),
            row=1,
            col=index,
        )
    figure.update_xaxes(title_text="Actual bleaching (%)", row=1, col=2)
    figure.update_yaxes(title_text="Predicted (%)", row=1, col=1)
    return style_figure(figure, 400)


def residual_distribution(predictions: pd.DataFrame):
    columns = {
        "Median baseline prediction": "Median Baseline",
        "Linear Regression prediction": "Linear Regression",
        "Random Forest prediction": "Random Forest",
    }
    figure = go.Figure()
    for column, label in columns.items():
        residuals = predictions["Actual Percent_Bleached"] - predictions[column]
        figure.add_trace(
            go.Histogram(
                x=residuals,
                name=label,
                opacity=0.55,
                marker_color=MODEL_COLORS[label],
                nbinsx=32,
            )
        )
    figure.add_vline(x=0, line_dash="dash", line_color=OCEAN, line_width=1)
    figure.update_layout(
        barmode="overlay",
        xaxis_title="Residual (actual − predicted), percentage points",
        yaxis_title="Observations",
    )
    return style_figure(figure, 360)


def feature_importance_chart(importance: pd.DataFrame):
    ordered = importance.sort_values("Importance", ascending=True)
    figure = px.bar(
        ordered,
        x="Importance",
        y="Feature",
        orientation="h",
        color_discrete_sequence=[TURQUOISE],
        labels={"Importance": "Impurity-based importance", "Feature": ""},
    )
    figure.update_layout(showlegend=False)
    return style_figure(figure, 360)


def temporal_validation_chart(temporal: pd.DataFrame):
    folds = temporal.loc[temporal["Fold"] != "Aggregate"].copy()
    folds["MAE"] = pd.to_numeric(folds["MAE"], errors="coerce")
    folds = folds.dropna(subset=["MAE"])
    folds["Series"] = folds.apply(
        lambda row: "Median Baseline" if row["Model"] == "Median Baseline" else row["Configuration"],
        axis=1,
    )
    colors = {
        "Median Baseline": MUTED,
        "RF-1": "#2C8190",
        "RF-2": CORAL,
        "RF-3": "#42A88F",
        "RF-4": "#8074A8",
    }
    figure = px.line(
        folds,
        x="Fold",
        y="MAE",
        color="Series",
        markers=True,
        color_discrete_map=colors,
        labels={"MAE": "Fold MAE (percentage points)", "Fold": ""},
    )
    return style_figure(figure, 380)


def yearly_observation_counts(data: pd.DataFrame):
    yearly = data.groupby("Date_Year", as_index=False).size()
    figure = px.bar(
        yearly,
        x="Date_Year",
        y="size",
        color_discrete_sequence=[TURQUOISE],
        labels={"Date_Year": "Year", "size": "Observations"},
    )
    figure.update_layout(showlegend=False)
    return style_figure(figure, 330)
