from . import views
from django.urls import path, re_path
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


urlpatterns = [
    # Require authentication in elegant-way
    path(r'', lambda request: redirect('index/', permanent=False)),
    re_path(r'^index/$', login_required(views.Index.as_view()), name='index'),
    re_path(r'^client_table/$', login_required(views.ClientTable.as_view()), name='client_table'),
    path('client_files/<pk>/', login_required(views.client_files), name='client_files'),
]