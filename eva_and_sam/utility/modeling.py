import os
from pathlib import Path
import pandas as pd
import numpy as np
import altair as alt
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, make_scorer

ANALYTIC_DATA_PATH = 'data/analytic_data/'
PREDICTION_PATH = 'data/predictions/'
EVALUATION_PATH = 'data/evaluation_data/'
PCA_ENDPOINT = 'PCAcomponents_'
UTIL_PLOT_PATH = 'data/plots/'
FLASK_PLOT_PATH = '../flask/templates/plots/'
FLASK_TABLE_PATH = '../flask/templates/tables/'
EVAL_METRICS = {}
EVAL_DFS = []

def import_and_preprocess_features():
    print("IMPORTING AND PREPROCESSING FEATURES")
    if os.path.exists(ANALYTIC_DATA_PATH):
        train_df = pd.read_csv(ANALYTIC_DATA_PATH+PCA_ENDPOINT+"train.csv")
        test_df = pd.read_csv(ANALYTIC_DATA_PATH+PCA_ENDPOINT+"test.csv")
        y_train_df = pd.read_csv(ANALYTIC_DATA_PATH+"y_train.csv")
        y_train_filtered = y_train_df[y_train_df.SUM != 0]
        filtered_index = y_train_filtered.index
        train_filtered = train_df.iloc[filtered_index]
        labels = y_train_filtered.SUM

        X_train = train_filtered.to_numpy(dtype=float, copy=True)
        y_train = labels.to_numpy(dtype=float, copy=True)
        X_test = test_df.to_numpy(dtype=float, copy=True)
    else:
        print("FileNotFoundError: Please run utility scripts and try again.")
    return X_train, y_train, X_test

def save_table_as_html(df, table_path):
    df_rounded = df.round(3)
    if os.path.exists(FLASK_TABLE_PATH) == False:
        os.mkdir(FLASK_TABLE_PATH)

    if os.path.exists(FLASK_TABLE_PATH) == True:
        buffer = Path(FLASK_TABLE_PATH+table_path)
        df_rounded.to_html(buf=buffer, index=False, justify='center')
        print("SAVED HTML IN WEB APP DIRECTORY")

    else:
        buffer = Path('data/html')
        print(buffer)
        df_rounded.to_html(buf=buffer, index=False, justify='center')
        print("SAVED CHART IN UTILITY DIRECTORY")

def save_alt_chart(alt_chart, chart_path):
    if os.path.exists(UTIL_PLOT_PATH) == False:
        os.mkdir(UTIL_PLOT_PATH)
    if os.path.exists(FLASK_PLOT_PATH) == True:
        alt_chart.save(FLASK_PLOT_PATH+chart_path)
        print("Saved Chart in Web App Directory")
    else:
        alt_chart.save(UTIL_PLOT_PATH+chart_path)
        print("Saved Chart in Utility Directory")

def save_final_predictions(preds_df, file_path):
    if os.path.exists(PREDICTION_PATH) == False:
        os.mkdir(PREDICTION_PATH)
    print("WRITING FINAL PREDICTIONS")
    preds_df.to_csv(PREDICTION_PATH+file_path, index=False)

def save_evals(eval_df, file_path):
    if os.path.exists(EVALUATION_PATH) == False:
        os.mkdir(PREDICTION_PATH)
    print("WRITING EVALUATIONS")
    eval_df.to_csv(EVALUATION_PATH+file_path+'.csv', index=False)

def generate_residual_scatterplot(eval_df, save_plot=True, model_name=None, multi_models=False):
    chart_path = (model_name.lower().replace(" ", "_") + "_residual_scatter_plot.html")
    title_text = model_name + " Residuals"
    if multi_models == True:
        pca_scatter = alt.Chart(eval_df
        ).mark_circle(size=60, opacity=0.3
        ).encode(x="PC1:Q", y="resid:Q", color='model:N'
        ).properties(title=title_text
        ).configure_title(fontSize=20, font='Courier', anchor='start', color='gray'
        ).interactive()
    else:
        pca_scatter = alt.Chart(eval_df
        ).mark_circle(size=60
        ).encode(x="PC1:Q", y="resid:Q",
        ).properties(title=title_text
        ).configure_title(fontSize=20, font='Courier', anchor='start', color='gray'
        ).interactive()

    if save_plot:
        save_alt_chart(pca_scatter, chart_path)
    return pca_scatter

def evaluate_model(X_train, y_train, model, model_name):
    preds = model.predict(X_train)
    r2 = model.score(X_train, y_train)
    mse = mean_squared_error(y_train, preds)
    EVAL_METRICS[model_name] = {'r2': r2, 'mse': mse}

    eval_df = pd.DataFrame(X_train[:,0]).rename(columns={0:'PC1'})
    eval_df['obs_y'] = y_train
    eval_df['pred_y'] = preds
    eval_df['resid'] = eval_df.obs_y - eval_df.pred_y
    eval_df['model'] = model_name

    EVAL_DFS.append(eval_df)

    return eval_df, preds

def compare_metrics(print_scores=True):
    print("COMPARING EVALUATION SCORES")
    eval_metrics_df = pd.DataFrame.from_dict(EVAL_METRICS)
    eval_metrics_long = eval_metrics_df.T.reset_index().rename(columns={'index':'model'})

    max_r2 = eval_metrics_long.r2.max()
    max_r2_model = eval_metrics_long[eval_metrics_long.r2 == max_r2]['model'].values
    best_r2 = (max_r2_model, round(max_r2, 3))

    min_mse = eval_metrics_long.mse.min()
    min_mse_model = eval_metrics_long[eval_metrics_long.mse == min_mse]['model'].values
    best_mse = (min_mse_model, round(min_mse, 3))

    best_scores = {'r2': best_r2, 'mse': best_mse}
    if print_scores == True:
        for metric, best in best_scores.items():
            print(f"Best {metric} model: {best[0]} | score={best[1]}")
    return best_scores

def get_user_optimize_decision(input_prompt):
    valid_input = False
    validated = ""
    error_msg = "Invalid Input. Please enter Yes or No."
    while not valid_input:
        user_input = input(input_prompt)
        try:
            standardized = str(user_input).lower().strip()
        except ValueError as x:
            print(error_msg)
            continue
        if "y" in standardized:
            valid_input = True
            validated = True
        elif "n" in standardized:
            valid_input = True
            validated = False
        else:
            print(error_msg)
    return validated

def optimize_svm(X_train, y_train, return_best=True):
    print("OPTIMIZING SVM MODEL. THIS WILL TAKE A WHILE.")
    param_grid = {
        'C': [.1, 1.0, 1.5],
        'kernel': ['linear', 'poly', 'rbf'],
        'degree': [2, 3, 4],
        'gamma': [1,0.1,0.01,0.001],
        'shrinking': [True, False]
    }
    scorers = {
        'r2': make_scorer(r2_score, greater_is_better=True),
        'mse': make_scorer(mean_squared_error, greater_is_better=False)
    }
    grid = GridSearchCV(svm.SVR(), refit='r2', scoring=scorers, param_grid=param_grid)
    grid.fit(X_train, y_train)
    eval_df, preds = evaluate_model(X_train, y_train, grid, "optimized svm")
    scatter = generate_residual_scatterplot(eval_df, model_name="Optimized SVM Regression")
    if return_best == True:
        print(f'Best parameters: {grid.best_params_}')
        print(f'Best scores: {grid.best_score_}')
    return grid, eval_df, preds, scatter

print("STARTING UTILITY: PREDICTIVE MODELING")

X_train, y_train, X_test = import_and_preprocess_features()
y_train = np.nan_to_num(y_train)
y_train_transformed = np.log(y_train).ravel()

print("Fitting and Evaluating Baseline (Linear Regression)")
# baseline linreg
lr = LinearRegression()
lr_base = lr.fit(X_train, y_train_transformed)
lr_eval_df, lr_preds = evaluate_model(X_train, y_train_transformed, lr_base, "baseline")
# major heteroskedasticity in residuals
lr_base_resid = generate_residual_scatterplot(lr_eval_df, save_plot=True, model_name="Baseline Linear Regression")

print("Fitting and Evaluating Ridge Regression")
# Ridge - same as baseline
lr_ridge = Ridge()
lrr = lr_ridge.fit(X_train, y_train_transformed)
lrr_eval_df, lrr_preds = evaluate_model(X_train, y_train_transformed, lrr, "ridge")
# major heteroskedasticity in residuals
lrr_base_resid = generate_residual_scatterplot(lrr_eval_df, save_plot=True, model_name="Linear Regression Ridge")

print("Fitting and Evaluating Lasso Regression")
# Lasso - worse than baseline
lr_lasso = Lasso()
lrl = lr_lasso.fit(X_train, y_train_transformed)
lrl_eval_df, lrl_preds = evaluate_model(X_train, y_train_transformed, lrl, "lasso")
# major heteroskedasticity in residuals
lrl_base_resid = generate_residual_scatterplot(lrl_eval_df, save_plot=True, model_name="Linear Regression Lasso")

print("Fitting and Evaluating Elastic Net Regression")
# Elastic Net - worse than baseline
lr_elastic = ElasticNet()
lren = lr_elastic.fit(X_train, y_train_transformed)
lren_eval_df, lren_preds = evaluate_model(X_train, y_train_transformed, lren, "elastic net")
# major heteroskedasticity in residuals
lren_base_resid = generate_residual_scatterplot(lren_eval_df, save_plot=True, model_name="Linear Regression Elastic Net")

print("Fitting and Evaluating SVM Regression Baseline")
# baseline svm regressor - same as baseline
regr_base = svm.SVR(kernel='linear')
svmr_base = regr_base.fit(X_train, y_train_transformed)
svmr_base_eval_df, svmr_preds = evaluate_model(X_train, y_train_transformed, svmr_base, "baseline svm")
svmr_base_resid = generate_residual_scatterplot(svmr_base_eval_df, save_plot=True, model_name="Baseline SVM Regression")

# compare metrics to determine if optimization is needed
current_best_scores = compare_metrics()

# optional svm optimization
optimize_svm_prompt = "Optimize SVM model? (Y/N)"
optimize = get_user_optimize_decision(optimize_svm_prompt)
if optimize == True:
    svm_optim = optimize_svm(X_train, y_train_transformed)
    grid_eval_df, grid_preds = evaluate_model(X_train, y_train_transformed, svm_optim, "optimized svm")
    grid_resid = generate_residual_scatterplot(grid_eval_df, model_name="Optimized SVM Regression")

# compare evaluation metrics
eval = pd.concat(EVAL_DFS, axis=0)
eval_resid = generate_residual_scatterplot(eval, model_name="All Models", multi_models=True)

eval_metrics_df = pd.DataFrame.from_dict(EVAL_METRICS)
eval_metrics_long = eval_metrics_df.T.reset_index().rename(columns={'index':'model'})
print("FINAL MODELING METRICS")
print(eval_metrics_long)
_ = save_table_as_html(eval_metrics_long, 'evaluation_metrics_table.html')
eval_bars_r2 = alt.Chart(eval_metrics_long).mark_bar().encode(
    y='model:N',
    x=alt.X('r2:Q', axis=alt.Axis(title='R-squared')),
    tooltip = ['model', 'r2']
)
eval_bars_mse = alt.Chart(eval_metrics_long).mark_bar().encode(
    y='model:N',
    x=alt.X('mse:Q', axis=alt.Axis(title='Mean Squared Error')),
    tooltip = ['model', 'mse']
)
eval_metrics_chart = eval_bars_r2 & eval_bars_mse
eval_metrics_chart = eval_metrics_chart.resolve_scale(x='shared'
).properties(title="Evaluation Metric Scores"
        ).configure_title(fontSize=20, font='Courier', anchor='start', color='gray'
        )

save_alt_chart(eval_metrics_chart, "eval_metrics_bar_chart.html")

# make predictions
print("MAKING PREDICTIONS ON TEST DATA")
y_pred_lr = lr.predict(X_test)
y_pred_svm = svmr_base.predict(X_test)
test_preds = pd.DataFrame(X_test[:,0]).rename(columns={0:'PC1'})
test_preds['lr_preds'] = y_pred_lr
test_preds['svm_preds'] = y_pred_svm

preds_scatter = alt.Chart(test_preds).mark_circle().transform_fold(
    fold=['lr_preds', 'svm_preds'], 
    as_=['model', 'prediction']
).encode(
    x='PC1:Q',
    y=alt.Y('value:Q', axis=alt.Axis(title='Energy Consumption')),
    color='model:N'
)

# lr_preds_scatter = alt.Chart(test_preds).mark_circle(color='green',opacity=0.3).encode(
#     x='PC1:Q',
#     y=,
# )
# svm_preds_scatter = alt.Chart(test_preds).mark_circle(color='steelblue', opacity=0.3).encode(
#     x='PC1:Q',
#     y=alt.Y('svm_preds:Q', axis=alt.Axis(title='Energy Consumption'))
# )
# (lr_preds_scatter + svm_preds_scatter)
preds_scatter = preds_scatter.properties(title="2018 Predicted Energy Consumption by Model Type"
        ).configure_title(fontSize=20, font='Courier', anchor='start', color='gray'
        )
save_alt_chart(preds_scatter, 'predicted_energy_consumption_scatter.html')
save_final_predictions(test_preds, "test_predictions.csv")
print("PREDICTIVE MODELING COMPLETE")