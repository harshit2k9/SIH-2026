"""
Test helper: issues a valid RS256 JWT signed with keys/private.pem, matching
the claims our API's verify_jwt() expects (aud, iss, exp, jti, sub, roles).

This simulates what your real auth service would do at login time.
Run: python scripts/generate_test_token.py <user_id>
"""
import os
import sys
import time
import uuid
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Resolve relative to project root regardless of execution location
PROJECT_ROOT = Path(__file__).resolve().parent.parent
KEYS_DIR = PROJECT_ROOT / "keys"
PRIVATE_KEY_PATH = KEYS_DIR / "private.pem"
PUBLIC_KEY_PATH = KEYS_DIR / "public.pem"


def ensure_jwt_keys():
    """Generates RSA key pair in the keys/ directory if missing."""
    if PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists():
        return

    KEYS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate Private Key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    # Generate Public Key
    public_key = private_key.public_key()
    with open(PUBLIC_KEY_PATH, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )


def main():
    # Guarantee keys exist prior to loading private.pem
    ensure_jwt_keys()

    user_id = sys.argv[1] if len(sys.argv) > 1 else "1"

    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()

    now = int(time.time())
    payload = {
        "sub": user_id,
        "roles": ["investigator"],
        "iat": now,
        "exp": now + 900,  # 15 minute expiry
        "jti": str(uuid.uuid4()),
        "aud": "sddms-api",
        "iss": "sddms-auth-service",
    }

    token = jwt.encode(payload, private_key, algorithm="RS256")
    print(token)


if __name__ == "__main__":
    main()