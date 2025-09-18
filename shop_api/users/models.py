from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import random

class UserManager(BaseUserManager):
    def create_user(self, email, phone_number=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен для регистрации")
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not phone_number:
            raise ValueError("У суперпользователя должен быть указан номер телефона")
        return self.create_user(email, phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)  
    birthdate = models.DateField(null=True, blank=True)  
    first_name = models.CharField(max_length=150, blank=True)  
    last_name = models.CharField(max_length=150, blank=True)   
    created_at = models.DateTimeField(default=timezone.now)     
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)    

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]

    def __str__(self):
        return self.email

class UserConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='confirmation')
    code = models.CharField(max_length=6)

    @staticmethod
    def generate_code():
        return f"{random.randint(0, 999999):06d}"
