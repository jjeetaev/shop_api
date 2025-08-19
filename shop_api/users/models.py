from django.contrib.auth.models import AbstractUser
from django.db import models
import random

class User(AbstractUser):
    is_active = models.BooleanField(default=True)

class UserConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='confirmation')
    code = models.CharField(max_length=6)

    @staticmethod
    def generate_code():
        return f"{random.randint(0, 999999):06d}"
