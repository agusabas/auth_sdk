import os
import requests
from requests.exceptions import RequestException, Timeout
import redis
import json
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings
from .models import User, AnonymousUser

# Configuración de Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)
CACHE_EXPIRATION = 3600  # Tiempo de expiración en segundos (1 hora)

# Host del servicio de autenticación desde variable de entorno
AUTH_SERVICE_HOST = os.environ.get('AUTH_SERVICE_HOST', 'localhost:8000')
AUTH_SERVICE_URL = f"http://{AUTH_SERVICE_HOST}/api/user/get_details/"

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('JWT '):
            return (AnonymousUser(), None)

        token = auth_header.split(' ')[1]

        # Intentar obtener los datos del usuario de la caché
        cached_user = redis_client.get(token)
        if cached_user:
            user_data = json.loads(cached_user)
            user = User(user_data)  # Recrear el objeto User con los datos de la caché
            return (user, token)

        # Si no está en caché, obtener del microservicio de autenticación
        headers = {'Authorization': auth_header}
        
        try:
            response = requests.get(AUTH_SERVICE_URL, headers=headers, timeout=10)
            response.raise_for_status()
            response_data = response.json()
            
            if response_data.get('success') and 'results' in response_data:
                user_data = response_data['results']
                user_data['is_authenticated'] = True
                
                # Almacenar en caché
                redis_client.setex(token, CACHE_EXPIRATION, json.dumps(user_data))
                
                user = User(user_data)
                return (user, token)
            else:
                raise exceptions.AuthenticationFailed('Respuesta inválida del servicio de autenticación')
        
        except Timeout:
            raise exceptions.AuthenticationFailed('Tiempo de espera agotado al contactar el servicio de autenticación')
        except RequestException as e:
            raise exceptions.AuthenticationFailed(f'Error al contactar el servicio de autenticación: {str(e)}')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Error de autenticación: {str(e)}')
        
class AuthSDK:
    @staticmethod
    def get_user_details(user_id=None, token=None):
        if not token:
            raise ValueError("Se requiere un token de autenticación")

        # Crear una clave única para el caché
        cache_key = f"user_details:{token}:{user_id}" if user_id else f"user_details:{token}"

        # Intentar obtener los datos del usuario de la caché
        cached_user = redis_client.get(cache_key)
        if cached_user:
            user_data = json.loads(cached_user)
            return User(user_data)

        headers = {'Authorization': f'JWT {token}'}
        params = {}
        if user_id:
            params['user_id'] = user_id

        try:
            response = requests.get(AUTH_SERVICE_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            response_data = response.json()
            
            if response_data.get('success') and 'results' in response_data:
                user_data = response_data['results']
                user_data['is_authenticated'] = True
                
                # Almacenar en caché
                redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(user_data))
                
                return User(user_data)
            else:
                raise exceptions.AuthenticationFailed('Respuesta inválida del servicio de autenticación')
        
        except Timeout:
            raise exceptions.AuthenticationFailed('Tiempo de espera agotado al contactar el servicio de autenticación')
        except RequestException as e:
            raise exceptions.AuthenticationFailed(f'Error al contactar el servicio de autenticación: {str(e)}')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Error de autenticación: {str(e)}')