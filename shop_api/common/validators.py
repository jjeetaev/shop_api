from datetime import date
from rest_framework import serializers

def validate_user_age(user):
    if not user.birthdate:
        raise serializers.ValidationError("Укажите дату рождения, чтобы создать продукт.")

    today = date.today()
    age = today.year - user.birthdate.year - (
        (today.month, today.day) < (user.birthdate.month, user.birthdate.day)
    )
    if age < 18:
        raise serializers.ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")
