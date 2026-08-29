"""
Test helper: issues a valid RS256 JWT signed with keys/private.pem, matching
the claims our API's verify_jwt() expects (aud, iss, exp, jti, sub, roles).

This simulates what your real auth service would do at login time.
Run: python scripts/generate_test_token.py <user_id>
"""
import sys
import time
import uuid
from pathlib import Path

import jwt

# Resolve relative to the project root (one level up from this scripts/ folder),
# so this works no matter which directory you run the command from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRIVATE_KEY_PATH = PROJECT_ROOT / "keys" / "private.pem"


def main():
    user_id = sys.argv[1] if len(sys.argv) > 1 else "1"

    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()

    now = int(time.time())
    payload = {
        "sub": user_id,
        "roles": ["investigator"],
        "iat": now,
        "exp": now + 900,          # 15 minute expiry
        "jti": str(uuid.uuid4()),
        "aud": "sddms-api",
        "iss": "sddms-auth-service",
    }

    token = jwt.encode(payload, private_key, algorithm="RS256")
    print(token)


if __name__ == "__main__":
    main()
