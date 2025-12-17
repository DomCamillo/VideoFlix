from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import EmailVerificationToken
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def send_verification_email(user, request):

    token_obj = EmailVerificationToken.objects.create(user=user)

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = str(token_obj.token)

    activation_link = f"{request.scheme}://{request.get_host()}/api/activate/{uidb64}/{token}/"

    subject ='Verify your email address'
    message = f"""
    Welcome {user.username},

    Please verify your email address by clicking the link below:

    {activation_link}

    This link will expire in 24 hours.


    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        print(f" Email erfolgreich an {user.email} gesendet!")
        print(f" Activation Link: {activation_link}")
        return True
    except Exception as e:
        print(f"Email-Versand Fehler: {e}")
        return False