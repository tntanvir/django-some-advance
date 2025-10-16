from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend, AuthException
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# Authorised JavaScript origins
# https://walleyed-manipulatively-katelynn.ngrok-free.dev

# Authorised redirect URIs
# https://walleyed-manipulatively-katelynn.ngrok-free.dev/social/complete/google-oauth2/



def google_login(request):
    return render(request, 'google.html')

class GoogleSocialAuthView(APIView):
    """
    Accepts access_token/id_token from frontend and returns JWT.
    """ 

    def post(self, request):
        token = request.data.get("access_token")  # frontend থেকে পাঠানো Google token

        if not token:
            return Response({"error": "Access token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            strategy = load_strategy(request)
            backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=None)
            user = backend.do_auth(token)

        except MissingBackend:
            return Response({"error": "Invalid backend"}, status=status.HTTP_400_BAD_REQUEST)
        except AuthException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if user and user.is_active:
            # JWT Token তৈরি করো
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                }
            })
        else:
            return Response({"error": "Authentication failed"}, status=status.HTTP_400_BAD_REQUEST)
