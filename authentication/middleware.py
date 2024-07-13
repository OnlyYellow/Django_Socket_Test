from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.db import database_sync_to_async

@database_sync_to_async
def get_user_from_token(token):
    jwt_auth = JWTAuthentication()
    validated_token = jwt_auth.get_validated_token(token)
    return jwt_auth.get_user(validated_token)

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware for extracting JWT token from cookies and authenticating users.
    """
    async def __call__(self, scope, receive, send):
        cookies = scope.get('cookies', {})
        jwt_token = cookies.get('access')  # Use the actual cookie name, which is 'access' in this case
        
        if jwt_token:
            scope['user'] = await get_user_from_token(jwt_token)
            if scope['user'] is None:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)
