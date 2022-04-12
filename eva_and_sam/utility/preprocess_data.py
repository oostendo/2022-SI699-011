import json
import pandas as pd

YEARS = [2012, 2018]
RAW_DATA_PATH = 'data/raw_data/cbecs'
PROCESSED_DATA_PATH = 'data/processed_data/cbecs'
DATA_PATH_ENDPOINT = 'data.csv'
CODEBOOK_PATH_ENDPOINT = 'codebook.csv'

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

    updated_codebook = create_new_codebook(df_codebook, list(df.columns))
    replace_map = create_replace_map(updated_codebook, df, return_errors=False)
    df_filled = df.replace(to_replace=replace_map, value=0).fillna(value=0)
    #print(f'Data Sample: {year}\n{df_filled[:5].sample(5, random_state=5)}')
    processed_dfs[year] = df_filled

processed_dfs[2012].to_csv(PROCESSED_DATA_PATH+'2012_train_'+DATA_PATH_ENDPOINT, index=False)
processed_dfs[2018].to_csv(PROCESSED_DATA_PATH+'2018_test_'+DATA_PATH_ENDPOINT, index=False)
