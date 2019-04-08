from django.urls import path

from . import views
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url('index', views.Index.as_view(), name='index'),
    url('register', views.register, name='register'),
    url(r'^(?P<pc_uuid>[\w-]+)/job$', views.job, name='job'),
    url(r'^(?P<pc_uuid>[\w-]+)/result$', views.result, name='result'),
    path('api/', views.ClientList.as_view(), name='client_list'),
    path('api/<pc_uuid>/', views.ClientDetail.as_view(), name='client_details'),
    path('api/<pc_uuid>/upload', csrf_exempt(views.ClientUploadFile.as_view()), name='client_upload_file')
]