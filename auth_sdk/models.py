class AnonymousUser:
    id = None
    username = ''
    is_authenticated = False

    def __str__(self):
        return 'AnonymousUser'

    def to_dict(self):
        return {
            'id': None,
            'username': '',
            'mayorista': 'N',
            'canal': 'MINOR',
            'provincia': '',
            'localidad': '',
            'varios': '',
            'zona': '',
            'role': '',
            'is_authenticated': False
        }

class User:
    def __init__(self, user_data):
        for key, value in user_data.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            'id': getattr(self, 'id', None),
            'username': getattr(self, 'username', None),
            'email': getattr(self, 'email', None),
            'role': getattr(self, 'role', None),
            'codigo': getattr(self, 'codigo', None),
            'c_postal': getattr(self, 'c_postal', None),
            'localidad': getattr(self, 'localidad', None),
            'provincia': getattr(self, 'provincia', None),
            'categoria': getattr(self, 'categoria', None),
            'mayorista': getattr(self, 'mayorista', None),
            'vendedor': getattr(self, 'vendedor', None),
            'canal': getattr(self, 'canal', None),
            'cuit': getattr(self, 'cuit', None),
            'sucursal': getattr(self, 'sucursal', None),
            'is_authenticated': getattr(self, 'is_authenticated', False)
        }
    
    def is_admin(self):
        return getattr(self, 'role', '').lower() == 'admin'

    def __str__(self):
        return f"User: {self.username}"