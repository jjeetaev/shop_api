from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, phone_number=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен для регистрации")
        if not phone_number:
            raise ValueError("Номер телефона обязателен")
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
        if not password:
            raise ValueError("Суперпользователь должен иметь пароль")
        return self.create_user(email, phone_number, password, **extra_fields)
