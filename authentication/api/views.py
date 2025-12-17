from rest_framework import status
from authentication.models import EmailVerificationToken  # Für get_object_or_404
from authentication.api.serializers import RegistrationSerializer
from ..send_mail import send_verification_email
from django.core.mail import send_mail ,EmailMessage
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegistrationSerializer, CostumeTokenObtainPairSerializer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.auth import get_user_model
User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegistrationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        try:
            send_verification_email(user, request)
            return Response({
                'message': 'Registrierung erfolgreich! Bitte überprüfe deine Emails.',
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            user.delete()
            return Response({
                'error': 'Email konnte nicht versendet werden. Bitte versuche es später erneut.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])

@permission_classes([AllowAny])
def verify_email(request, token):
    verification_token = get_object_or_404(EmailVerificationToken, token=token)

    if not verification_token.is_valid():
        return Response({
            'error': 'Dieser Verifizierungslink ist abgelaufen.'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = verification_token.user
    user.is_email_verified = True
    user.is_active = True
    user.save()

    verification_token.delete()

    return Response({
        'message': 'Email erfolgreich verifiziert! Du kannst dich jetzt einloggen.'
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
    serializer_class = CostumeTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = Response({"message": "Login Successfull"})

        refresh = serializer.validated_data['refresh']
        access = serializer.validated_data['access']

        response.set_cookie(
            key="acces_token",
            httponly=True,
            value=str(access),
            secure=True,
            samesite='Lax'
        ),
        response.set_cookie(
            key="refresh_token",
            httponly=True,
            value=str(refresh),
            secure=True,
            samesite='Lax'
        )
        response.data={"login": "successfully"}
        return response






class CookieTokenRefreshView(TokenRefreshView):
 def post(self, request, *args, **kwargs):
     refresh_token =request.COOKIES.get('refresh_token')

     if refresh_token is None:
         return Response({"detial": "Refresh token not found"}, status=400)

     serializer = self.get_serializer(data={'refresh': refresh_token})

     try: serializer.is_valid(raise_exception=True)
     except:
         return Response({"detail": "Invalid refresh token "}, status=401)

     acces_token = serializer.validated_data.get("access")

     response = Response({"message": "access token refreshed successfully"})
     response.set_cookie(
            key="acces_token",
            httponly=True,
            value=acces_token,
            secure=True,
            samesite='Lax'
        ),
     return response