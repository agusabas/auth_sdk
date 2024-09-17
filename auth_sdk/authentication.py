import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings
import redis
import json

# Configuración de Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)
CACHE_EXPIRATION = 3600  # Tiempo de expiración en segundos (1 hora)

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            # Extraer el token del encabezado de autorización
            token = auth_header.split(' ')[1]

            # Intentar obtener los datos del usuario de la caché
            cached_user = redis_client.get(token)
            if cached_user:
                user_data = json.loads(cached_user)
                user = type('User', (), user_data)()
                return (user, token)

            # Decodificar el token con la clave secreta
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            # Extraer todos los campos personalizados
            user_data = {
                'id': payload['user_id'],
                'username': payload.get('username'),
                'email': payload.get('email'),
                'role': payload.get('role'),
                'codigo': payload.get('codigo'),
                'c_postal': payload.get('c_postal'),
                'localidad': payload.get('localidad'),
                'provincia': payload.get('provincia'),
                'categoria': payload.get('categoria'),
                'mayorista': payload.get('mayorista'),
                'vendedor': payload.get('vendedor'),
                'canal': payload.get('canal'),
                'cuit': payload.get('cuit'),
                'sucursal': payload.get('sucursal'),
                'is_staff': payload.get('is_staff', False),
                'is_superuser': payload.get('is_superuser', False),
                'permissions': payload.get('permissions', []),
                'is_authenticated': True
            }

            # Almacenar en caché
            redis_client.setex(token, CACHE_EXPIRATION, json.dumps(user_data))

            # Crear un objeto tipo User con los datos extraídos
            user = type('User', (), user_data)()
            return (user, token)
        
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expirado')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Token inválido')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Error de autenticación: {str(e)}')