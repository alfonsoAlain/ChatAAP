from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings
from asgiref.sync import sync_to_async

User = get_user_model()

@sync_to_async
def get_user(token_key):
    try:
        access_token = AccessToken(token_key)
        print("🧪 Token decodificado correctamente:", access_token)
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)
        print("✅ Usuario autenticado:", user.username)
        return user
    except Exception as e:
        print("❌ Error autenticando token:", e)
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"].decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if token:
            scope["user"] = await get_user(token)
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)