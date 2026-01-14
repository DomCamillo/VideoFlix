from rest_framework import serializers
from video_content.models import Video
from django.core.exceptions import ValidationError

class VideoSerializer(serializers.ModelSerializer):
    thumpnail_url = serializers.SerializerMethodField()
    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumpnail_url' ,'category',   ]
        read_only_fields = ['status', 'created_at']

    def get_thumpnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
        return None

class HLSMasterPlaylistSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    resolution = serializers.CharField(max_length=10)

    def validate_movie_id(self, value):
        if not Video.objects.filter(id=value).exists():
            raise ValidationError("Video with this ID does not exist.")
        return value


class HLSVideoSegmentSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    resolution = serializers.CharField(max_length=10)
    segment = serializers.CharField(max_length=100)

    def validate_movie_id(self, value):
        if not Video.objects.filter(id=value).exists():
            raise ValidationError("Video with this ID does not exist.")
        return value
    def validate_segment(self, value):
        if not value.endswith('.ts'):
            raise ValidationError("Segment must be a .ts file.")
        return value
