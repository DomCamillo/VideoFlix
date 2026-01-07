from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from .models import EmailVerificationToken
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import PasswordResetToken
from django.utils.html import strip_tags

def send_verification_email(user, request):

    token_obj = EmailVerificationToken.objects.create(user=user)

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = str(token_obj.token)

    activation_link = f"{request.scheme}://{request.get_host()}/api/activate/{uidb64}/{token}/"

    subject ='Verify your email address'


    html_content = render_to_string('verification_email.html', {
        'username': user.username,
        'activation_link': activation_link,
    })

    text_content = strip_tags(html_content)


    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        print(f" Succesfully send email to {user.email} ")
        return True
    except Exception as error:
        print(f"Emial sent error: {error}")
        return False



def send_password_reset_email(user, request):
    token_obj = PasswordResetToken.objects.create(user=user)

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = str(token_obj.token)

    reset_link = f"http://localhost:5500/pages/auth/confirm_password.html?uid={uidb64}&token={token}"

    subject ='Password Reset Request'

    html_content = render_to_string('password_reset.html', {
    'username': user.username,
    'reset_link': reset_link,
    })
    text_content = strip_tags(html_content)

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        print(f" Succesfully send email to {user.email} ")
        return True
    except Exception as error:
        print(f"Emial sent error: {error}")
        return False