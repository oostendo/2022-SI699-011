import os
import json
import pandas as pd
import numpy

YEARS = [2012, 2018]
RAW_DATA_PATH = 'data/raw_data/cbecs'
PROCESSED_DATA_PATH = 'data/processed_data/cbecs'
DATA_PATH_ENDPOINT = 'data.csv'
CODEBOOK_PATH_ENDPOINT = 'codebook.csv'

ANALYTIC_DATA_PATH = 'data/analytic_data/'
ANALYTIC_PATH_ENDPOINTS = {2012: 'train.csv', 2018: 'test.csv', 'Y': 'y_train.csv'}
consumption2012vars = [
    'MFHTBTU',
    'MFCLBTU',
    'MFVNBTU',
    'MFWTBTU',
    'MFLTBTU',
    'MFCKBTU',
    'MFRFBTU',
    'MFOFBTU',
    'MFPCBTU',
    'MFOTBTU',
    'ELHTBTU',
    'ELCLBTU',
    'ELVNBTU',
    'ELWTBTU',
    'ELLTBTU',
    'ELCKBTU',
    'ELRFBTU',
    'ELOFBTU',
    'ELPCBTU',
    'ELOTBTU',
    'NGHTBTU',
    'NGCLBTU',
    'NGWTBTU',
    'NGCKBTU',
    'NGOTBTU',
    'FKHTBTU',
    'FKCLBTU',
    'FKWTBTU',
    'FKCKBTU',
    'FKOTBTU',
    'DHHTBTU',
    'DHCLBTU',
    'DHWTBTU',
    'DHCKBTU',
    'DHOTBTU'
    ]

def find_num_cat_cols(df, category_num, list_of_numcols, list_of_catcols):
    numeric_cols = []
    categorical_cols = []
    for col in df.columns:
        if col in list_of_numcols:
            numeric_cols.append(col)
        elif col in list_of_catcols:
            categorical_cols.append(col)
    new_df = df[category_num].copy()[numeric_cols + categorical_cols]
    return new_df, numeric_cols, categorical_cols

def create_new_codebook(codebook, cols):
    new_codebook = dict(codebook.set_index('col_name').loc[cols].code_map)
    return new_codebook

def create_replace_map(new_codebook, category_df, return_errors=False):
    # creates a mapping to facilitate a pandas replace function
    replace_map = {}
    error_map = {}
    for col_name, codebook in new_codebook.items():
        try:
            codebook = json.loads(codebook.replace("'", '"'))
        except ValueError as e:
            #print(f'JSONDecodeError on column {col_name}')
            error_map[col_name] = (col_name, e)
            codebook = codebook.replace('"', '')
            codebook = json.loads(codebook.replace("'", '"'))
            #print('Error Resolved')
        finally:
            if col_name in category_df.columns:
                for code, code_val in codebook.items():
                    if code == '2' and code_val == 'No':
                        replace_map[col_name] = 2

    if return_errors == True:
        return replace_map, error_map
    else:
        return replace_map

print("STARTING UTILITY: PREPROCESS DATA")
processed_dfs = {}
for year in YEARS:
    df_data = pd.read_csv(RAW_DATA_PATH+str(year)+DATA_PATH_ENDPOINT)
    df_codebook = pd.read_csv(PROCESSED_DATA_PATH+str(year)+CODEBOOK_PATH_ENDPOINT)
    df = df_data[df_codebook.col_name.values].copy()

    print("MANIPULATING DATA:", year)
    # Adjusting for weird values
    df.NFLOOR.replace(to_replace=994, value=20, inplace=True)
    df.NFLOOR.replace(to_replace=995, value=26, inplace=True)
    df.FLCEILHT.replace(to_replace=995, value=51, inplace=True)
    df.NELVTR.replace(to_replace=995, value=51, inplace=True)
    df.NESLTR.replace(to_replace=995, value=21, inplace=True)
    df.RWSEAT.replace(to_replace=99995, value=15001, inplace=True)
    df.PBSEAT.replace(to_replace=999995, value=15001, inplace=True)
    df.HCBED.replace(to_replace=9995, value=251, inplace=True)
    df.NRSBED.replace(to_replace=9995, value=251, inplace=True)
    df.LODGRM.replace(to_replace=99995, value=901, inplace=True)
    df.NOCC.replace(to_replace=995, value=201, inplace=True)
    df.WOEXP.replace(to_replace=999999, value=None, inplace=True)
    df.XRAYN.replace(to_replace=995, value=21, inplace=True)
    df.RFGCOMPN.replace(to_replace=99995, value=1001, inplace=True)
    df.TVVIDEON.replace(to_replace=995, value=201, inplace=True)

    # adjust weird values that are year specific
    if year == 2012:
        df.YRCON.replace(to_replace=995, value=1945, inplace=True)
        df.ELLUPCT.replace(to_replace=999, value=None, inplace=True)

    # force data type
    if year == 2018:
        df_filled = df.fillna(value=0).replace(to_replace='.', value="0")
    else:
        df_filled = df.fillna(value=0)
    objects = list(df_filled.select_dtypes(['object']).columns)
    for col in objects:
        df_filled[col] = df_filled[col].astype(str).astype(int)

    updated_codebook = create_new_codebook(df_codebook, list(df_filled.columns))
    replace_map = create_replace_map(updated_codebook, df_filled, return_errors=False)
    df_filled = df_filled.replace(to_replace=replace_map, value=0)
    processed_dfs[year] = df_filled

print("WRITING PROCESSED DATA")
processed_dfs[2012].to_csv(PROCESSED_DATA_PATH+str(YEARS[0])+DATA_PATH_ENDPOINT, index=False)
processed_dfs[2018].to_csv(PROCESSED_DATA_PATH+str(YEARS[1])+DATA_PATH_ENDPOINT, index=False)

if os.path.exists(ANALYTIC_DATA_PATH) == False:
    print("CREATING ANALYTIC DATA")
    os.mkdir(ANALYTIC_DATA_PATH)
    colset2012 = set(processed_dfs[2012].columns)
    colset2018 = set(processed_dfs[2018].columns)
    intersection = colset2012 & colset2018
    difference = colset2012 - colset2018
    print("Column intersection of 2012 and 2018 data:", len(intersection))
    print("Column difference of 2012 and 2018 data:", len(difference))

    x_train_df = processed_dfs[2012][list(intersection)].copy()
    y_train_df = processed_dfs[2012][consumption2012vars].copy()
    y_train_df['SUM'] = y_train_df.sum(axis=1)
    train_df = pd.concat([x_train_df, y_train_df['SUM']], axis=1).rename(columns={'SUM': 'LABELS'})
    test_df = processed_dfs[2018][list(intersection)].copy()

    print("WRITING ANALYTIC DATA")
    x_train_df.to_csv(ANALYTIC_DATA_PATH+'X_'+ANALYTIC_PATH_ENDPOINTS[2012])
    y_train_df.to_csv(ANALYTIC_DATA_PATH+ANALYTIC_PATH_ENDPOINTS['Y'])
    train_df.to_csv(ANALYTIC_DATA_PATH+ANALYTIC_PATH_ENDPOINTS[2012], index=False)
    test_df.to_csv(ANALYTIC_DATA_PATH+ANALYTIC_PATH_ENDPOINTS[2018], index=False)

else:
    print("ANALYTIC DATA ALREADY EXISTS")