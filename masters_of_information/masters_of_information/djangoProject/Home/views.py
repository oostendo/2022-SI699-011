# some base packages
from urllib import request
from django.http import HttpResponse
from django.template import loader
from django.views import View


# a short cut

from django.shortcuts import render

from Home.weather_data_visualization import *
from Home.production_visualization import *
from Home.model_visualization import *

def index(request):
    #return HttpResponse("Hello, world. You're at Daiwei's website.")

    tem = WeatherDataVis()
    path = tem.load_path()

    # data frame
    df_all = tem.load_data()

    temperatures_avg = tem.visualize_temp()

    plt_div = tem.plotly_weather_stations()

    plt_div_weather_changes = tem.plotly_weather_change()


    template = loader.get_template('Home/index.html')
    context = {
        'path': tem,
        'df_all': df_all.to_html(),
        'temperatures_avg': temperatures_avg,
        'plt_div': plt_div,
        'plt_div_weather_changes': plt_div_weather_changes,
    }

    return HttpResponse(template.render(context, request))


def production(request):

    tem = ProductionDataVis()

    my_json = tem.load_production_json()



    template = loader.get_template('Home/production.html')
    context = {
        'tem': "Hello World",
        'my_json': my_json,
    }
    return HttpResponse(template.render(context, request))


def model(request):

    tem = ModelDataVis()

    dt_json = tem.load_dt_json()
    lr_json = tem.load_lr_json()



    template = loader.get_template('Home/model.html')
    context = {
        'tem': "Hello World",
        'dt_json': dt_json,
        'lr_json': lr_json,
    }
    return HttpResponse(template.render(context, request))