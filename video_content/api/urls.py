from django.urls import path, include
from . import views

urlpatterns = [
    path('video/', views.get_video, name='get-video'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', views.get_index, name='get-index-m3u8'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', views.get_segment, name='get-segment'),

]
