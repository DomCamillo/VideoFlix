from django.urls import path, include
from . import views
from .views import  LogoutView, LoginView,CookieTokenRefreshView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# su domin 0508 dominic@moerth.ch

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate-email'),
    path('logout/', LogoutView.as_view(), name='token_obtain_pair'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_confirm'),


]