from datetime import date
from rest_framework.exceptions import ValidationError


def validate_user_age(user):
    birthdate = getattr(user, "birthdate", None)

    if not birthdate:
        raise ValidationError("Укажите дату рождения, чтобы создать продукт.")

    if isinstance(birthdate, str):
        try:
            birthdate = date.fromisoformat(birthdate)
        except ValueError:
            raise ValidationError("Некорректный формат даты рождения в токене.")

    today = date.today()
    age = today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )

    if age < 18:
        raise ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")
