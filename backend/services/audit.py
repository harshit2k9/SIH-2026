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
# This prevents hash-chain forking without locking the entire audit_log table.
AUDIT_CHAIN_LOCK_ID = 867530901 

def _compute_entry_hash(
    prev_hash: str | None,
    document_id: uuid.UUID | None,
    actor_id: uuid.UUID,
    action: str,
    details: dict[str, Any],
    timestamp: str,
) -> str:
    payload = json.dumps(
        {
            "prev_hash": prev_hash,
            "document_id": str(document_id) if document_id else None,
            "actor_id": str(actor_id),
            "action": action,
            "details": details,
            "timestamp": timestamp, # Cryptographically binds the time to the hash
        },
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

async def write_audit_entry(
    conn: asyncpg.Connection,
    actor_id: uuid.UUID,
    action: str,
    document_id: uuid.UUID | None = None,
    details: dict[str, Any] | None = None,
) -> str:
    """Writes a hash-chained entry to audit_log. Uses advisory locks for better concurrency."""
    details_payload = details or {}
    
    # Use ISO format timestamp for the hash payload
    current_time = datetime.now(timezone.utc).isoformat()

    # We do NOT use `async with conn.transaction()` here anymore. 
    # Because this is called INSIDE the outer transaction in documents.py, 
    # using a nested transaction (savepoint) with LOCK TABLE can cause lock escalation issues.
    # Instead, we use an advisory lock which is transaction-scoped automatically.
    
    await conn.execute("SELECT pg_advisory_xact_lock($1)", AUDIT_CHAIN_LOCK_ID)

    prev_hash: str | None = await conn.fetchval(
        "SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1"
    )

    entry_hash = _compute_entry_hash(
        prev_hash=prev_hash,
        document_id=document_id,
        actor_id=actor_id,
        action=action,
        details=details_payload,
        timestamp=current_time,
    )

    await conn.execute(
        """
        INSERT INTO audit_log (document_id, actor_id, action, details, prev_hash, entry_hash, created_at)
        VALUES ($1, $2, $3, $4::jsonb, $5, $6, $7)
        """,
        document_id,
        actor_id,
        action,
        json.dumps(details_payload, default=str), # default=str safely handles any leftover UUIDs in details
        prev_hash,
        entry_hash,
        current_time,
    )

    return entry_hash

async def log_audit_event(
    conn: asyncpg.Connection, 
    document_id: uuid.UUID, 
    user_id: uuid.UUID, 
    action: str, 
    ip_address: str,
    extra_details: dict[str, Any] | None = None,
) -> str:
    """Appends an immutable entry to the chain of custody audit log."""
    details = extra_details or {}
    details["ip_address"] = ip_address
    return await write_audit_entry(
        conn=conn,
        actor_id=user_id,
        action=action,
        document_id=document_id,
        details=details,
    )