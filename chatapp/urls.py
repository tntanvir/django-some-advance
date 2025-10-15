from django.urls import path
from .views import ChatListCreateAPIView, ChatMessageAPIView, ChatDetailAPIView

urlpatterns = [
    path('chats/', ChatListCreateAPIView.as_view(), name='chat-list-create'),
    path('chats/<int:pk>/', ChatDetailAPIView.as_view(), name='chat-detail'),
    path('chats/<int:pk>/message/', ChatMessageAPIView.as_view(), name='chat-message'),
]
