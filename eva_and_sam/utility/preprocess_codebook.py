import pandas as pd
import numpy as np
import re
import os
import json

YEARS = [2012, 2018]
RAW_CODEBOOK_PATH = 'data/raw_data/cbecs'
PROCESSED_CODEBOOK_PATH = 'data/processed_data/'
vars_to_drop = re.compile(r"^Z\w+|^FINAL\w+|MFBTU|MFEXP|ELCNS|ELBTU|ELEXP|NGCNS|NGBTU|NGEXP|FKCNS|FKBTU|FKEXP|DHCNS|DHBTU|DHEXP|DRVTHRU")
codebook_col_map = {
    'CATEOGORIES': 'category',
    'File order': 'file_order',
    'Variable\nname': 'col_name',
    'Variable type': 'col_type',
    'Length': 'length',
    'Len-\ngth': 'length',
    'Format': 'format',
    'Label': 'col_description',
    'Values/Format codes': 'codes',
    'Unnamed: 8': 'empty_col' # (continued in next cell) code prompt?
}

def map_code_values(code_list, print_errors=False):
    equal_split = re.compile(r'\s?=\s?')
    cont_num_range = re.compile(r'\d+\s?-\s?\d+|\d+\,?\s?-\s?\d+\,?\d+')
    code_equals = re.compile(r'\d+=')

    code_map = {}
    error_map = {}

    i = 0 # col index
    col_codes = []
    for codes in code_list:
        if type(codes) != list:
            if type(codes) == float:
                codes = ['missing']
            else:
                codes = [codes]
        for code in codes:
            # check codes to follow "num = category pattern"
            if bool(cont_num_range.search(code)) == True:
                # check codes with continuous numerical ranges i.e. 6 - 12,000 or 1 - 10
                if bool(code_equals.search(code)) == False:
                    # check to make sure the range is not attached to a code i.e. 4=10-20% or 1=10,000 - 20,000 square feet
                    code = code + " = continuous numerical range"
                    col_codes.append(code)
                else:
                    col_codes.append(code)
            elif bool(code_equals.search(code)) == True:
                # resolve human error in codebook codes i.e. 32=Fast food 33=Restaurant/cafeteria instead of 32=Fast food\n33=Restaurant/cafeteria
                # or 4=Aluminum, asbestos, plastic, or wood materials (siding, shingles, tiles,5=Sheet metal panels instead of 4=Aluminum, asbestos, plastic, or wood materials (siding, shingles, tiles)'\n5=Sheet metal panels
                all_equals = code_equals.findall(code)
                if len(all_equals) > 1:
                    split_code = re.split(code_equals.pattern, code)[1:]
                    ci = 0
                    for new_code in split_code:
                        updated_code = all_equals[ci] + new_code
                        col_codes.append(updated_code)
                        ci += 1
                else:
                    col_codes.append(code)
            elif 'missing' in code:
                code = ["no code = continuous numerical value"]
                col_codes.append(code)
            elif 'continued' in code:
                # if (continued in next cell) is last, exclude from col_codes
                pass
            else:
                col_codes.append(code)


        # convert codes to dict
        code_dict = {}
        for code in col_codes:
            try:
                # combine each code dict as list for each col
                if type(code) == list:
                    for inst in code:
                        split_dict = dict([re.split(equal_split.pattern, inst.replace("'", "").strip())])
                        for k, v in split_dict.items():
                            code_dict[k] = v.strip('"')
                else:
                    split_dict = dict([re.split(equal_split.pattern, code.replace("'", "").strip())])
                    for k, v in split_dict.items():
                        code_dict[k] = v.strip('"')
            except ValueError as e:
                error_map[i] = (code, e)

        code_map[i] = code_dict
        i += 1

    if print_errors == True:
        for k,v in error_map.items():
            print(f'codelist: {k} | error: {v}\n-----------')
    return code_map

print("STARTING UTILITY: PREPROCESS CODEBOOKS")
if os.path.exists(PROCESSED_CODEBOOK_PATH) == False:
    os.mkdir(PROCESSED_CODEBOOK_PATH)

for year in YEARS:
    print("READING DATA:", year)
    df_codebook = pd.read_csv(RAW_CODEBOOK_PATH+str(year)+'codebook.csv').rename(columns=codebook_col_map)
    #print(f'codebook cols before drop = {len(df_codebook.col_name)}')
    df_codebook_filtered = df_codebook[df_codebook['col_name'].str.contains(vars_to_drop.pattern) == False]
    #print(f'codebook cols after drop = {len(df_codebook_filtered.col_name)}')

    print("MAPPING CODES", year)
    if year == 2018:
        code_df = df_codebook_filtered.drop(['file_order', 'col_type', 'length'], axis=1)
    else:
        code_df = df_codebook_filtered.drop(['file_order', 'col_type', 'length', 'format'], axis=1)
    code_df['code_split'] = code_df.codes.str.split('\n')
    code_list = code_df.code_split.values
    code_map = map_code_values(code_list, print_errors=True)
    #print('number of cols in code map:,',len(code_map))
    index = 0
    for col_name in code_df.col_name.values:
        code_map[col_name] = code_map.pop(index)
        index += 1

    print("GENERATING NEW CODEBOOK:", year)
    code_map_df = pd.DataFrame(columns=['col_name', 'code_map'])
    code_map_df['col_name'] = code_map.keys()
    code_map_df['code_map'] = code_map.values()
    new_codebook = df_codebook.merge(code_map_df, how='inner', on='col_name')

    print("WRITING NEW CODEBOOK FILES:", year)
    new_codebook.to_csv(PROCESSED_CODEBOOK_PATH+'cbecs'+str(year)+'codebook.csv',index=False)
    with open(PROCESSED_CODEBOOK_PATH+'cbecs'+str(year)+'codebook.json', 'w') as f:
        json.dump(code_map, f)