import redis
import random
from django.conf import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

def generate_confirmation_code():
    return f"{random.randint(0, 999999):06d}"

def save_confirmation_code(email, code):
    r.setex(email, 300, code)

def validate_confirmation_code(email, code):
    stored_code = r.get(email)
    if stored_code is None:
        return False
    if stored_code != code:
        return False
    r.delete(email)
    return True
