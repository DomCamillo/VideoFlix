from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True,)
    category = models.CharField(max_length=50, blank=True, default='Comedy', choices=[
        ('Drama', 'Drama'),
        ('Comedy', 'Comedy'),
        ('Documentary', 'Documentary'),
        ('Action', 'Action'),
        ('Horror', 'Horror'),
        ('Romance', 'Romance'),
        ('Sci-Fi', 'Sci-Fi'),
        ('Thriller', 'Thriller'),
        ('Animation', 'Animation'),
        ('Fantasy', 'Fantasy'),
        ('Crime', 'Crime'),
        ('Family', 'Family'),
    ] )
    video_file = models.FileField(upload_to='videos/')
    status = models.CharField(max_length=20, default='pending', choices=[

        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])

    hls_480p_path = models.CharField(max_length=500, blank=True, null=True)
    hls_720p_path = models.CharField(max_length=500, blank=True, null=True)
    hls_1080p_path = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        ordering =['-created_at']

    def __str__(self):
        return f" title: {self.title}, category: {self.category} "



