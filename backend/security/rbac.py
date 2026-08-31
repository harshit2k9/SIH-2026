"""
Case-level access control. This is checked at the DB layer (not just in
Python), and every query here uses parameterized placeholders ($1, $2...)
so user-controlled values can NEVER be interpolated into SQL text.
"""
from fastapi import HTTPException, status

from database import get_pool
from security.auth import AuthenticatedUser


async def require_upload_permission(user: AuthenticatedUser, case_id: int) -> None:
    pool = get_pool()
    # Parameterized query -- asyncpg sends $1/$2 as bind params over the wire,
    # never string-concatenated. This closes the SQL injection vector entirely
    # for this call, regardless of what case_id/user.id contain.
    allowed = await pool.fetchval(
        """
        SELECT 1
        FROM case_assignments ca
        JOIN cases c ON c.id = ca.case_id
        WHERE ca.case_id = $1
          AND ca.user_id = $2
          AND ca.can_upload = TRUE
          AND c.status != 'closed'
        """,
        case_id,
        user.id,
    )
    if not allowed:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You do not have upload permission for this case.",
        )
