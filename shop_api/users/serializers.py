from rest_framework import serializers
from .models import User, UserConfirmation
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data, is_active=False)
        code = UserConfirmation.generate_code()
        UserConfirmation.objects.create(user=user, code=code)
        print(f"Confirmation code for {user.username}: {code}")
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Неверные учетные данные")
        if not user.is_active:
            raise serializers.ValidationError("Пользователь не активирован")
        attrs['user'] = user
        return attrs

class ConfirmationSerializer(serializers.Serializer):
    username = serializers.CharField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        try:
            user = User.objects.get(username=attrs['username'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
        if user.is_active:
            raise serializers.ValidationError("Пользователь уже активирован")
        if user.confirmation.code != attrs['code']:
            raise serializers.ValidationError("Неверный код подтверждения")
        attrs['user'] = user
        return attrs
