from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import EmailVerificationToken

def send_verification_email(user, request):
    token = EmailVerificationToken.objects.create(user=user)
    verification_link = f"{request.scheme}://{request.get_host()}/api/verify-email/{token.token}/"

    subject ='Verify your email address'
    message = f"""
    Welcome {user.username},

    Please verify your email address by clicking the link below:

    {verification_link}

    This link will expire in 24 hours.


    """

    send_mail