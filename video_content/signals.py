from .models import Video
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Video)
def video_post_safe(sender, instance, created, **kwargs):
    if created:
        print(f'New video uploaded: {instance.title}')