
from django.conf import settings
from django.template.loader import render_to_string
from .models import EmailVerificationToken
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import PasswordResetToken
from django.utils.html import strip_tags

import os
from .models import EmailVerificationToken, PasswordResetToken
from .email import EmailMultiRelated

def send_verification_email(user, request):
    """When the user signs up, a token is generated and an email is sent to the user with a verification link.
    The link contains the encoded user ID and the token. User must click the link to activate the account.
    Html email template is used to send the email,
    falls back to plain text if html email fails to send.
    """

    token_obj = EmailVerificationToken.objects.create(user=user)
    """encodes the user ID in base64 and stringifies the token"""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = str(token_obj.token)

    activation_link = f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uidb64}&token={token}"

    subject ='Verify your email address'


    html_content = render_to_string('verification_email.html', {
        'username': user.username,
        'activation_link': activation_link,
    })

    text_content = strip_tags(html_content)

    try:
        email = EmailMultiRelated(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],

        )
        email.attach_alternative(html_content, "text/html")
        logo_path = os.path.join(settings.BASE_DIR, 'assets', 'images', 'logo.png')

        if os.path.exists(logo_path):
            email.attach_related_file(logo_path, 'image/png')
        email.send(fail_silently=False)

        print(f" Succesfully send email to {user.email} ")
        return True
    except Exception as error:
        print(f"Emial sent error: {error}")

        return False






def send_password_reset_email(user, request):
    """Sends a password reset email to the user with a link containing a token and encoded user ID."""
    token_obj = PasswordResetToken.objects.create(user=user)

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = str(token_obj.token)

    reset_link = f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html?uid={uidb64}&token={token}"

    subject ='Password Reset Request'

    html_content = render_to_string('password_reset.html', {
    'username': user.username,
    'reset_link': reset_link,
    })
    text_content = strip_tags(html_content)

    try:
        email = EmailMultiRelated(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],

        )
        email.attach_alternative(html_content, "text/html")
        logo_path = os.path.join(settings.BASE_DIR, 'assets', 'images', 'logo.png')

        if os.path.exists(logo_path):

            email.attach_related_file(logo_path, 'image/png')
        email.send(fail_silently=False)

        print(f" Succesfully send email to {user.email} ")
        return True
    except Exception as error:
        print(f"Emial sent error: {error}")

        return False