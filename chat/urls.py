from django.urls import path

from .views import (
    ChatConversationListView,
    ChatMessageListCreateView,
)

urlpatterns = [
    path(
        "conversations/",
        ChatConversationListView.as_view(),
        name="chat-conversations",
    ),
    path(
        "conversations/<int:conversation_id>/messages/",
        ChatMessageListCreateView.as_view(),
        name="chat-messages",
    ),
]