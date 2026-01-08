from django.db import models

# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering =['-category']

    def __str__(self):
        return f" title: {self.title}, category: {self.category} "