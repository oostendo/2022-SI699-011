import pandas as pd
import re
import os

YEARS = [2012, 2018]
RAW_CODEBOOK_PATH = 'data/raw_data/cbecs'
PROCESSED_CODEBOOK_PATH = 'data/processed_data/'
codebook_col_map = {
    'CATEOGORIES': 'category',
    'File order': 'file_order',
    'Variable\nname': 'col_name',
    'Variable type': 'col_type',
    'Length': 'length',
    'Format': 'format',
    'Label': 'col_description',
    'Values/Format codes': 'codes',
    'Unnamed: 8': 'empty_col' # (continued in next cell) code prompt?
}

def map_code_values(category_code_list, print_errors=False):
    equal_split = re.compile(r'\s?=\s?')
    cont_num_range = re.compile(r'\d+\s?-\s?\d+')
    code_map = {}
    error_map = {}
    i = 0 # col index
    for code_list in category_code_list:
        # check codes to follow "num = category pattern"
        if 'no code' in code_list:
            code_list = ["no code = continuous numerical value"]
        if bool(cont_num_range.search(code_list[0])) == True:
            # if numerical range is first ie "1 - 10"
            code_list[0] = code_list[0] + " = continuous numerical range"
        elif bool(cont_num_range.search(code_list[-1])) == True:
            # if numerical range is last ie "1946 - 2012"
            code_list[-1] = code_list[-1] + " = continuous numerical range"
        elif 'continued' in code_list[-1]:
            # if (continued in next cell) is last, delete from list
            del code_list[-1]

        # convert codes to dict
        try:
            code_map[i] = dict([re.split(equal_split.pattern, code.replace("'", "").strip()) for code in code_list])
        except ValueError as e:
            error_map[i] = (code_list, e)

        # increment col index
        i += 1
    if print_errors == True:
        for k,v in error_map.items():
            print(f'codelist: {k} | error: {v}\n-----------')
    return code_map

print("STARTING UTILITY: PREPROCESS CODEBOOKS")
if os.path.exists(PROCESSED_CODEBOOK_PATH) == False:
    os.mkdir(PROCESSED_CODEBOOK_PATH)

for year in YEARS:
    print("READING DATA: ", year)
    df_codebook = pd.read_csv(RAW_CODEBOOK_PATH+str(year)+'codebook.csv').rename(columns=codebook_col_map)

    # define mappings and create new dataframes organized by category
    print("DEFINING CODE MAPPINGS:", year)
    categories = df_codebook.category.unique()
    category_map = {}
    category_dfs = {}
    for cat_name in categories:
        if cat_name != 'get rid of':
            category_map[cat_name] = df_codebook[df_codebook['category'] == cat_name].col_name.values
            category_dfs[cat_name] = df_codebook[df_codebook['category'] == cat_name]
    print(category_dfs.keys())
    # only category 10 in year 2012 has missing codes
    if year == 2012:
        category_dfs[10].loc[:,'codes'] = category_dfs[10].codes.fillna('no code')
        category_dfs[10].head()

    # create code mappings for each category
    print("MAPPING CODES ", year)
    all_cats_code_maps = {}
    for cat_num, df in category_dfs.items():
        print(f'category: {cat_num}')
        if cat_num != 'get rid of':
            i = 0
            category_code_df = category_dfs[cat_num].drop(['category', 'file_order', 'col_type', 'length', 'format',], axis=1)
            category_code_df['code_split'] = category_code_df.codes.str.split('\n')
            category_code_list = category_code_df.code_split.values
            category_cols = category_code_df.columns
            category_code_map = map_code_values(category_code_list, print_errors=True)
            for col_name in category_code_df.col_name.values:
                category_code_map[col_name] = category_code_map.pop(i)
                i += 1
            all_cats_code_maps[cat_num] = category_code_map

    # create new codebook dataframe
    print("COMPILING PROCESSED CODEBOOK: ", year)
    new_codes_df = pd.DataFrame(all_cats_code_maps)
    new_codes_df['0'].dropna()

    to_add_dfs = []
    for category_num in new_codes_df.columns:
        to_add = new_codes_df[category_num].dropna().reset_index().rename(
            columns={'index':'col_name', category_num:'codes_dict'})
        to_add_dfs.append(to_add)
    to_merge = pd.concat(to_add_dfs)

    new_codebook = df_codebook.merge(to_merge, on='col_name')

    # write new codebook
    print("WRITING NEW CODEBOOK: ", year)
    new_codebook.to_csv(PROCESSED_CODEBOOK_PATH+'cbecs'+str(year)+'codebook.csv', index=False)