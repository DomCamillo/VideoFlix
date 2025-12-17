from django.urls import path, include
from . import views
from .views import  LogoutView, LoginView,CookieTokenRefreshView# RegistrationView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate-email'),
  #  path('register/', RegistrationView.as_view(), name='registration'),
    path('logout/', LogoutView.as_view(), name='token_obtain_pair'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('password_reset/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('password_confirm/<uidb64>/<token>/', CookieTokenRefreshView.as_view(), name='token_refresh'),


]