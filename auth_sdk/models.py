from django.db import models
from django.contrib.auth.models import AbstractBaseUser
import uuid

class User(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True, blank=True)
    jwt_secret = models.UUIDField(default=uuid.uuid4)

    class Meta:
        managed = False
        db_table = "users_user"

    USERNAME_FIELD = 'username'

    def jwt_get_secret_key(self):
        return self.jwt_secret