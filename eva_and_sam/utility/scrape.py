import warnings
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

warnings.filterwarnings("ignore")

BASE_URL = 'https://www.eia.gov/consumption/commercial/data/'
YEAR_URL_ENDPOINTS = {2012:'2012/', 2018:'2018/'}
TAB_ENDPOINT = 'index.php?view='
tabs = ['characteristcs', 'consumption', 'microdata', 'methodology']
data_path = 'data/'
html_path = data_path+'html/'

if os.path.exists(data_path) == False:
    os.mkdir(data_path)
if os.path.exists(html_path) == False:
    os.mkdir(html_path)

def collect_cbecs_microdata(soup):
    results = soup.find("div", id=tabs[2])
    csv_element = results.find("a", class_='ico_csv')
    csv_download = csv_element["href"].strip('../')

    #print(f'csv_element: {csv_element}')
    #print(f'csv_download: {csv_download}')
    #print(f'download url: {BASE_URL+csv_download}')

    data_df = pd.read_csv(BASE_URL+csv_download)

    xls_elements = results.find_all("a", class_="ico_xls")
    for xls in xls_elements:
        if "codebook" in xls["href"]:
            codebook_download = xls["href"].strip('../')

            # print(f'codebook xls: {xls}')
            # print(f'xls_download: {codebook_download}')
            # print(f'download url: {BASE_URL+codebook_download}')

            codebook_df = pd.read_excel(BASE_URL+codebook_download)
    return data_df, codebook_df


print("STARTING UTILITY: SCRAPE")

soup2012 = None
soup2018 = None
for year in YEAR_URL_ENDPOINTS.keys():
    path = html_path+'cbecs'+str(year)+'.html'
    if os.path.exists(path):
        print("USING CACHE")
        with open(path, "r", encoding='utf-8') as file:
            if year == 2012:
                soup2012 = BeautifulSoup(file.read(), "html.parser")
            elif year == 2018:
                soup2018 = BeautifulSoup(file.read(), 'html.parser')
    else:
        print("REQUESTING URL")
        response = requests.get(BASE_URL+YEAR_URL_ENDPOINTS[year]+TAB_ENDPOINT+tabs[2])
        with open(path, "w", encoding='utf-8') as file:
            file.write(response.text)
            if year == 2012:
                soup2012 = BeautifulSoup(response.content, "html.parser")
            elif year == 2018:
                soup2018 = BeautifulSoup(response.content, "html.parser")

print("COLLECTING DATA")
data_dfs = {}
codebook_dfs = {}
for year in YEAR_URL_ENDPOINTS.keys():
    if year == 2012:
        data_dfs[year], codebook_dfs[year] = collect_cbecs_microdata(soup2012)
    elif year == 2018:
        data_dfs[year], codebook_dfs[year] = collect_cbecs_microdata(soup2018)

print("WRITING DATA")
for year in data_dfs.keys():
    path = data_path+'raw_data/'+'cbecs'+str(year)
    data_dfs[year].to_csv(path+'data.csv', index=False)
    codebook_dfs[year].to_csv(path+'codebook.csv', index=False)