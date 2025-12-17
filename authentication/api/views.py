from rest_framework import status
from authentication.models import EmailVerificationToken , User
from authentication.api.serializers import RegistrationSerializer
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from ..send_mail import send_verification_email
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import RegistrationSerializer, CostumeTokenObtainPairSerializer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)




@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegistrationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        email_sent = send_verification_email(user, request)
        if not email_sent:
            user.delete()
            return Response({
                'error': 'Email konnte nicht versendet werden.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        token_obj = EmailVerificationToken.objects.filter(user=user).first()

        return Response({
            'user': {
                'id': user.id,
                'email': user.email
            },
            'token': str(token_obj.token) if token_obj else None
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['GET'])
@permission_classes([AllowAny])
def activate(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({
            'error': 'ivalid link.'
        }, status=status.HTTP_400_BAD_REQUEST)
    try:
        verification_token = EmailVerificationToken.objects.get(
            user=user,
            token=token
        )
    except EmailVerificationToken.DoesNotExist:
        return Response({
            'error': 'ivalid token'
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
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {"error": "Ungültige Anmeldedaten."},
                status=status.HTTP_401_UNAUTHORIZED
            )


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


        response.set_cookie(
            key='access_token',
            value=str(access),
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=3600
        )

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=86400
        )

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