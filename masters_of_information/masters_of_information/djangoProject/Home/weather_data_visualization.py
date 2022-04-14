import pandas as pd

import os
from django.contrib.staticfiles.storage import staticfiles_storage

from django.conf import settings

import plotly.graph_objects as go
import json

from plotly.offline import plot




class WeatherDataVis:

    def __init__(self):
        pass



    def load_path(self):
        """
        Load csv file from the local file
        :return: [(path, directions, csv files)]
        """

        static_url = staticfiles_storage.url('Home/weather_data')

        base_url = settings.BASE_DIR

        urls = []
        for root, dirs, files in os.walk(base_url+static_url):

            urls.append((root, dirs, files))

        return urls



    def load_data(self):
        urls = self.load_path()
        files = urls[-1][-1]
        base_url = urls[-1][0]

        df_all = pd.DataFrame()
        for i in files:
            df_all = pd.concat([pd.read_csv(base_url+'/'+i), df_all], join='outer')
        df_all = df_all.groupby(by='DATE').mean().drop(columns=['PSUN', 'TSUN'], index=[2021, 2022])

        pd.options.display.max_columns = None
        df_all = df_all.dropna(axis='columns', how='any')


        return df_all


    def visualize_temp(self):

        df_all = self.load_data()
        temperatures_df = df_all[['TMAX', 'TMIN', 'TAVG']]
        temperatures_df = temperatures_df.reset_index()


        fig = go.Figure()
        fig.add_trace(go.Scatter(x=temperatures_df['DATE'], y=temperatures_df['TMAX'],
                                 mode='lines+markers',
                                 name='TMAX'))
        fig.add_trace(go.Scatter(x=temperatures_df['DATE'], y=temperatures_df['TMIN'],
                                 mode='lines+markers',
                                 name='TMIN'))
        fig.add_trace(go.Scatter(x=temperatures_df['DATE'], y=temperatures_df['TAVG'],
                                 mode='lines+markers', name='TAVG'))

        


        return fig

    def show_avg_yearly(self):
        """
        Show avg yearly data for michigan
        :return:
        """




        return None

    def plotly_weather_stations(self):
        """

        :return:
        """
        static_url = staticfiles_storage.url('geo_json_data.json')

        base_url = settings.BASE_DIR




        static_url_weather = staticfiles_storage.url('Home/weather_data')



        df3 = pd.read_csv(base_url+static_url_weather+'/2021_2022.csv')
        locations = df3['NAME'].unique()
        locations









        with open(base_url+static_url, 'r') as infile:
            result_list = json.load(infile)


        loc = {"address": locations, "lat": [i[0]['geometry']['location']['lat'] for i in result_list],
               "lng": [i[0]['geometry']['location']['lng'] for i in result_list]}
        location_df = pd.DataFrame(data=loc)
        location_df['text'] = location_df['address'] + '' + str(location_df['lat']) + ', ' + str(
            location_df['lng']) + ''

        fig = go.Figure(data=go.Scattergeo(
            lon=location_df['lng'],
            lat=location_df['lat'],
            text=location_df['text'],
            mode='markers',
        ))

        fig.update_layout(
            title='Locations',
            geo_scope='usa',
        )

        # https://plotly.com/python/renderers/
        plt_div = plot(fig, output_type='div')

        return plt_div

    def plotly_weather_change(self):

        from plotly.subplots import make_subplots

        df_all = self.load_data()

        fig = make_subplots(rows=6, cols=6, subplot_titles=(df_all.columns))

        temperatures_df = df_all[['TMAX', 'TMIN', 'TAVG']]
        temperatures_df = temperatures_df.reset_index()



        for index, i in enumerate(df_all.columns):
            # print(index, index//5, index%5)




            fig.add_trace(
                go.Scatter(x=temperatures_df['DATE'], y=df_all[i], name=i),
                row=index // 6 + 1, col=index % 6 + 1
            )
        fig.update_layout(height=1600, width=1800, title_text="Side By Side Subplots")

        plt_div = plot(fig, output_type='div')

        return plt_div