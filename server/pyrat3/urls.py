"""pyrat3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', lambda request: redirect('pyrgui/', permanent=False)),
    path('pyrgui/', include('pyrgui.urls')),
    path('pyrserver/', include('pyrserver.urls')),
    path('admin/', admin.site.urls),
    url(r'^accounts/login/$',
        auth_views.LoginView.as_view(
            template_name="registration/login.html"), name="login"
        ),
    url(r'^accounts/logout/$',
        auth_views.LogoutView.as_view(
            template_name="registration/logged_out.html"), name="logout"
        ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
