import json
import logging
from typing import Optional, Tuple, Union

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

from .config import AuthConfig
from .models import User, AnonymousUser
from .cache import CacheManager

logger = logging.getLogger(__name__)

# Initialize cache manager
cache_manager = CacheManager()

class JWTAuthentication(BaseAuthentication):
    """JWT Authentication class for Django REST Framework."""
    
    def authenticate(self, request) -> Optional[Tuple[Union[User, AnonymousUser], Optional[str]]]:
        """
        Authenticate the request and return a two-tuple of (user, token).
        Returns None if authentication fails or is not attempted.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None
            
        try:
            token = self._extract_token(auth_header)
            if not token:
                return None
                
            user = self._get_user_from_token(token)
            return (user, token)
            
        except exceptions.AuthenticationFailed:
            raise
        except Exception as e:
            logger.error(f"Unexpected authentication error: {e}")
            raise exceptions.AuthenticationFailed('Authentication failed')
    
    def _extract_token(self, auth_header: str) -> Optional[str]:
        """Extract JWT token from Authorization header."""
        prefix = AuthConfig.JWT_HEADER_PREFIX
        if not auth_header.startswith(f'{prefix} '):
            return None
            
        parts = auth_header.split(' ')
        if len(parts) != 2:
            return None
            
        return parts[1]
    
    def _get_user_from_token(self, token: str) -> User:
        """Get user data from token, using cache if available."""
        # Try to get user data from cache first
        if cache_manager.is_available():
            cached_data = cache_manager.get(token)
            if cached_data:
                try:
                    user_data = json.loads(cached_data)
                    return User(user_data)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse cached user data: {e}")
                    cache_manager.delete(token)
        
        # Get user data from authentication service
        user_data = self._fetch_user_from_service(token)
        user_data['is_authenticated'] = True
        
        # Cache the user data
        if cache_manager.is_available():
            try:
                cache_manager.set(token, json.dumps(user_data))
            except Exception as e:
                logger.warning(f"Failed to cache user data: {e}")
        
        return User(user_data)
    
    def _fetch_user_from_service(self, token: str) -> dict:
        """Fetch user data from authentication service."""
        url = AuthConfig.get_auth_service_url()
        headers = {
            'Authorization': f'{AuthConfig.JWT_HEADER_PREFIX} {token}',
            'Content-Type': 'application/json',
        }
        
        try:
            response = requests.get(
                url, 
                headers=headers, 
                timeout=AuthConfig.AUTH_SERVICE_TIMEOUT
            )
            response.raise_for_status()
            
            response_data = response.json()
            
            if not response_data.get('success') or 'results' not in response_data:
                logger.warning(f"Invalid response from auth service: {response_data}")
                raise exceptions.AuthenticationFailed('Invalid response from authentication service')
            
            return response_data['results']
            
        except Timeout:
            logger.error("Timeout connecting to authentication service")
            raise exceptions.AuthenticationFailed('Authentication service timeout')
        except ConnectionError:
            logger.error("Connection error to authentication service")
            raise exceptions.AuthenticationFailed('Authentication service unavailable')
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                raise exceptions.AuthenticationFailed('Invalid token')
            logger.error(f"HTTP error from auth service: {e}")
            raise exceptions.AuthenticationFailed('Authentication service error')
        except RequestException as e:
            logger.error(f"Request error to auth service: {e}")
            raise exceptions.AuthenticationFailed('Authentication service error')

class AuthSDK:
    """SDK for programmatic authentication operations."""
    
    @staticmethod
    def get_user_details(token: str, user_id: Optional[str] = None) -> User:
        """
        Get user details from authentication service.
        
        Args:
            token: JWT authentication token
            user_id: Optional specific user ID to fetch
            
        Returns:
            User object with user data
            
        Raises:
            ValueError: If token is not provided
            AuthenticationFailed: If authentication fails
        """
        if not token or not isinstance(token, str):
            raise ValueError("Authentication token is required and must be a string")
        
        if not AuthConfig.ENABLE_USER_DETAILS_ENDPOINT:
            raise ValueError("User details endpoint is disabled")
        
        # Create unique cache key
        cache_key = f"user_details:{token}"
        if user_id:
            cache_key += f":{user_id}"
        
        # Try cache first
        if cache_manager.is_available():
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                try:
                    user_data = json.loads(cached_data)
                    return User(user_data)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse cached user details: {e}")
                    cache_manager.delete(cache_key)
        
        # Fetch from service
        url = AuthConfig.get_auth_service_url()
        headers = {
            'Authorization': f'{AuthConfig.JWT_HEADER_PREFIX} {token}',
            'Content-Type': 'application/json',
        }
        params = {'user_id': user_id} if user_id else {}
        
        try:
            response = requests.get(
                url, 
                headers=headers, 
                params=params,
                timeout=AuthConfig.AUTH_SERVICE_TIMEOUT
            )
            response.raise_for_status()
            
            response_data = response.json()
            
            if not response_data.get('success') or 'results' not in response_data:
                logger.warning(f"Invalid response from auth service: {response_data}")
                raise exceptions.AuthenticationFailed('Invalid response from authentication service')
            
            user_data = response_data['results']
            user_data['is_authenticated'] = True
            
            # Cache the result
            if cache_manager.is_available():
                try:
                    cache_manager.set(cache_key, json.dumps(user_data))
                except Exception as e:
                    logger.warning(f"Failed to cache user details: {e}")
            
            return User(user_data)
            
        except Timeout:
            logger.error("Timeout connecting to authentication service")
            raise exceptions.AuthenticationFailed('Authentication service timeout')
        except ConnectionError:
            logger.error("Connection error to authentication service")
            raise exceptions.AuthenticationFailed('Authentication service unavailable')
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                raise exceptions.AuthenticationFailed('Invalid token')
            logger.error(f"HTTP error from auth service: {e}")
            raise exceptions.AuthenticationFailed('Authentication service error')
        except RequestException as e:
            logger.error(f"Request error to auth service: {e}")
            raise exceptions.AuthenticationFailed('Authentication service error')