from rest_framework import serializers
from video_content.models import Video
from django.core.exceptions import ValidationError

class VideoSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url' ,'category',   ]
        read_only_fields = ['status', 'created_at']

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
        return None




