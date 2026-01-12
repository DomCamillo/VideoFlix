from .models import Video
from django.db.models.signals import post_save
from django.dispatch import receiver
import django_rq


@receiver(post_save, sender=Video)
def video_post_safe(sender, instance, created, **kwargs):
    """everytime a video is saved this signal is triggerd """
    if created and instance.video_file:
        print(f"Video {instance.title} has been uploaded")
        from video_content.tasks import process_video
        queue = django_rq.get_queue('default')
        queue.enqueue(process_video, instance.id)
        print(f"video {instance.id} {instance.title} has been queued for processing")

