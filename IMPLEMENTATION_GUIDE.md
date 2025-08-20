# Implementation Guide

This guide explains how to implement both the authentication service and client microservices using this SDK.

## Authentication Service Implementation

The authentication service needs to provide the `/api/user/get_details/` endpoint that this SDK expects.

### Required Endpoint

**URL:** `/api/user/get_details/`  
**Method:** `GET`  
**Headers:** `Authorization: JWT <token>`  
**Optional Query Params:** `user_id` (to get details of a specific user)

### Expected Response Format

```json
{
    "success": true,
    "results": {
        "id": 123,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": true,
        "is_staff": false,
        "is_superuser": false,
        "user_permissions": ["read_users", "write_posts"],
        "groups": ["editors", "moderators"],
        "date_joined": "2024-01-15T10:00:00Z",
        "last_login": "2024-01-20T15:30:00Z",
        
        // Custom fields (optional)
        "company_id": 456,
        "role": "manager",
        "department": "sales"
    }
}
```

### Authentication Service Example (Django)

```python
# views.py in your authentication service
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    """
    Get user details for microservices authentication.
    Supports getting current user or specific user by ID.
    """
    user_id = request.GET.get('user_id')
    
    if user_id:
        # Get specific user (ensure proper permissions)
        try:
            user = User.objects.get(id=user_id)
            # Add permission check here if needed
        except User.DoesNotExist:
            return Response({
                "success": False,
                "error": "User not found"
            }, status=404)
    else:
        # Get current authenticated user
        user = request.user
    
    # Build user data
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'date_joined': user.date_joined.isoformat() if user.date_joined else None,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        
        # Get user permissions
        'user_permissions': list(user.user_permissions.values_list('codename', flat=True)),
        'groups': list(user.groups.values_list('name', flat=True)),
    }
    
    # Add custom fields if needed
    # user_data.update({
    #     'company_id': getattr(user, 'company_id', None),
    #     'role': getattr(user, 'role', None),
    # })
    
    return Response({
        "success": True,
        "results": user_data
    })

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/user/get_details/', views.get_user_details, name='get_user_details'),
]
```

### JWT Token Generation

Your authentication service should generate JWT tokens during login:

```python
# login view in authentication service
import jwt
from datetime import datetime, timedelta
from django.conf import settings

def login_view(request):
    # ... authenticate user ...
    
    # Generate JWT token
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
        'iat': datetime.utcnow(),
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    return Response({
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })
```

## Client Microservice Implementation

Client microservices use this SDK to authenticate requests against the authentication service.

### Installation

```bash
# Install the SDK
pip install -e git+https://github.com/agusabas/auth_sdk.git#egg=django-microservices-auth

# Or with Redis support
pip install -e "git+https://github.com/agusabas/auth_sdk.git#egg=django-microservices-auth[redis]"
```

### Django Settings Configuration

```python
# settings.py in your microservice

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'auth_sdk',  # Add the auth SDK
    # ... your apps
]

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'auth_sdk.JWTAuthentication',  # Use the SDK authentication
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'auth_sdk.IsAuthenticated',  # Require authentication by default
    ],
}

# Optional: Configure logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'auth_sdk': {
            'handlers': ['console'],
            'level': 'INFO',  # Change to DEBUG for development
            'propagate': False,
        },
    },
}
```

### Environment Variables

Create `.env` file in your microservice:

```bash
# Authentication Service
AUTH_SDK_SERVICE_HOST=auth-service:8000
AUTH_SDK_SERVICE_SCHEME=http
AUTH_SDK_SERVICE_ENDPOINT=/api/user/get_details/
AUTH_SDK_SERVICE_TIMEOUT=10

# Redis (optional)
AUTH_SDK_REDIS_HOST=redis
AUTH_SDK_REDIS_PORT=6379
AUTH_SDK_REDIS_DB=0
AUTH_SDK_CACHE_EXPIRATION=3600
AUTH_SDK_ENABLE_CACHING=true

# JWT Configuration
AUTH_SDK_JWT_HEADER_PREFIX=JWT

# Logging
AUTH_SDK_LOG_LEVEL=INFO
```

### Usage in Views

```python
# views.py in your microservice
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from auth_sdk import IsAuthenticated, HasPermission, IsAdminUser, AuthSDK

# Basic authenticated endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    user = request.user
    return Response({
        'message': f'Hello {user.username}!',
        'user_id': user.id,
        'is_admin': user.is_admin(),
    })

# Permission-based endpoint
@api_view(['POST'])
@permission_classes([HasPermission('create_post', 'write_content')])
def create_post(request):
    # Only users with 'create_post' OR 'write_content' permission can access
    return Response({'message': 'Post created'})

# Admin-only endpoint
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def admin_only_view(request):
    # Only staff or superuser can access
    return Response({'message': 'Admin action performed'})

# Programmatic user lookup
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user_id = request.GET.get('user_id')
    
    # Get current user's token from the authentication
    token = request.auth
    
    try:
        # Get details of another user
        user = AuthSDK.get_user_details(token=token, user_id=user_id)
        return Response({
            'user': user.to_dict()
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=400)
```

### Class-Based Views

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from auth_sdk import IsAuthenticated, HasPermission

class UserProfileView(APIView):
    authentication_classes = []  # SDK handles this globally
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'profile': user.to_dict(),
            'full_name': user.get_full_name(),
            'permissions': user.user_permissions,
        })

class ContentView(APIView):
    permission_classes = [HasPermission('read_content')]
    
    def get(self, request):
        return Response({'content': 'Secret content'})
        
    def post(self, request):
        # This will be checked separately
        if not request.user.has_permission('write_content'):
            return Response({'error': 'No write permission'}, status=403)
        return Response({'message': 'Content created'})
```

## Frontend Integration

Frontend applications need to include the JWT token in requests:

```javascript
// JavaScript/React example
const token = localStorage.getItem('jwt_token');

fetch('/api/protected-endpoint/', {
    headers: {
        'Authorization': `JWT ${token}`,
        'Content-Type': 'application/json',
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Docker Compose Example

```yaml
version: '3.8'

services:
  auth-service:
    build: ./auth_service
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/auth_db
    depends_on:
      - db
      
  microservice-1:
    build: ./microservice_1
    ports:
      - "8002:8000"
    environment:
      - AUTH_SDK_SERVICE_HOST=auth-service:8000
      - AUTH_SDK_REDIS_HOST=redis
      - AUTH_SDK_ENABLE_CACHING=true
    depends_on:
      - auth-service
      - redis
      
  microservice-2:
    build: ./microservice_2
    ports:
      - "8003:8000"
    environment:
      - AUTH_SDK_SERVICE_HOST=auth-service:8000
      - AUTH_SDK_REDIS_HOST=redis
    depends_on:
      - auth-service
      - redis
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
      
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=auth_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
```

## Testing

```python
# test_authentication.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from auth_sdk import User

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
    @patch('auth_sdk.authentication.requests.get')
    def test_jwt_authentication(self, mock_get):
        # Mock the auth service response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'success': True,
            'results': {
                'id': 1,
                'username': 'testuser',
                'email': 'test@example.com',
                'is_active': True,
                'user_permissions': ['read_content']
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test authenticated request
        response = self.client.get(
            '/api/protected/',
            HTTP_AUTHORIZATION='JWT fake_token'
        )
        
        self.assertEqual(response.status_code, 200)
```