from django.urls import path
from .views import GoogleLoginURL, RegisterView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path("auth/google/", GoogleLoginURL.as_view(), name="google-login"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
