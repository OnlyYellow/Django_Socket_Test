# from channels.middleware import BaseMiddleware
# from channels.auth import AuthMiddlewareStack
# from channels.db import database_sync_to_async
# from urllib.parse import parse_qs
# from django.contrib.auth.models import User
# from django.db import close_old_connections
# from rest_framework_simplejwt.tokens import AccessToken
# from .models import User

# class TokenAuthMiddleware(BaseMiddleware):
#     async def __call__(self, scope, receive, send):
#         headers = dict(scope['headers'])
        
#         if b'cookie' in headers:
#             cookies = headers[b'cookie'].decode()
#             cookie_dict = dict(map(lambda x: x.split('='), cookies.split('; ')))
#             access_token = cookie_dict.get('access', None)
#             if access_token:
#                 try:
#                     token = AccessToken(access_token)
#                     user_id = token['user_id']
#                     user = await database_sync_to_async(User.objects.get)(id=user_id)
#                     scope['user'] = user
#                 except Exception as e:
#                     # 토큰 검증 실패, 연결을 거부
#                     await send({
#                         'type': 'websocket.close'
#                     })
#                     return
#         else:
#             # 쿠키에 토큰이 없는 경우, 연결 거부
#             await send({
#                 'type': 'websocket.close'
#             })
#             return

#         return await super().__call__(scope, receive, send)

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
