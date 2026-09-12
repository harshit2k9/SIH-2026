"""
Case-level access control. This is checked at the DB layer (not just in
Python), and every query here uses parameterized placeholders ($1, $2...)
so user-controlled values can NEVER be interpolated into SQL text.
"""
import uuid
from fastapi import HTTPException, status

from database import get_pool
from security.auth import AuthenticatedUser


async def require_upload_permission(user: AuthenticatedUser, case_id: uuid.UUID) -> None:
    pool = get_pool()
    
    # Parameterized query -- asyncpg sends $1/$2 as bind params over the wire.
    # We check if the user is the lead investigator OR belongs to the primary department of the case.
    allowed = await pool.fetchval(
        """
        SELECT 1
        FROM cases c
        WHERE c.id = $1
          AND (c.lead_investigator_id = $2 OR c.primary_department_id = (
              SELECT department_id FROM user_departments WHERE user_id = $2 AND is_primary = TRUE
          ))
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