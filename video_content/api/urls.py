from django.urls import path, include
from . import views

urlpatterns = [
    path('upload/video/', views.uploadVideo, name='upload-video'),
]
