from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .redis_codes import generate_confirmation_code, save_confirmation_code, validate_confirmation_code


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['phone_number'] = user.phone_number
        if user.birthdate:
            token['birthdate'] = str(user.birthdate)
        return token


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(required=True)
    birthdate = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'email',
            'phone_number',
            'password',
            'first_name',
            'last_name',
            'birthdate',
        ]

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Номер телефона должен содержать только цифры")
        if len(value) < 10:
            raise serializers.ValidationError("Номер телефона должен содержать не менее 10 цифр")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            birthdate=validated_data.get('birthdate'),
            is_active=False
        )
        code = generate_confirmation_code()
        save_confirmation_code(user.email, code)
        print(f"Confirmation code for {user.email}: {code}")
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Неверные учетные данные")
        if not user.is_active:
            raise serializers.ValidationError("Пользователь не активирован")
        attrs['user'] = user
        return attrs


class ConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs['email']
        code = attrs['code']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")

        if user.is_active:
            raise serializers.ValidationError("Пользователь уже активирован")

        from .redis_codes import validate_confirmation_code
        if not validate_confirmation_code(email, code):
            raise serializers.ValidationError("Неверный код подтверждения")

        attrs['user'] = user
        return attrs
