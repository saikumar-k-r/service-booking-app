from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound

from .models import ChatConversation, ChatMessage
from .serializers import ChatConversationSerializer, ChatMessageSerializer


class ChatConversationListView(generics.ListCreateAPIView):
    serializer_class = ChatConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatConversation.objects.filter(
            customer=self.request.user
        ) | ChatConversation.objects.filter(
            provider=self.request.user
        )


class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_conversation(self):
        try:
            conversation = ChatConversation.objects.get(
                pk=self.kwargs["conversation_id"]
            )
        except ChatConversation.DoesNotExist:
            raise NotFound("Conversation not found.")

        if (
            conversation.customer_id != self.request.user.id
            and conversation.provider_id != self.request.user.id
        ):
            raise PermissionDenied(
                "You are not allowed to access this conversation."
            )

        return conversation

    def get_queryset(self):
        conversation = self.get_conversation()

        return ChatMessage.objects.filter(
            conversation=conversation
        )

    def perform_create(self, serializer):
        conversation = self.get_conversation()

        serializer.save(
            conversation=conversation,
            sender=self.request.user
        )