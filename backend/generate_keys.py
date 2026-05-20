from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

KEYS_DIR = Path(__file__).parent / "keys"
KEYS_DIR.mkdir(exist_ok=True)

private_key_path = KEYS_DIR / "private.key"
public_key_path = KEYS_DIR / "public.key"

if private_key_path.exists():
    print("Keys already exist, skipping.")
else:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_key_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public_key_path.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    print("Keys generated in ./keys/")