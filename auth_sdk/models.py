class AnonymousUser:
    """Anonymous user model for unauthenticated requests."""
    
    def __init__(self):
        self.id = None
        self.username = ''
        self.email = ''
        self.is_authenticated = False
        self.is_active = False
        self.user_permissions = []

    def __str__(self):
        return 'AnonymousUser'

    def to_dict(self):
        return {
            'id': None,
            'username': '',
            'email': '',
            'is_authenticated': False,
            'is_active': False,
            'user_permissions': []
        }
    
    def has_permission(self, perm):
        return False
    
    def is_admin(self):
        return False

class User:
    """Authenticated user model with standard Django user attributes."""
    
    def __init__(self, user_data):
        if not isinstance(user_data, dict):
            raise ValueError("user_data must be a dictionary")
        
        # Set standard user attributes with defaults
        self.id = user_data.get('id')
        self.username = user_data.get('username', '')
        self.email = user_data.get('email', '')
        self.first_name = user_data.get('first_name', '')
        self.last_name = user_data.get('last_name', '')
        self.is_authenticated = user_data.get('is_authenticated', True)
        self.is_active = user_data.get('is_active', True)
        self.is_staff = user_data.get('is_staff', False)
        self.is_superuser = user_data.get('is_superuser', False)
        self.user_permissions = user_data.get('user_permissions', [])
        self.groups = user_data.get('groups', [])
        self.date_joined = user_data.get('date_joined')
        self.last_login = user_data.get('last_login')
        
        # Store any additional custom fields
        self._custom_fields = {}
        for key, value in user_data.items():
            if not hasattr(self, key):
                self._custom_fields[key] = value

    def to_dict(self):
        """Return user data as dictionary."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_authenticated': self.is_authenticated,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'is_superuser': self.is_superuser,
            'user_permissions': self.user_permissions,
            'groups': self.groups,
            'date_joined': self.date_joined,
            'last_login': self.last_login
        }
        # Include custom fields
        data.update(self._custom_fields)
        return data
    
    def is_admin(self):
        """Check if user has admin privileges."""
        return self.is_staff or self.is_superuser

    def has_permission(self, perm):
        """Check if user has specific permission."""
        if not isinstance(perm, str):
            return False
        return perm in self.user_permissions

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.username

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.username

    def __str__(self):
        return f"User: {self.username}"