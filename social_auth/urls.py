from django.urls import path,include
from .views import *

urlpatterns = [
    path('google-login/', google_login, name='google-login'),
    path('', include('social_django.urls', namespace='social')), 

    #restfremwork google login
    path('auth/google/', GoogleSocialAuthView.as_view(), name='google-rest-login'),
]
