import hmac
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional
import logging

import os
import uuid
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings
from database import get_pool

# 1. Define the security scheme (THIS WAS MISSING)
security = HTTPBearer()

class AuthenticatedUser:
    """Represents the authenticated user extracted from the JWT payload."""
    def __init__(
        self, 
        id: uuid.UUID, 
        email: str, 
        roles: list[str], 
        department_id: uuid.UUID | None = None
    ):
        self.id = id
        self.email = email
        self.roles = roles
        self.department_id = department_id

async def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthenticatedUser:
    """
    Dependency to verify JWT token and return AuthenticatedUser object.
    Used in router endpoints via: user: AuthenticatedUser = Depends(verify_jwt)
    """
    token = credentials.credentials
    
    # Load public key for verification
    key_path = os.getenv("JWT_PUBLIC_KEY_PATH", "keys/public.pem")
    try:
        with open(key_path, "r") as f:
            public_key = f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT public key not found. Ensure keys are generated or mounted."
        )

    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )

    # OPTIONAL: Check revoked tokens (uncomment when you add the revoked_tokens table check)
    pool = get_pool()
    revoked = await pool.fetchval(
        "SELECT 1 FROM revoked_tokens WHERE token_jti = $1", 
        payload.get("jti")
     )
    if revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has been revoked"
        )

    return AuthenticatedUser(
        id=uuid.UUID(payload["sub"]),
        email=payload["email"],
        roles=payload.get("roles", []),
        department_id=uuid.UUID(payload["department_id"]) if payload.get("department_id") else None,
    )
def constant_time_equals(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())