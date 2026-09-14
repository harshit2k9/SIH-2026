import hmac
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional
import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import logging
from config import settings
from database import get_pool

bearer_scheme = HTTPBearer(auto_error=True)

@lru_cache(maxsize=1)
def _load_public_key() -> str:
    try:
        with open(settings.JWT_PUBLIC_KEY_PATH, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "JWT Public Key missing. Restart backend to generate.")

class AuthenticatedUser:
    def __init__(self, user_id: uuid.UUID, roles: list[str], token_jti: str, department_id: Optional[uuid.UUID] = None):
        self.id = user_id
        self.roles = roles
        self.token_jti = token_jti
        self.department_id = department_id

async def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> AuthenticatedUser:
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            _load_public_key(),
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={"require": ["exp", "iat", "jti", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid credentials: {str(e)}")

    # Robust UUID parsing
    try:
        user_uuid = uuid.UUID(payload["sub"])
    except (ValueError, AttributeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid user ID format in token")

    token_jti = payload["jti"]
    
    # Optional: Check revocation (gracefully fail if table doesn't exist yet)
    pool = get_pool()
    try:
        revoked = await pool.fetchval(
            "SELECT 1 FROM revoked_tokens WHERE token_jti = $1 AND expires_at > NOW()",
            token_jti,
        )
        if revoked:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token has been revoked")
    except HTTPException:
        raise  # Re-raise auth errors
    except Exception as e:
        # Fail closed in production - log and reject
        logging.getLogger("security").error(f"Revocation check failed: {e}")
        if os.getenv("ENVIRONMENT") == "production":
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "Security system temporarily unavailable"
            )
        # In dev, continue if table missing
        logging.getLogger("security").warning("Revocation table missing - continuing in dev mode")
    # Validate user exists and is active
    user_record = await pool.fetchrow(
        "SELECT id, is_active FROM public.users WHERE id = $1",
        user_uuid
    )

    if not user_record or not user_record['is_active']:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "User not found or inactive"
        )
    

    # Extract optional department_id
    dept_id_str = payload.get("department_id")
    dept_uuid = None
    if dept_id_str:
        try:
            dept_uuid = uuid.UUID(dept_id_str)
        except ValueError:
            pass
    
    return AuthenticatedUser(
        user_id=user_uuid,
        roles=payload.get("roles", []),
        token_jti=token_jti,
        department_id=dept_uuid
    )

def constant_time_equals(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())