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

print("STARTING UTILITY: SCRAPE")

cbecs_soup = {}
for year in YEAR_URL_ENDPOINTS.keys():
    path = html_path+'cbecs'+str(year)+'.html'
    if os.path.exists(path):
        print("USING CACHE")
        with open(path, "r", encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), "html.parser")
            cbecs_soup[year] = soup
    else:
        print("REQUESTING URL")
        response = requests.get(BASE_URL+YEAR_URL_ENDPOINTS[year]+TAB_ENDPOINT+tabs[2])
        with open(path, "w", encoding='utf-8') as file:
            file.write(response.text)
            soup = BeautifulSoup(response.content, "html.parser")
            cbecs_soup[year] = soup

print("COLLECTING DATA")
data_dfs = {}
codebook_dfs = {}
for year in cbecs_soup.keys():
    results = soup.find(id=tabs[2])
    csv_element = results.find("a", class_='ico_csv')
    csv_download = csv_element["href"].strip('..')
    data_df = pd.read_csv(BASE_URL+csv_download)
    data_dfs[year] = data_df

    xls_elements = results.find_all("a", class_="ico_xls")
    for xls in xls_elements:
        if "codebook" in xls["href"]:
            codebook_download = xls["href"].strip('..')
            codebook_df = pd.read_excel(BASE_URL+codebook_download)
            codebook_dfs[year] = codebook_df

print("WRITING DATA")
for year in data_dfs.keys():
    path = data_path+'raw_data/'+'cbecs'+str(year)
    data_dfs[year].to_csv(path+'data.csv', index=False)
    codebook_dfs[year].to_csv(path+'codebook.csv', index=False)