"""
JWT verification dependency.

Security decisions:
- Algorithm is PINNED server-side to RS256. We never let the token's own
  header dictate which algorithm/key is used to verify it — that's the
  classic "alg confusion" forgery (e.g. swapping RS256 -> HS256 and using
  the public key as an HMAC secret).
- We only ever hold the PUBLIC key here. Token issuance (with the private
  key) happens in a separate, more locked-down auth service.
- Revocation is checked against a DB table (jti blacklist) so a
  compromised/logged-out token can be killed before its natural expiry.
- Any comparison of secret-like values uses hmac.compare_digest to avoid
  timing side-channels.
"""
import hmac
from datetime import datetime, timezone
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.database import get_pool

bearer_scheme = HTTPBearer(auto_error=True)


@lru_cache(maxsize=1)
def _load_public_key() -> str:
    with open(settings.JWT_PUBLIC_KEY_PATH, "r") as f:
        return f.read()


class AuthenticatedUser:
    def __init__(self, user_id: int, roles: list[str], jti: str):
        self.id = user_id
        self.roles = roles
        self.jti = jti


async def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> AuthenticatedUser:
    token = credentials.credentials

    # Pin the algorithm explicitly — do NOT read it from the token itself.
    try:
        payload = jwt.decode(
            token,
            _load_public_key(),
            algorithms=[settings.JWT_ALGORITHM],   # hard-coded allowlist of exactly one
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={"require": ["exp", "iat", "jti", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")
    except jwt.InvalidTokenError:
        # Deliberately generic message — don't leak *why* verification failed.
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    jti = payload["jti"]
    pool = get_pool()
    revoked = await pool.fetchval(
        "SELECT 1 FROM revoked_tokens WHERE jti = $1 AND expires_at > NOW()",
        jti,
    )
    if revoked:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token has been revoked")

    return AuthenticatedUser(
        user_id=int(payload["sub"]),
        roles=payload.get("roles", []),
        jti=jti,
    )


def constant_time_equals(a: str, b: str) -> bool:
    """Use for any secret/token/signature comparison to avoid timing attacks."""
    return hmac.compare_digest(a.encode(), b.encode())
