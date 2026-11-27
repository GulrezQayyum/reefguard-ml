## ReefGuard-ML project notes

The original staged checklist is complete: the repository now includes
prepared datasets, a median baseline, Linear Regression and Random Forest
experiments, temporal validation, saved evaluation outputs, a Streamlit
prototype, and tests.

The current results do not show that the initial ML models beat the median
baseline on the 2016 comparison. RF-2 has a lower mean MAE than the baseline
in the historical expanding-window validation, but wins in only one of three
folds. These outcomes should be presented with the existing scientific
limitations, not as evidence of a validated forecast.

Use the [README](README.md) for the current data description, reproducibility
commands, architecture, findings, and limitations. Before public
redistribution, verify attribution and licensing for the source data; terms
are not established in the repository.