import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import User

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            return (user, token)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expirado')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Token inválido')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Usuario no encontrado')