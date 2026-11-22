ReefGuard-ML: Practical workflow
1. Data exploration — almost complete
   
   Finish your existing notebook. Keep the important charts, dataset statistics, missing-value analysis, and limitations. Avoid adding more exploratory analysis unless it affects our model.
   Current stage
2.  Prepare the modelling dataset
   - Select relevant environmental features.
   - Exclude IDs and leakage-prone columns.
   - Handle missing values if they arise.
   - Document the ClimSST issue.
   - Create reproducible train/test datasets.
3. Establish the baseline
   
   We already have this:
   - MAE: 7.3684
   - RMSE: 10.0726
   - Bias: +1.3439
   Keep this as our reference point.
4. Train actual ML models
   
   Start with:
   - Linear Regression
   - Random Forest Regressor
   Compare both against the median baseline. Don't introduce complex models unless the simpler ones fail to provide useful results.
5. Evaluate and visualize
   
   Produce:
   - Model performance comparison.
   - Actual vs predicted bleaching.
   - Prediction error distribution.
   - Feature importance (for Random Forest).
   Explain what each result means.
6. Build the working prototype
   
   A simple interface where someone can enter environmental measurements and receive an estimated bleaching percentage.
   
   Display the prediction, a clear interpretation, and a disclaimer about its limitations.
7. Submission preparation
   - Project README
   - Architecture/workflow diagram
   - Demonstration screenshots or video
   - Model evaluation results
   - Known limitations and future improvements