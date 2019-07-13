from . import views
from django.urls import path
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^generate_job_id/$', views.generate_job_id, name='generate_job_id'),
    # Require authentication in elegant-way
    path('api/', views.ClientList.as_view(), name='client_list'),
    path('api/<pk>/', views.ClientDetail.as_view(), name='client_details'),
    # Exclude CSRF from this form in elegant-way
    path('api/<pk>/upload/', csrf_exempt(views.ClientUploadFile.as_view()), name='client_upload_file')
]