from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from authentication.models import EmailVerificationToken , User, PasswordResetToken
from authentication.api.serializers import RegistrationSerializer
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import RegistrationSerializer,PasswordResetSerializer, PasswordResetConfirmSerializer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from ..send_mail import send_verification_email, send_password_reset_email
class RegisterView(APIView):
    """
    POST /api/register/
    Handle user registration by validating the incoming data,
    creating a new user, and sending an email verification link.
    If email delivery fails, the user is deleted.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            email_sent = send_verification_email(user, request)

            if not email_sent:
                user.delete()
                return Response({
                    'error': 'Could not send email.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            """Retrieve the token object to include in the response"""
            token_obj = EmailVerificationToken.objects.filter(user=user).first()

            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email
                },
                'token': str(token_obj.token) if token_obj else None
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class ActivateView(APIView):
    """
    GET /api/activate/<uidb64>/<token>/
    Handle account activation by extracting and decoding the user ID from the URL,
    validating the email verification token,
    and setting is_active to True if the token is valid.
    Deletes the token after successful activation.
    """
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'error': 'Invalid link.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification_token = EmailVerificationToken.objects.get(
                user=user,
                token=token
            )
        except EmailVerificationToken.DoesNotExist:
            return Response({
                'error': 'Invalid token.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not verification_token.is_valid():
            verification_token.delete()
            return Response({
                'error': 'This activation link has expired.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()

        verification_token.delete()

        return Response({
            'message': 'Account successfully activated.'
        }, status=status.HTTP_200_OK)



class LogoutView(APIView):
    """
    View to handle user logout by deleting JWT cookies.
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
       response = Response()
       response.delete_cookie('access_token')
       response.delete_cookie('refresh_token')
       response.data = {'message' : 'Sucessfully logged out'}
       return response


class EmailTokenObtainSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        attrs['username'] = attrs.get('email')
        return super().validate(attrs)



class LoginView(TokenObtainPairView):
    """
    An endpoint for obtaining JWT tokens and storing them in HttpOnly cookies.
    works with email and password isntead of username
    """
    serializer_class = EmailTokenObtainSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response(
                {"error": "Ungültige Anmeldedaten."},
                status=status.HTTP_401_UNAUTHORIZED )

        refresh = serializer.validated_data['refresh']
        access = serializer.validated_data['access']
        user = serializer.user

        response = Response({
            "detail": "Login successful",
            "user": {
                "id": user.id,
                "username": user.email
            }
        }, status=status.HTTP_200_OK)
        """Set HttpOnly cookies for access and refresh tokens"""
        response.set_cookie(
            key='access_token',
            value=str(access),
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=3600)

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=86400)

        return response




class CookieTokenRefreshView(TokenRefreshView):
    """get new access token using refresh token from HttpOnly cookie"""
def post(self, request, *args, **kwargs):
     refresh_token =request.COOKIES.get('refresh_token')

     if refresh_token is None:
         return Response({"detial": "Refresh token not found"}, status=400)

     serializer = self.get_serializer(data={'refresh': refresh_token})

     try: serializer.is_valid(raise_exception=True)
     except:
         return Response({"detail": "Invalid refresh token "}, status=401)

     access_token = serializer.validated_data.get("access")

     response = Response({"message": "access token refreshed successfully"})
     response.set_cookie(
            key="acces_token",
            httponly=True,
            value=access_token,
            secure=True,
            samesite='Lax'
        ),
     return response



class PasswordResetRequestView(APIView):
    """
    POST /api/password-reset/
    Request a password reset email by providing the user's email.
    If the email exists and the user is active, a password reset email is sent.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email, is_active=True)
                PasswordResetToken.objects.filter(user=user).delete()
                send_password_reset_email(user, request)
            except User.DoesNotExist:
                pass


            return Response({
            'detail': 'An email has been sent to reset your password.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PasswordResetConfirmView(APIView):
    """
    POST /api/password-reset-confirm/<uidb64>/<token>/
    Set a new password after validating the reset token.
    uidb64 and token are extracted from the URL.
    """
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Ivalid Reset Link.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            reset_token = PasswordResetToken.objects.get(
                user=user,
                token=token
            )
        except PasswordResetToken.DoesNotExist:
            return Response({ 'error': 'invalid Token.'}, status=status.HTTP_400_BAD_REQUEST)

        if not reset_token.is_valid():
            reset_token.delete()
            return Response({'error': 'This reset link is no longer valid.'}, status=status.HTTP_400_BAD_REQUEST)

        new_password = serializer.validated_data['new_password']
        user.set_password(new_password)
        user.save()

        reset_token.delete()
        return Response({'detail': 'Your Password has been successfully reset.' }, status=status.HTTP_200_OK)




