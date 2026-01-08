from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail_url = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    video_file = models.FileField(upload_to='videos/')
    status = models.CharField(max_length=20, default='pending', choices=[

        ('pending', 'pending'),
        ('processing', 'processing'),
        ('completed', 'completed'),
        ('failed', 'failed'),
    ])

    hls_480p_path = models.CharField(max_length=500, blank=True, null=True)
    hls_720p_path = models.CharField(max_length=500, blank=True, null=True)
    hls_1080p_path = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        ordering =['-category']

    def __str__(self):
        return f" title: {self.title}, category: {self.category} "