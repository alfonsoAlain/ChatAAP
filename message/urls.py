from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatMessageViewSet, ChatSummaryView, ConversationMessagesView, StartConversationView, \
    GrupoMessagesList

router = DefaultRouter()
router.register(r'messages', ChatMessageViewSet)

urlpatterns = [
    path('messages/summary/', ChatSummaryView.as_view(), name='chat-summary'),
    path('messages/conversation/<str:conversation_id>/', ConversationMessagesView.as_view(), name='conversation-messages'),
    path('messages/start_conversation/', StartConversationView.as_view(), name='start-conversation'),
    path('messages/group_messages/', GrupoMessagesList.as_view(), name='group_messages'),
    path('', include(router.urls)),
]