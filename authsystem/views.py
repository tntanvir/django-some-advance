# from rest_framework.views import APIView 
# from rest_framework.response import Response 
# from rest_framework_simplejwt.tokens import RefreshToken 
# from .serializers import  RegisterSerializer
# from django.contrib.auth import get_user_model 
# from django.contrib.auth import authenticate 
# from rest_framework import generics, permissions, status 
# import requests
# from django.db import transaction


# User = get_user_model() 


# class GoogleLoginURL(APIView):
#     def post(self, request):
#         access_token = request.data.get('access_token')

#         if not access_token:
#             return Response({'error': 'Access token is required'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # ✅ Verify Google token info
#             token_info_response = requests.get(
#                 f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}'
#             )

#             if token_info_response.status_code != 200:
#                 return Response({'error': 'Invalid access token'}, status=status.HTTP_400_BAD_REQUEST)

#             token_info = token_info_response.json()
#             if 'error' in token_info:
#                 return Response({'error': token_info['error']}, status=status.HTTP_400_BAD_REQUEST)

#             # ✅ Get Google user data
#             user_info_response = requests.get(
#                 'https://www.googleapis.com/oauth2/v2/userinfo',
#                 headers={'Authorization': f'Bearer {access_token}'}
#             )

#             if user_info_response.status_code != 200:
#                 return Response({'error': 'Failed to fetch user info'}, status=status.HTTP_400_BAD_REQUEST)

#             user_data = user_info_response.json()
#             email = user_data.get("email")
#             name = user_data.get("name", "")
#             picture = user_data.get("picture", "")

#             if not email:
#                 return Response({'error': 'Email not found in Google account'}, status=status.HTTP_400_BAD_REQUEST)

#             username = email.split("@")[0]

#             # ✅ Create or get user atomically
#             with transaction.atomic():
#                 user, created = User.objects.get_or_create(
#                     email=email,
#                     defaults={
#                         "username": username,
#                         "Fullname": name,
#                         "social_auth_provider": "google",
#                         "is_active": True,
#                     },
#                 )

#                 # ✅ If user already exists, just log them in and return tokens
#                 if not created:
#                     # Update profile picture if not already set
#                     if hasattr(user, 'profile') and not user.profile.profile_picture and picture:
#                         user.profile.profile_picture = picture
#                         user.profile.save()

#                     # Issue JWT tokens for existing user
#                     refresh = RefreshToken.for_user(user)
#                     return Response({
#                         'access': str(refresh.access_token),
#                         'refresh': str(refresh),
#                         'user': {
#                             "id": user.id,
#                             "email": user.email,
#                             "Fullname": user.Fullname,
#                             "profile_picture": user.profile.profile_picture if hasattr(user, 'profile') else None,
#                             "is_verified": user.profile.is_verified if hasattr(user, 'profile') else False,
#                             "balance": user.account.balance if hasattr(user, 'account') else 0,
#                             "social_auth_provider": user.social_auth_provider,
#                         }
#                     }, status=status.HTTP_200_OK)

#                 # ✅ Create Profile & Account if new user
#                 Profile.objects.create(
#                     user=user,
#                     profile_picture=picture,
#                     is_verified=True
#                 )
#                 Account.objects.create(user=user)

#             # ✅ Check if suspended user (optional)
#             if getattr(user, 'is_active', False) is False:
#                 return Response(
#                     {"error": "User account is disabled."},
#                     status=status.HTTP_403_FORBIDDEN
#                 )

#             # ✅ Issue JWT tokens for new user
#             refresh = RefreshToken.for_user(user)

#             return Response({
#                 'access': str(refresh.access_token),
#                 'refresh': str(refresh),
#                 'user': {
#                     "id": user.id,
#                     "email": user.email,
#                     "Fullname": user.Fullname,
#                     "profile_picture": user.profile.profile_picture if hasattr(user, 'profile') else None,
#                     "is_verified": user.profile.is_verified if hasattr(user, 'profile') else False,
#                     "balance": user.account.balance if hasattr(user, 'account') else 0,
#                     "social_auth_provider": user.social_auth_provider,
#                 }
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             print("Google Login Error:", str(e))
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    
# """ -------- Manual Register -------- """
# class RegisterView(generics.CreateAPIView):
#     serializer_class = RegisterSerializer
#     permission_classes = [permissions.AllowAny]


# """ -------- Manual Login -------- """
# class LoginView(APIView):

#     def post(self, request):
#         # Get email and password directly from request
#         email = request.data.get("email")
#         password = request.data.get("password")
#         # print(email,password)
#         # user = User.objects.get(email=email)
#         # if user:
#         #     print('user',user)
#         # else:
#         #     print("no user")
#         # return Response({"message": "Login endpoint is under construction."},
#         #                 status=status.HTTP_501_NOT_IMPLEMENTED)
#         if not email or not password:
#             return Response({"error": "Email and password are required."},
#                             status=status.HTTP_400_BAD_REQUEST)

#         # Authenticate user
#         user = authenticate(username=email, password=password)
#         if not user:
#             return Response({"error": "Invalid email or password."},
#                             status=status.HTTP_401_UNAUTHORIZED)

#         # Generate JWT tokens
#         refresh = RefreshToken.for_user(user)

#         return Response({
#             "refresh": str(refresh),
#             "access": str(refresh.access_token),
#             "user": {
#                 "email": user.email,
#                 "fullname": user.Fullname,
#                 "provider": user.social_auth_provider or "manual",
#                 "profile_picture": user.profile.profile_picture if hasattr(user, "profile") else None,
#             }
#         }, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, status
from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
import requests

from .serializers import RegisterSerializer

User = get_user_model()


class GoogleLoginURL(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({'error': 'Access token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # ✅ Verify Google token
            token_info_response = requests.get(
                f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}'
            )
            if token_info_response.status_code != 200:
                return Response({'error': 'Invalid access token'}, status=status.HTTP_400_BAD_REQUEST)

            token_info = token_info_response.json()
            if 'error' in token_info:
                return Response({'error': token_info['error']}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ Get user info
            user_info_response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            if user_info_response.status_code != 200:
                return Response({'error': 'Failed to fetch user info'}, status=status.HTTP_400_BAD_REQUEST)

            user_data = user_info_response.json()
            email = user_data.get("email")
            name = user_data.get("name", "")
            picture = user_data.get("picture", "")

            if not email:
                return Response({'error': 'Email not found in Google account'}, status=status.HTTP_400_BAD_REQUEST)

            username = email.split("@")[0]

            # ✅ Create or get user
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "username": username,
                        "fullname": name,
                        "social_auth_provider": "google",
                        "is_verified": True,
                        "profile_picture": picture,
                        "is_active": True,
                    },
                )

                # ✅ If existing user, update profile picture if missing
                if not created:
                    if not user.profile_picture and picture:
                        user.profile_picture = picture
                        user.save(update_fields=["profile_picture"])

            # ✅ JWT tokens
            refresh = RefreshToken.for_user(user)

            # ✅ Unified Response
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "fullname": user.fullname,
                    "profile_picture": user.profile_picture,
                    "is_verified": user.is_verified,
                    "social_auth_provider": user.social_auth_provider,
                    "is_subscribed": user.is_subscribed,
                    "subscribed_model": user.subscribed_model,
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("Google Login Error:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



""" -------- Manual Register -------- """
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]



""" -------- Manual Login -------- """
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        if not user:
            return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "fullname": user.fullname,
                "profile_picture": user.profile_picture,
                "is_verified": user.is_verified,
                "social_auth_provider": user.social_auth_provider or "manual",
                "is_subscribed": user.is_subscribed,
                "subscribed_model": user.subscribed_model,
            }
        }, status=status.HTTP_200_OK)
