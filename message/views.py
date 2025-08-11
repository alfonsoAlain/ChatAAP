# Create your views here.
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from .models import ChatMessage
from .serializers import ChatMessageSerializer, ConversationStartSerializer, ChatMessageDetailedSerializer
from django.db.models import Max, Q
from django.contrib.auth import get_user_model

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)  # ⬅️ asigna automáticamente el sender

    def get_queryset(self):
        user = self.request.user
        # Mostrar solo mensajes en los que el usuario sea emisor o receptor
        return ChatMessage.objects.filter(sender=user) | ChatMessage.objects.filter(receiver=user)


class ChatSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        latest_messages = (
            ChatMessage.objects
            .filter(Q(sender=user) | Q(receiver=user))
            .values('conversation_id')
            .annotate(last_timestamp=Max('timestamp'))
            .order_by('-last_timestamp')
        )

        summaries = []

        for item in latest_messages:
            conv_id = item['conversation_id']
            if not conv_id:
                continue

            last_message = (
                ChatMessage.objects
                .filter(conversation_id=conv_id)
                .order_by('-timestamp')
                .first()
            )

            if not last_message:
                continue

            # Determinar contacto
            contact = last_message.receiver if last_message.sender == user else last_message.sender

            # Determinar la clave AES para el usuario actual
            if user == last_message.receiver:
                aes_key_for_me = last_message.aes_key_for_receiver
            elif user == last_message.sender:
                aes_key_for_me = last_message.aes_key_for_sender
            else:
                aes_key_for_me = None

            summaries.append({
                "conversation_id": conv_id,
                "contact_name": contact.username,
                "profile_image": request.build_absolute_uri(contact.profile_image.url) if getattr(contact, 'profile_image', None) else None,
                "last_message": last_message.content_encrypted,
                "last_timestamp": last_message.timestamp,
                "receiver_id": contact.id,
                "public_key": contact.public_key,
                "aes_key_for_me": aes_key_for_me,
            })

        return Response(summaries)


class ConversationMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        user = request.user

        messages = ChatMessage.objects.filter(
            conversation_id=conversation_id
        ).filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by('timestamp')

        messages.update(is_read=True)

        serializer = ChatMessageDetailedSerializer(
            messages,
            many=True,
            context={'user': user, 'request': request}
        )

        return Response(serializer.data)


class StartConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_one = request.user
        user_two_id = request.data.get('user_two_id')

        if not user_two_id:
            return Response({'error': 'user_two_id es requerido'}, status=400)

        try:
            User = get_user_model()
            user_two = User.objects.get(id=user_two_id)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)

        conversation_id = f"{min(user_one.id, user_two.id)}_{max(user_one.id, user_two.id)}"

        contact = user_two if user_one != user_two else user_one

        response_data = {
            "conversation_id": conversation_id,
            "contact_name": contact.username,
            "profile_image": request.build_absolute_uri(contact.profile_image.url) if getattr(contact, 'profile_image', None) else None,
            "last_message": "",
            "last_timestamp": timezone.now(),
            "receiver_id": contact.id,
            "public_key": contact.public_key,  # sin condicional aquí
        }

        print("DEBUG StartConversation response_data:", response_data)

        serializer = ConversationStartSerializer(response_data)  # instancia, no data=
        return Response(serializer.data)

class GrupoMessagesList(generics.ListAPIView):
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        return ChatMessage.objects.filter(
            (Q(aes_key_for_sender__isnull=True) | Q(aes_key_for_sender='')),
            (Q(aes_key_for_receiver__isnull=True) | Q(aes_key_for_receiver=''))
        ).order_by('timestamp')

