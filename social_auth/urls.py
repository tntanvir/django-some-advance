from django.urls import path,include
from .views import google_login

urlpatterns = [
    path('google-login/', google_login, name='google-login'),
    path('', include('social_django.urls', namespace='social')), 
]
