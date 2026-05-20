import base64
from functools import lru_cache
from pathlib import Path

import httpx
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend

from app.core.exceptions.lti import LtiVerificationError



KEYS_DIR = Path(__file__).parent.parent.parent.parent / "keys"


@lru_cache()
def _load_private_key():
    with open(KEYS_DIR / "private.key", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def get_jwks() -> dict:
    public_numbers = _load_private_key().public_key().public_numbers()
    return {
        "keys": [
            {
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "kid": "app-key-1",
                "n": _int_to_base64url(public_numbers.n),
                "e": _int_to_base64url(public_numbers.e),
            }
        ]
    }


def verify_lti13_token(id_token: str, moodle_jwks_url: str, expected_aud: str) -> dict:
    try:
        response = httpx.get(moodle_jwks_url, timeout=10)
        response.raise_for_status()
        jwks = response.json()
    except httpx.HTTPError as e:
        raise LtiVerificationError(f"Failed to fetch Moodle JWKS: {e}")

    unverified_header = jwt.get_unverified_header(id_token)
    kid = unverified_header.get("kid")

    public_key = _find_public_key(jwks, kid)
    if not public_key:
        raise LtiVerificationError(f"No matching key found in Moodle JWKS for kid={kid}")

    try:
        decoded = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=expected_aud,
        )
    except jwt.ExpiredSignatureError:
        raise LtiVerificationError("id_token has expired")
    except jwt.InvalidAudienceError:
        raise LtiVerificationError(f"Invalid audience, expected {expected_aud}")
    except jwt.InvalidTokenError as e:
        raise LtiVerificationError(f"Invalid id_token: {e}")

    return decoded


def _find_public_key(jwks: dict, kid: str | None):
    keys = jwks.get("keys", [])
    if not keys:
        return None

    key_data = None
    if kid:
        key_data = next((k for k in keys if k.get("kid") == kid), None)
    if not key_data:
        key_data = keys[0]

    if key_data.get("kty") != "RSA":
        return None

    n = _base64url_to_int(key_data["n"])
    e = _base64url_to_int(key_data["e"])
    public_key = RSAPublicNumbers(e, n).public_key(default_backend())
    return public_key


def _int_to_base64url(i: int) -> str:
    hex_str = hex(i)[2:]
    if len(hex_str) % 2:
        hex_str = "0" + hex_str
    return base64.urlsafe_b64encode(bytes.fromhex(hex_str)).decode().rstrip("=")


def _base64url_to_int(s: str) -> int:
    padded = s + "=" * (4 - len(s) % 4)
    return int.from_bytes(base64.urlsafe_b64decode(padded), "big")