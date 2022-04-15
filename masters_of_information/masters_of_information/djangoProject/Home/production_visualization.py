import pandas as pd

import os
from django.contrib.staticfiles.storage import staticfiles_storage

from django.conf import settings


import json

class ProductionDataVis:


    def __init__(self):



        self.static_url = staticfiles_storage.url('production.json')

        self.base_url = settings.BASE_DIR


    def load_production_json(self):
        with open(self.base_url+self.static_url, 'r') as infile:
            production_json = json.load(infile)
        return json.dumps(production_json)
