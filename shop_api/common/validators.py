from datetime import date
from rest_framework import serializers

def validate_user_age(request):
    token_payload = getattr(request, "auth", None)

    if not token_payload or "birthdate" not in token_payload:
        raise serializers.ValidationError("Укажите дату рождения, чтобы создать продукт.")

    try:
        birthdate = date.fromisoformat(token_payload["birthdate"])
    except Exception:
        raise serializers.ValidationError("Некорректный формат даты рождения в токене.")

    today = date.today()
    age = today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )

    if age < 18:
        raise serializers.ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")
