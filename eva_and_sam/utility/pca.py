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
FLASK_PLOT_PATH = '../flask/templates'

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

def get_num_components(print_components=True):
    # define user prompts
    user_input_thresh = {
        'min': "Define a minimum explained variance threshold (0 to 1): ",
        'max': "Define a maximum explained variance threshold (0 to 1): "
    }

    # get valid user input (decimal between 0 and 1)
    validated_thresh = {}
    for k,v in user_input_thresh.items():
        validated_thresh[k] = get_user_defined_threshold(v)

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

    return components


print("STARTING ANALYSIS: PCA")
print("READING ANALYTIC DATA")
if os.path.exists(ANALYTIC_DATA_PATH):
    train_df = pd.read_csv(ANALYTIC_DATA_PATH+ANALYTIC_PATH_ENDPOINTS[2012])
    test_df = pd.read_csv(ANALYTIC_DATA_PATH+ANALYTIC_PATH_ENDPOINTS[2018])
else:
    print("FileNotFoundError: Please run utility scripts and try again.")

if os.path.exists(UTIL_PLOT_PATH) == False:
    os.mkdir(UTIL_PLOT_PATH)


print("FORMATTING DATA")
X_train = train_df.drop(columns=['LABELS']).to_numpy(dtype=float, copy=True)
y_train = train_df['LABELS'].to_numpy(dtype=float, copy=True)
X_test = test_df.to_numpy(dtype=float, copy=True)

scaler_train = StandardScaler()
pca_train = PCA(random_state=699)

print("FITTING PCA")
X_train_scaled = scaler_train.fit_transform(X_train)
X_train_pca = pca_train.fit_transform(X_train_scaled)

pca_exp_var = pd.DataFrame(pca_train.explained_variance_ratio_,).reset_index().rename(columns={'index': 'num_components', 0:'exp_var'})
pca_exp_var['num_components'] = pca_exp_var.num_components.apply(lambda x: x+1)
pca_exp_var['cum_exp_var'] = pca_exp_var.exp_var.cumsum()
print('Explained Variance of the first 5 components:')
print(pca_exp_var[:5])

# define explained variance thresholds and get number of components according to threshold
number_components = get_num_components(print_components=True)

# 2D scatter plot
pca_df = pd.DataFrame(pca_train.components_)
new_cols = {}
for col_index in pca_df.columns:
    new_cols[col_index] = "PC"+str(col_index+1)
pca_df.rename(columns=new_cols, inplace=True)

pca_scatter = alt.Chart(pca_df
).mark_circle(size=60
).encode(x="PC1:Q", y="PC2:Q",
).properties(title="2012 Building Characteristics"
).configure_title(fontSize=20, font='Courier', anchor='start', color='gray'
).interactive()

print("WRITING PCA SCATTER PLOT")
if os.path.exists(FLASK_PLOT_PATH) == True:
    pca_scatter.save(FLASK_PLOT_PATH+'PCA_scatter_plot.html')
else:
    pca_scatter.save(UTIL_PLOT_PATH+'PCA_scatter_plot.html')

# TODO: WRITE EXPLAINED VARIANCE PLOT IN ALTAIR
# plt.rcParams["figure.figsize"] = (12,6)

# fig, ax = plt.subplots()
# xi = np.arange(1, 331, step=1)
# y = np.cumsum(pca_train.explained_variance_ratio_)

# plt.ylim(0.0,1.1)
# plt.plot(xi, y, marker='o', linestyle='--', color='b')

# plt.xlabel('Number of Components')
# plt.xticks(np.arange(0, 400, step=50)) #change from 0-based array index to 1-based human-readable label
# plt.ylabel('Cumulative variance (%)')
# plt.title('The number of components needed to explain variance')

# plt.axhline(y=0.80, color='r', linestyle='-')
# plt.text(0.5, 0.85, '80% cut-off threshold', color = 'red', fontsize=16)

# plt.axhline(y=0.95, color='b', linestyle='-')
# plt.text(0.5, 0.97, '95% cut-off threshold', color = 'red', fontsize=16)

# ax.grid(axis='x')
# plt.show()

# TODO: FIT FINAL PCA
pca_final = PCA(n_components=200)
X_train_pca = pca_final.fit_transform(X_train_scaled)

# TODO: SAVE PCA OUTPUT AS CSV
#np.savetxt('Xtrain_PCAcomponents.csv', pca_train.components, delimiter=',')

# TODO: PCA ON 2018 DATA
X_test_scaled = scaler_train.transform(X_test)
X_test_pca = pca_final.transform(X_test_scaled)

# TODO: WRITE 2D SCATTER PLOT IN ALTAIR
# pca_test_df = pd.DataFrame(pca_train.components_)
# sns.set(rc = {'figure.figsize':(5,5)})
# sns.scatterplot(x=pca_test_df.T[0], y=pca_test_df.T[1])

# TODO: SAVE PCA OUTPUT AS CSV
#np.savetxt('Xtrain_PCAcomponents.csv', pca_train.components, delimiter=',')
