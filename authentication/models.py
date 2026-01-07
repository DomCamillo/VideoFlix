from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta




class User(AbstractUser):
    """Costume user model using email as username field,
    to login with email and password. is_active gets set to True when user verifies email."""
    email = models.EmailField(unique=True)
    is_active= models.BooleanField(default=False)
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


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        expiry_time  = self.created_at + timedelta(hours=1)
        return timezone.now() < expiry_time

    class Meta:
        ordering = ['-created_at']