"""
Generate a test JWT for development/testing.
Bypasses the HTML login flow to let you test API endpoints directly.

Usage:
    python -m scripts.generate_test_token
    python -m scripts.generate_test_token --user 20000000-0000-0000-0000-000000000001
"""
import os
import sys
import uuid
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add parent dir to path so we can import config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import jwt
from config import settings

def generate_test_jwt(
    operational_user_id: str = "20000000-0000-0000-0000-000000000001",
    email: str = "rajesh.sharma@police.gov.in",
    role: str = "investigator",
    department_id: str = "10000000-0000-0000-0000-000000000001",
    expires_minutes: int = 30,
) -> str:
    """Generate a JWT matching the real /api/auth/token payload structure."""
    
    now = datetime.utcnow()
    payload = {
        "sub": operational_user_id,
        "email": email,
        "roles": [role],
        "department_id": department_id,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
        "jti": str(uuid.uuid4()),
        "aud": settings.JWT_AUDIENCE,
        "iss": settings.JWT_ISSUER,
    }
    
    # Load the auto-generated private key
    key_path = Path(settings.JWT_PRIVATE_KEY_PATH)
    if not key_path.exists():
        raise FileNotFoundError(
            f"Private key not found at {key_path}. "
            "Run the backend once to auto-generate it, or set JWT_PRIVATE_KEY_PATH."
        )
    
    with open(key_path, "r") as f:
        private_key = f.read()
    
    return jwt.encode(payload, private_key, algorithm="RS256")


def main():
    parser = argparse.ArgumentParser(description="Generate a test JWT")
    parser.add_argument(
        "--user", default="20000000-0000-0000-0000-000000000001",
        help="Operational user UUID (from test_database.sql)"
    )
    parser.add_argument(
        "--role", default="investigator",
        choices=["admin", "investigator", "judge", "forensic_analyst", "super_admin"],
        help="Role to assign"
    )
    parser.add_argument(
        "--expires", type=int, default=30,
        help="Token lifetime in minutes"
    )
    args = parser.parse_args()
    
    token = generate_test_jwt(
        operational_user_id=args.user,
        role=args.role,
        expires_minutes=args.expires,
    )
    
    print("\n" + "=" * 80)
    print("🔑 TEST JWT GENERATED")
    print("=" * 80)
    print(f"\nUser ID:      {args.user}")
    print(f"Role:         {args.role}")
    print(f"Expires in:   {args.expires} minutes")
    print(f"\n📋 Copy-paste this token:\n")
    print(token)
    print(f"\n💡 Use it like this:\n")
    print(f'curl -H "Authorization: Bearer {token}" \\')
    print(f'     http://localhost:8000/documents/case/60000000-0000-0000-0000-000000000001')
    print("=" * 80)


if __name__ == "__main__":
    main()