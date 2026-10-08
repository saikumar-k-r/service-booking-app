from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication


@database_sync_to_async
def authenticate_token(token):
    try:
        authentication = JWTAuthentication()
        validated_token = authentication.get_validated_token(token)
        return authentication.get_user(validated_token)
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)

        token = params.get("token", [None])[0]
        device_id = params.get("device_id", [None])[0]

        scope["user"] = (
            await authenticate_token(token)
            if token
            else AnonymousUser()
        )

        scope["device_id"] = device_id

        return await self.inner(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)