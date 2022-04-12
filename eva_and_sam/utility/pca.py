import os
import pandas as pd
import numpy as np

YEARS = [2012, 2018]
PROCESSED_DATA_PATH = 'data/processed_data/cbecs'
DATA_PATH_ENDPOINT = 'data.csv'
ANALYTIC_DATA_PATH = 'data/analytic_data/'
ANALYTIC_PATH_ENDPOINTS = {2012: 'train.csv', 2018: 'test.csv'}

if os.path.exists(ANALYTIC_DATA_PATH) == False:
    os.mkdir(ANALYTIC_DATA_PATH)

data_dfs = {}
for year in YEARS:
    if year == 2012:
        df_data = pd.read_csv(PROCESSED_DATA_PATH+str(year)+'_train_'+DATA_PATH_ENDPOINT)
        data_dfs[year] = df_data
    else:
        df_data = pd.read_csv(PROCESSED_DATA_PATH+str(year)+'_test_'+DATA_PATH_ENDPOINT)
        data_dfs[year] = df_data

colset2012 = set(data_dfs[2012].columns)
colset2018 = set(data_dfs[2018].columns)
union = colset2012 | colset2018
intersection = colset2012 & colset2018
difference = colset2012 - colset2018
symmetric_difference = colset2012 ^ colset2018
print("Union :", len(union))
print("Intersection :", len(intersection))
print("Difference :", len(difference))
print("Symmetric difference :", len(symmetric_difference))