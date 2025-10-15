from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import google.generativeai as genai
import json
import re

from .models import Chat, Message
from .serializers import ChatListSerializer, ChatDetailSerializer, MessageSerializer


# === Gemini Configuration ===
genai.configure(api_key=settings.GEMINI_API_KEY)

GEMINI_MODEL_NAMES = {
    'pro': 'gemini-2.5-pro',
    # Future scalability:
    # 'free': 'gemini-1.5-flash',
    # 'plus': 'gemini-2.5-turbo',
}


# === Chat List / Create View ===
class ChatListCreateAPIView(APIView):
    """List all chats or create a new one for the sidebar."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all chats for the logged-in user."""
        chats = Chat.objects.filter(user=request.user).order_by('-created_at')
        serializer = ChatListSerializer(chats, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new chat."""
        title = request.data.get("title", "New Chat")
        chat = Chat.objects.create(
            user=request.user,
            title=title
        )
        serializer = ChatListSerializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# === Chat Message View ===
class ChatMessageAPIView(APIView):
    """Send a message to a chat and get a structured bot response."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk, user=request.user)
        user_text = request.data.get("text")

        if not user_text:
            return Response(
                {"error": "Text field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Build AI Prompt ---
        prompt = f"""
        You are a technical documentation assistant.
        Respond ONLY with a valid JSON object following this schema:

        {{
          "title": "string - concise topic title",
          "summary": "string - short summary (1–2 lines)",
          "sections": [
            {{
              "heading": "string - section title",
              "content": "string - markdown formatted text",
              "code_examples": [
                {{
                  "language": "string - e.g. python, js, bash",
                  "code": "string - formatted code"
                }}
              ]
            }}
          ]
        }}

        User question: {user_text}

        Guidelines:
        - Use Markdown for 'content'
        - Keep it concise and clear
        - Include 2–4 sections, each with relevant info
        - Provide 1–2 short code examples
        - Return ONLY valid JSON — no text outside JSON.
        """

        try:
            # Select appropriate Gemini model
            user_sub = getattr(request.user, 'subscribed_model', 'pro')
            model_name = GEMINI_MODEL_NAMES.get(user_sub, GEMINI_MODEL_NAMES['pro'])

            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            raw_text = (response.text or "").strip()

            # Clean potential markdown code fences
            cleaned_text = re.sub(r"^```json|```$", "", raw_text, flags=re.MULTILINE).strip()

            # Parse JSON safely
            bot_json = json.loads(cleaned_text)

        except json.JSONDecodeError:
            bot_json = {
                "title": "Response Error",
                "summary": "Failed to parse AI response as valid JSON.",
                "sections": [
                    {"heading": "Error", "content": raw_text or "No valid content returned."}
                ],
                "code_examples": []
            }

        except Exception as e:
            bot_json = {
                "title": "Internal Error",
                "summary": "An unexpected error occurred.",
                "sections": [
                    {"heading": "Error", "content": str(e)}
                ],
                "code_examples": []
            }

        # Save message in database
        message = Message.objects.create(
            chat=chat,
            user=request.user,
            user_text=user_text,
            bot_text=bot_json
        )

        # Build response payload
        return Response({
            "id": message.id,
            "user_msg": message.user_text,
            "bot": bot_json,
            "created_at": message.created_at
        }, status=status.HTTP_201_CREATED)


# === Chat Detail View ===
class ChatDetailAPIView(APIView):
    """Retrieve full chat details and message history."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk, user=request.user)
        serializer = ChatDetailSerializer(chat)
        return Response(serializer.data)
