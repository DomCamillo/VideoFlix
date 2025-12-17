from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta



class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']



class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        expiry_time  = self.created_at + timedelta(hours=24)
        return timezone.now() < expiry_time

    class Meta:
        ordering = ['created_at']