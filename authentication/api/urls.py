from django.urls import path, include
from . import views
from .views import  LogoutView, LoginView,CookieTokenRefreshView, PasswordResetView, PasswordResetConfirmView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate-email'),
    path('logout/', LogoutView.as_view(), name='token_obtain_pair'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_confirm'),


]