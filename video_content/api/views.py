from rest_framework.response import Response
import os
from django.conf import settings
from django.http import FileResponse, HttpResponse
from video_content.models import Video
from video_content.api.serializers import VideoSerializer
from video_content.signals import video_post_safe
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_video(request):
    """GET /api/video/ - List of all Videos"""
    videos = Video.objects.filter(status='completed')
    serializer = VideoSerializer(videos, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_HLSMasterPlaylist(request, movie_id, resolution):
    """GET /api/video/<movie_id>/<resolution>/index.m3u8
    Return the M3U8-Playlist file """
    video = get_object_or_404(Video, id=movie_id, status='completed')
    file_path = os.path.join(settings.MEDIA_ROOT,'videos','hls', str(movie_id), resolution, 'index.m3u8')

    if not os.path.exists(file_path):
        return Response({'error': 'Playlist not found'}, status=404)

    """open and read the m3u8 file and return its content"""
    with open(file_path, 'r' ) as file:
        content = file.read()
    return HttpResponse(content, content_type='application/vnd.apple.mpegurl')



@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_HLSVideoSegment(request, movie_id, resolution, segment):
    """ GET /api/video/<movie_id>/<resolution>/<segment>/
    Gets the video segments (.ts-Data)"""
    video = get_object_or_404(Video, id=movie_id)
    file_path = os.path.join(settings.MEDIA_ROOT,'videos','hls', str(movie_id), resolution, segment)

    if not os.path.exists(file_path):
        return Response({'error': 'Segment'}, status=404)
    """open and return the .ts file as FileResponse 'rb' for reading binary data"""
    return FileResponse(open(file_path, 'rb'), content_type='video/MP2T')
