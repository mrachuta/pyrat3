from . import views
from django.urls import path
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


urlpatterns = [
    # Require authentication in elegant-way
    url(r'^index/$', login_required(views.Index.as_view()), name='index'),
    url(r'^client_table/$', login_required(views.ClientTable.as_view()), name='client_table'),
    url(r'^generate_job_id/$', views.generate_job_id, name='generate_job_id'),
    path('client_files/<pk>/', login_required(views.client_files), name='client_files'),
    path('api/', views.ClientList.as_view(), name='client_list'),
    path('api/<pk>/', views.ClientDetail.as_view(), name='client_details'),
    # Exclude CSRF from this form in elegant-way
    path('api/<pk>/upload/', csrf_exempt(views.ClientUploadFile.as_view()), name='client_upload_file')
]