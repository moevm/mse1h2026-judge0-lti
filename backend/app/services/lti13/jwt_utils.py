import jwt
from cryptography.hazmat.primitives import serialization
from pathlib import Path
from datetime import datetime, timedelta, timezone

KEYS_DIR = Path(__file__).parent.parent.parent.parent / "keys"

with open(KEYS_DIR / "private.key", "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(
        f.read(),
        password=None,
    )

with open(KEYS_DIR / "public.key", "rb") as f:
    PUBLIC_KEY_PEM = f.read()

def verify_jwt(token: str, expected_aud: str) -> dict:
    """Проверка JWT от Moodle"""
    # Публичный ключ Moodle нужно получить из их JWKS (позже)
    # Пока заглушка
    return jwt.decode(token, options={"verify_signature": False})

def get_jwks():
    """JWKS для Moodle"""
    public_numbers = PRIVATE_KEY.public_key().public_numbers()
    return {
        "keys": [{
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "kid": "judge0-key-1",
            "n": int_to_base64url(public_numbers.n),
            "e": int_to_base64url(public_numbers.e),
        }]
    }

def int_to_base64url(i: int) -> str:
    """Конвертирует int в base64url"""
    from base64 import urlsafe_b64encode
    hex_str = hex(i)[2:]
    if len(hex_str) % 2:
        hex_str = "0" + hex_str
    bytes_data = bytes.fromhex(hex_str)
    return urlsafe_b64encode(bytes_data).decode().rstrip("=")
