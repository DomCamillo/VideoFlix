from rest_framework.response import Response
from rest_framework.views import APIView
from video_content.models import Video
from video_content.api.serializers import VideoSerializer
from video_content.signals import video_post_safe
from rest_framework import status

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
def get_video(request):
    videos = Video.objects.all()
    serializer = VideoSerializer(videos, many=True)
    return Response(serializer.data)



def get_index(request, movie_id, resolution):
    pass



def get_segment(request, movie_id, resolution, segment):
    pass