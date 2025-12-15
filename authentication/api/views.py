from rest_framework import status
from rest_framework.views import APIView
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

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            activation_token = str(refresh.access_token)
            response_data = {
                'user': {
                    'id': user.id,
                    'email': user.email
                },
                'token': activation_token
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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

        response.set_cookie( #Speichere diesen Token in einem HttpOnly-Cookie namens access_token
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
        #response.set_cookie() ist eine Django-Funktion, mit der du dem Browser Cookies mitschickst.
        #Diese Cookies werden danach automatisch vom Browser gespeichert und bei jedem zukünftigen Request automatisch wieder mitgeschickt.

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