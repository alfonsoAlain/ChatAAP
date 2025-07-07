# Create your views here.
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ChatMessage
from .serializers import ChatMessageSerializer, ChatSummarySerializer
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

        # Agrupar por conversation_id y obtener timestamp más reciente
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

            # Buscar el mensaje más reciente de esa conversación
            last_message = (
                ChatMessage.objects
                .filter(conversation_id=conv_id)
                .order_by('-timestamp')
                .first()
            )

            if not last_message:
                continue

            contact = (
                last_message.receiver if last_message.sender == user
                else last_message.sender
            )

            summaries.append({
                'conversation_id': conv_id,
                'contact_name': contact.username,
                'profile_image': request.build_absolute_uri(contact.profile_image.url) if contact.profile_image else None,
                'last_message': last_message.message,
                'last_timestamp': last_message.timestamp,
                'receiver_id': contact.id
            })

        serializer = ChatSummarySerializer(summaries, many=True)
        return Response(serializer.data)


class ConversationMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        user = request.user

        # Asegura que el usuario sea parte de la conversación
        messages = ChatMessage.objects.filter(
            conversation_id=conversation_id
        ).filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by('timestamp')

        messages.update(is_read=True)

        serializer = ChatMessageSerializer(messages, many=True)

        return Response(serializer.data)

# views.py
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

        # Generar ID único en base a los IDs ordenados
        conversation_id = f"{min(user_one.id, user_two.id)}_{max(user_one.id, user_two.id)}"

        # Opcional: puedes crear un mensaje vacío si no hay ninguno todavía

        # Determinar el contacto: si yo soy user_one, el contacto es user_two y viceversa
        contact = user_two if user_one != user_two else user_one

        response_data = {
            "conversation_id": conversation_id,
            "contact_name": contact.username,
            "profile_image": request.build_absolute_uri(contact.profile_image.url) if hasattr(contact, 'profile_image') and contact.profile_image else None,
            "last_message": "",  # Podrías buscar el último mensaje si quieres
            "last_timestamp": timezone.now(),  # o el del último mensaje real
            "receiver_id": contact.id
        }

        return Response(response_data)
