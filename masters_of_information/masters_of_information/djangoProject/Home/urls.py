from django.urls import path, reverse_lazy

from . import views


app_name='Home'



urlpatterns = [
    path('', views.index, name='index'),
    path('production', views.production, name='production'),
    path('model', views.model, name='model'),
    # path('home/content', views.AdListView.as_view(), name='content'),
    # path('home/upload', views.AdCreateView.as_view(), name='upload'),
    # path('home/<int:pk>', views.stream_file, name='ad_picture'),
    # path('home/random', views.random, name='random'),
    #path("register", views.register_request, name="register")
]