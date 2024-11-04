from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from .views import MyAPIView, UploadView, UploadResultView


urlpatterns = [
    path('', MyAPIView.as_view()),
    path('upload/', UploadView.as_view()),
    path('result/', UploadResultView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
