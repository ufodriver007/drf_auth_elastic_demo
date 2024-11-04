"""
URL configuration for drf_downloader project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include, re_path

from main.views import OAuthCompleteView, ElasticSearchView, SpectacularSwaggerAdminView, SpectacularRedocAdminView, SpectacularAPIAdminView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/complete/vk/', OAuthCompleteView.as_view()),
    path(r'auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    re_path(r'^auth/', include('djoser.urls.jwt')),
    # path(r'auth/', include('djoser.social.urls')),

    # http://127.0.0.1:8000/social-auth/login/vk-oauth2/ login page
    path('social-auth/', include('social_django.urls', namespace='social')),

    path('search/<str:q>', ElasticSearchView.as_view()),

    path('api/schema/', SpectacularAPIAdminView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerAdminView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocAdminView.as_view(url_name='schema'), name='redoc'),

    path('', include('main.urls')),
]
