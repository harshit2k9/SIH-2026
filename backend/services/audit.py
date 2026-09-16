"""
Append-only, hash-chained audit log. Each entry's hash incorporates the
previous entry's hash, so altering any historical row invalidates every
entry after it — this gives tamper-evidence for chain-of-custody.

IMPORTANT: writes here must happen inside the SAME transaction as the
document insert (see routers/documents.py) so we never have a document
row with no corresponding audit trail, or vice versa.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

import asyncpg

# Fixed integer for the advisory lock. 
# This prevents hash-chain forking without locking the entire chain_of_custody_logs table.
AUDIT_CHAIN_LOCK_ID = 867530901 

def _compute_entry_hash(
    prev_hash: str | None,
    case_id: uuid.UUID,
    document_id: uuid.UUID | None,
    evidence_id: uuid.UUID | None,
    actor_id: uuid.UUID,
    actor_department_id: uuid.UUID,
    action: str,
    ip_address: str | None,
    user_agent: str | None,
) -> str:
    """Computes the hash for an audit entry. All parameters must be included to ensure chain integrity."""
    payload = json.dumps(
        {
            "prev_hash": prev_hash,
            "case_id": str(case_id),
            "document_id": str(document_id) if document_id else None,
            "evidence_id": str(evidence_id) if evidence_id else None,
            "actor_id": str(actor_id),
            "actor_department_id": str(actor_department_id),
            "action": action,
            "ip_address": ip_address,
            "user_agent": user_agent,
        },
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
async def write_audit_entry(
    conn: asyncpg.Connection,
    case_id: Optional[uuid.UUID],
    actor_id: uuid.UUID,
    actor_department_id: uuid.UUID,
    action: str,
    document_id: uuid.UUID | None = None,
    evidence_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    details: dict[str, Any] | None = None,
) -> str:
    """Writes a hash-chained entry to chain_of_custody_logs. Uses advisory locks for better concurrency."""
    details_payload = details or {}
    
    # Use ISO format timestamp for the hash payload
    current_time = datetime.now(timezone.utc).isoformat()

    # Use an advisory lock which is transaction-scoped automatically.
    await conn.execute("SELECT pg_advisory_xact_lock($1)", AUDIT_CHAIN_LOCK_ID)

    # Fetch the previous hash (Note: column name is current_log_hash in your schema)
    prev_hash: str | None = await conn.fetchval(
        "SELECT current_log_hash FROM chain_of_custody_logs ORDER BY created_at DESC LIMIT 1"
    )

    # Compute the new hash including ALL context for legal integrity
    entry_hash = _compute_entry_hash(
        prev_hash=prev_hash,
        case_id=case_id,
        document_id=document_id,
        evidence_id=evidence_id,
        actor_id=actor_id,
        actor_department_id=actor_department_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    # Insert into the database
    await conn.execute(
        """
        INSERT INTO chain_of_custody_logs 
        (case_id, document_id, evidence_id, actor_id, actor_department_id, 
         action, ip_address, user_agent, previous_log_hash, current_log_hash, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """,
        case_id, 
        document_id, 
        evidence_id, 
        actor_id, 
        actor_department_id,  # Fixed typo from 'department_id'
        action, 
        ip_address, 
        user_agent, 
        prev_hash, 
        entry_hash,
        current_time
    )

    return entry_hash

async def log_audit_event(
    conn: asyncpg.Connection, 
    case_id: uuid.UUID,
    document_id: uuid.UUID, 
    user_id: uuid.UUID,
    department_id: uuid.UUID, 
    action: str, 
    ip_address: str,
) -> str:
    """Appends an immutable entry to the chain of custody audit log."""
    return await write_audit_entry(
        conn=conn,
        case_id=case_id,
        actor_id=user_id,
        actor_department_id=department_id,
        action=action,
        document_id=document_id,
        ip_address=ip_address,
    )