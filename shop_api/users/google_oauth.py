import requests
from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

def get_google_user_info(auth_code, redirect_uri):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": auth_code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    r = requests.post(token_url, data=data)
    r.raise_for_status()
    access_token = r.json().get("access_token")

    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(user_info_url, headers=headers)
    r.raise_for_status()
    return r.json()  # вернёт dict с email, given_name, family_name

def get_or_create_user(google_user):
    email = google_user["email"]
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "first_name": google_user.get("given_name", ""),
            "last_name": google_user.get("family_name", ""),
            "created_at": timezone.now(),
        }
    )
    return user

def generate_jwt_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['email'] = user.email
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }
