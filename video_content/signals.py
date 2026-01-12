from .models import Video
from django.db.models.signals import post_save
from django.dispatch import receiver
import django_rq


@receiver(post_save, sender=Video)
def video_post_safe(sender, instance, created, **kwargs):
    """everytime a video is saved, this signal is triggerd """
    if created and instance.video_file:
        print(f"Video {instance.title} has been uploaded")
        from video_content.tasks import convert_1080p, convert_720p, convert_480p, generate_thunbnail, convert_hls
        queue = django_rq.get_queue('default')
        queue.enqueue(convert_480p, instance.id)
        queue.enqueue(convert_720p, instance.id)
        queue.enqueue(convert_1080p, instance.id)
        print(f"Video{instance.id} qued for processing")
