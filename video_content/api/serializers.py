from rest_framework import serializers
from video_content.models import Video
from django.core.exceptions import ValidationError

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'category', 'video_file', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

