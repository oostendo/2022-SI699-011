import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import altair as alt

YEARS = [2012, 2018]
ANALYTIC_DATA_PATH = 'data/analytic_data/'
ANALYTIC_PATH_ENDPOINTS = {2012: 'train.csv', 2018: 'test.csv'}
UTIL_PLOT_PATH = 'data/plots/'
FLASK_PLOT_PATH = '../flask/templates/plots/'
RANDOM_STATE = 699

def read_analytic_data():
    print("READING ANALYTIC DATA")
    if os.path.exists(ANALYTIC_DATA_PATH):
        train_df = pd.read_csv(ANALYTIC_DATA_PATH+ANALYTIC_PATH_ENDPOINTS[2012])
        test_df = pd.read_csv(ANALYTIC_DATA_PATH+ANALYTIC_PATH_ENDPOINTS[2018])
    else:
        print("FileNotFoundError: Please run utility scripts and try again.")
    return train_df, test_df

def save_alt_chart(alt_chart, chart_path):
    if os.path.exists(UTIL_PLOT_PATH) == False:
        os.mkdir(UTIL_PLOT_PATH)

    if os.path.exists(FLASK_PLOT_PATH) == True:
        alt_chart.save(FLASK_PLOT_PATH+chart_path)
        print("SAVED CHART IN WEB APP DIRECTORY")
    else:
        alt_chart.save(UTIL_PLOT_PATH+chart_path)
        print("SAVED CHART IN UTILITY DIRECTORY")

def save_pca_output(pca_output, csv_path, train=True):
    if train == False:
        dataset = 'TEST DATA'
    else:
        dataset = 'TRAIN DATA'
    if os.path.exists(ANALYTIC_DATA_PATH):
        print(f"SAVING PCA COMPONENTS: {dataset}")
        np.savetxt(csv_path, pca_output, delimiter=',')
    else:
        print("DirectoryNotFoundError: Please run utility scripts and try again.")

def generate_2d_pca_scatterplot(pca_components, save_plot=True, train=True):
    if train == False:
        year = str(YEARS[1])
    else:
        year = str(YEARS[0])

    chart_path = year + "PCA_scatter_plot.html"
    title_text = year + " Building Characteristics"
    pca_df = pd.DataFrame(pca_components)
    new_cols = {}
    for col_index in pca_df.columns:
        new_cols[col_index] = "PC"+str(col_index+1)
    pca_df.rename(columns=new_cols, inplace=True)

    pca_scatter = alt.Chart(pca_df
    ).mark_circle(size=60
    ).encode(x="PC1:Q", y="PC2:Q",
    ).properties(title=title_text
    ).configure_title(fontSize=20, font='Courier', anchor='start', color='gray'
    ).interactive()

    if save_plot:
        save_alt_chart(pca_scatter, chart_path)
    return pca_scatter

def get_user_defined_threshold(input_prompt):
    valid_input = False
    decimal = -1
    error_range_msg = "Invalid Value. Please enter a valid number between 0 and 1"
    error_type_msg = "Invalid Type. Please enter a valid decimal between 0 and 1"
    while not valid_input:
        user_input = input(input_prompt)
        try:
            decimal = float(user_input)
        except ValueError as x:
            print(error_type_msg)
            continue
        if decimal > 0.0 and decimal < 1.0:
            valid_input = True
            validated = decimal
        else:
            print(error_range_msg)
    return validated

def narrow_num_components(user_input=False, return_summary=True, print_components=True):
    if user_input:
        # define user prompts
        user_input_thresh = {
            'min': "Define a minimum explained variance threshold (0 to 1): ",
            'max': "Define a maximum explained variance threshold (0 to 1): "
        }

        # get valid user input (decimal between 0 and 1)
        validated_thresh = {}
        for k,v in user_input_thresh.items():
            validated_thresh[k] = get_user_defined_threshold(v)
    else:
        validated_thresh = {
            'min': .8,
            'max': .95
        }
        print("Using Default Cutoffs")

    # extract components based on threshold definitions
    threshold_exp_var = pca_exp_var[(pca_exp_var.cum_exp_var >= validated_thresh['min']) & (pca_exp_var.cum_exp_var <= validated_thresh['max'])].copy()
    components = {
        'Minimum': int(threshold_exp_var.num_components.min()),
        'Median': int(threshold_exp_var.num_components.median()),
        'Maximum': int(threshold_exp_var.num_components.max())
    }

    # display components
    if print_components == True:
        for k, v in components.items():
            print(f'{k} components explaining {round((threshold_exp_var.loc[(v-1)].cum_exp_var)*100, 2)}% variance = {v}')
    if return_summary == True:
        summary = pd.DataFrame([validated_thresh, components]).fillna(method='ffill').fillna(method='bfill').drop(labels=[0])
        summary.rename(columns={
                "min": "expvar_min_cutoff",
                "max": "expvar_max_cutoff",
                "Minimum": "min_components",
                "Median": "med_components",
                "Maximum": "max_components"
                }, inplace=True)

    return validated_thresh, components, summary

def optimize_pca(train_scaled, optim_summary, use_default_components=True):
    if use_default_components == False:
        user_input = input("Please enter the number of components to fit:")
        num_components = get_user_defined_num_components(user_input, optim_summary)
    else:
        print("Using Default Number Components for Optimization")
        num_components = int(optim_summary.med_components.values)
    pca_model = PCA(n_components=num_components)
    pca_out = pca_model.fit_transform(train_scaled)
    return pca_model, pca_out

def get_user_defined_num_components(input_prompt, component_summary):
    valid_input = False
    integer = -1
    error_range_msg = "Invalid Value. Please enter a valid whole number."
    error_type_msg = "Invalid Type. Please enter a valid integer."
    while not valid_input:
        user_input = input(input_prompt)
        try:
            integer = int(user_input)
        except ValueError as x:
            print(error_type_msg)
            continue
        if integer > component_summary.min_components and integer < component_summary.max_components:
            valid_input = True
            validated = integer
        else:
            print(error_range_msg)
    return validated

print("STARTING ANALYSIS: PCA")
train_df, test_df = read_analytic_data()

print("FORMATTING DATA")
X_train = train_df.drop(columns=['LABELS']).to_numpy(dtype=float, copy=True)
y_train = train_df['LABELS'].to_numpy(dtype=float, copy=True)
X_test = test_df.to_numpy(dtype=float, copy=True)

print("FITTING PCA")
scaler_train = StandardScaler()
pca_train = PCA(random_state=RANDOM_STATE)
X_train_scaled = scaler_train.fit_transform(X_train)
X_train_pca = pca_train.fit_transform(X_train_scaled)

# 2D scatter plot 2012
train_pca_scatter = generate_2d_pca_scatterplot(X_train_pca)

print("DETERMINE EXPLAINED VARIANCE CUTOFFS")
pca_exp_var = pd.DataFrame(pca_train.explained_variance_ratio_,).reset_index().rename(columns={'index': 'num_components', 0:'exp_var'})
pca_exp_var['num_components'] = pca_exp_var.num_components.apply(lambda x: x+1)
pca_exp_var['cum_exp_var'] = pca_exp_var.exp_var.cumsum()
pca_exp_var['cum_exp_var_pcent'] = pca_exp_var.cum_exp_var * 100

# define explained variance thresholds
# get number of components according to threshold
threshold, number_components, optim_summary = narrow_num_components(return_summary=True, print_components=True)
optim_summary['expvar_min_pcent'] = optim_summary.expvar_min_cutoff * 100
optim_summary['expvar_max_pcent'] = optim_summary.expvar_max_cutoff * 100

# plot optimal number of components
pca_cum_exp = alt.Chart(pca_exp_var).mark_circle(size=60).encode(
            x=alt.X("num_components:Q",
                axis=alt.Axis(title='Number of Components', tickCount=25)),
            y=alt.Y("cum_exp_var_pcent:Q",
                axis=alt.Axis(title="Cumulative Percent Explained Variance"))
        )
min_hline = alt.Chart(optim_summary).mark_rule(color='red').encode(y='expvar_min_pcent')
max_hline = alt.Chart(optim_summary).mark_rule(color='red').encode(y='expvar_max_pcent')
min_vline = alt.Chart(optim_summary).mark_rule(color='blue').encode(x='min_components')
max_vline = alt.Chart(optim_summary).mark_rule(color='blue').encode(x='max_components')
pca_line = (pca_cum_exp + min_hline + max_hline + min_vline + max_vline)
pca_line = pca_line.properties(
            title="Optimal Number of Components"
        ).configure_title(
            fontSize=20,
            font="Courier",
            anchor="start",
            color="gray"
        )
save_alt_chart(pca_line, "PCA_cumulative_expvar.html")

# generate optimal PCA model
print("OPTIMIZING PCA MODEL")
pca_optim, pca_optim_components = optimize_pca(X_train_scaled, optim_summary, use_default_components=True)
save_pca_output(pca_optim_components, ANALYTIC_DATA_PATH+"PCAcomponents_"+ANALYTIC_PATH_ENDPOINTS[2012])

# PCA on 2018 data
X_test_scaled = scaler_train.transform(X_test)
X_test_pca = pca_optim.transform(X_test_scaled)
save_pca_output(X_test_pca, ANALYTIC_DATA_PATH+"PCAcomponents_"+ANALYTIC_PATH_ENDPOINTS[2018])

# 2D Scatter plot 2018
test_pca_scatter = generate_2d_pca_scatterplot(X_test_pca, train=False)

print("PCA ANALYSIS COMPLETE.")