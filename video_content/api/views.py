from rest_framework.response import Response
from rest_framework.views import APIView
from video_content.models import Video
from video_content.api.serializers import VideoSerializer
from video_content.signals import video_post_safe
from rest_framework import status
from video_content.tasks import convert_1080p, convert_720p, convert_480p, generate_thunbnail
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes

@api_view(['POST'])
def uploadVideo(self, request, *args, **kwargs):
    serializer = VideoSerializer(data=request.data)
    if serializer.is_valid():
        video = serializer.save()

        convert_480p.delay(video.id)
        convert_720p.delay(video.id)
        convert_1080p.delay(video.id)
        generate_thunbnail.delay(video.id)
        video_post_safe.send(sender=Video, instance=video)
        return Response(serializer.data, status=status.HTTP_201_CREATED)