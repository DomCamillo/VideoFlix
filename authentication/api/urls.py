from django.urls import path, include
from . import views
from .views import  LogoutView, LoginView,CookieTokenRefreshView# RegistrationView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify-email'),
  #  path('register/', RegistrationView.as_view(), name='registration'),
    path('logout/', LogoutView.as_view(), name='token_obtain_pair'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
  #  path('/api/accounts/', include('drf_registration.urls')),
  #  path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
  #  path('password_reset/', CookieTokenRefreshView.as_view(), name='token_refresh'),
   # path('password_confirm/<uidb64>/<token>/', CookieTokenRefreshView.as_view(), name='token_refresh'),


]