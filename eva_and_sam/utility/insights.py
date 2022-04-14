import os
import pandas as pd
import numpy as np
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
import scipy
import statsmodels.formula.api as smf
from scipy.stats import ttest_ind

UTIL_PLOT_PATH = 'data/plots/'
FLASK_PLOT_PATH = '../flask/templates/plots/'
FLASK_TABLE_PATH = '../flask/templates/tables/'

def save_alt_chart(alt_chart, chart_path):
    if os.path.exists(UTIL_PLOT_PATH) == False:
        os.mkdir(UTIL_PLOT_PATH)
    if os.path.exists(FLASK_PLOT_PATH) == True:
        alt_chart.save(FLASK_PLOT_PATH+chart_path)
        print("Saved Chart in Web App Directory")
    else:
        alt_chart.save(UTIL_PLOT_PATH+chart_path)
        print("Saved Chart in Utility Directory")

print("GENERATING INSIGHTS")
df_2018 = pd.read_csv('data/predictions/df_2018_predictions.csv')

## Filtered for Outliers
df_2018.loc[df_2018.predicted > df_2018.predicted.quantile(0.95), "outlier"] = 1
df_2018.loc[df_2018.predicted < df_2018.predicted.quantile(0.05), "outlier"] = 1

df_2018 = df_2018.drop(df_2018[df_2018.outlier == 1].index)
df_2018.reset_index(drop=True, inplace=True)

df_2018["eui"] = df_2018['predicted'] / df_2018["SQFT"]

## Highest median energy use intensity by Principal Building Activity
# PBA 15 = Food Service
food_df = df_2018.groupby("PBA").median().sort_values('eui', ascending=False)
print(food_df.columns)
food_df = food_df[['predicted', 'eui']].copy()
print(bool('PBA' in food_df.columns))
food_df.to_html(FLASK_TABLE_PATH+'food_service_median_eui.html', index=False, col_space='30px')

df_food_service = df_2018[(df_2018.PBA == 15)]
df_food_service.drop(df_food_service[df_food_service.predicted < -50].index, inplace=True) # without outlier

# water boost
boost = df_food_service[df_food_service["BOOSTWT"] == 1]
no_boost = df_food_service[df_food_service["BOOSTWT" ] == 2]
boost_df = pd.concat([boost, no_boost])

boost_boxplot = alt.Chart(boost_df).mark_boxplot(extent='min-max'
).encode(
    y='BOOSTWT:N',
    x=alt.X('eui:Q', axis=alt.Axis(title='Energy Use Intensity')),
).properties(title="Buildings With (1), or Without (2), Water Heater Booster"
        ).configure_title(fontSize=20, font='Courier', anchor='start', color='gray'
        )
save_alt_chart(boost_boxplot, 'boost_boxplot.html')

sns_boxplot= sns.boxplot(data=df_food_service, x='BOOSTWT', y='eui').set(title='Distirbuiton of Water Heater Boosters')
plt.savefig(FLASK_PLOT_PATH+'seaborn_boxplot_eui_boost.png')

ttest_result = ttest_ind(boost["eui"],no_boost["eui"])
print(f'One Sample T-Test Results: {ttest_result}')
model = smf.ols("eui ~ BOOSTWT", data = df_food_service)
results = model.fit()
summary = results.summary()
print(summary)
html_summary = summary.as_html()
f = open(FLASK_TABLE_PATH+"ols_html_summary.html", "w")
f.write(html_summary)
f.close()
print("ANALYTIC PIPELINE COMPLETE")