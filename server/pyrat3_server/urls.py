from django.urls import path

from . import views
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^index/$', views.Index.as_view(), name='index'),
    url(r'^client_table/$', views.ClientTable.as_view(), name='client_table'),
    url(r'^generate_command_id/$', views.generate_command_id, name='generate_command_id'),
    path('api/', views.ClientList.as_view(), name='client_list'),
    path('api/<pk>/', views.ClientDetail.as_view(), name='client_details'),
    path('api/<pk>/upload/', csrf_exempt(views.ClientUploadFile.as_view()), name='client_upload_file')
]