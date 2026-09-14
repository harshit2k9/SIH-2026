"""
Case-level access control. Checked at the DB layer using parameterized queries.
"""
import uuid
from fastapi import HTTPException, status, Depends
import logging
from database import get_pool
from security.auth import AuthenticatedUser

logger = logging.getLogger(__name__)

async def require_upload_permission(user: AuthenticatedUser, case_id: uuid.UUID, pool) -> None:
    if "admin" in user.roles or "master_admin" in user.roles:
        return
        
    allowed = await pool.fetchval(
        """
        SELECT 1 FROM cases c
        WHERE c.id = $1
          AND (c.lead_investigator_id = $2 OR c.primary_department_id = (
              SELECT department_id FROM user_departments WHERE user_id = $2 AND is_primary = TRUE
          ))
          AND c.status != 'closed'
        """,
        case_id, user.id,
    )
    if not allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have upload permission for this case.")

async def require_case_access(user: AuthenticatedUser, case_id: uuid.UUID, pool) -> None:
    """Generic check for viewing, updating, or downloading documents in a case."""
    if "admin" in user.roles or "master_admin" in user.roles or "auditor" in user.roles:
        return
        
    allowed = await pool.fetchval(
        """
        SELECT 1 FROM cases c
        WHERE c.id = $1
          AND (c.lead_investigator_id = $2 OR c.primary_department_id = (
              SELECT department_id FROM user_departments WHERE user_id = $2 AND is_primary = TRUE
          ))
        """,
        case_id, user.id,
    )
    if not allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have access to this case.")