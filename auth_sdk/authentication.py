import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            user_data = {
                'id': payload['user_id'],
                'username': payload.get('username'),
                'email': payload.get('email'),
                'is_staff': payload.get('is_staff', False),
                'is_superuser': payload.get('is_superuser', False),
                'permissions': payload.get('permissions', []),
                'is_authenticated': True
            }
            
            user = type('User', (), user_data)()
            return (user, token)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expirado')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Token inválido')
        except Exception as e:
            raise exceptions.AuthenticationFailed('Error de autenticación')