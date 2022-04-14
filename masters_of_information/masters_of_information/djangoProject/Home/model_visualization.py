import pandas as pd

import os
from django.contrib.staticfiles.storage import staticfiles_storage

from django.conf import settings


import json

class ModelDataVis:


    def __init__(self):



        self.static_url = staticfiles_storage.url('dt_mae_chart.json')
        self.static_url2 = staticfiles_storage.url('lr_mae_chart.json')
        self.base_url = settings.BASE_DIR


    def load_dt_json(self):
        with open(self.base_url+self.static_url, 'r') as infile:
            dt_json = json.load(infile)
        return json.dumps(dt_json)


    def load_lr_json(self):
        with open(self.base_url+self.static_url2, 'r') as infile:
            lr_json = json.load(infile)
        return json.dumps(lr_json)