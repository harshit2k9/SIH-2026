"""
Append-only, hash-chained audit log. Each entry's hash incorporates the
previous entry's hash, so altering any historical row invalidates every
entry after it — this gives tamper-evidence for chain-of-custody, which
matters a lot for anything that might end up in front of a court.

IMPORTANT: writes here must happen inside the SAME transaction as the
document insert (see routers/documents.py) so we never have a document
row with no corresponding audit trail, or vice versa.
"""
#from typing import Any, Dict, Optional  
from typing import Any
import hashlib
import json

import asyncpg


def _compute_entry_hash(
    prev_hash: str | None,
    document_id: int | None,
    actor_id: int,
    action: str,
    details: dict[str, Any],
) -> str:
    payload = json.dumps(
        {
            "prev_hash": prev_hash,
            "document_id": document_id,
            "actor_id": actor_id,
            "action": action,
            "details": details,
        },
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

async def write_audit_entry(
    conn: asyncpg.Connection,
    actor_id: int,
    action: str,
    document_id: int | None = None,
    details: dict[str, Any] | None = None,
) -> str:
    """Writes a hash-chained entry to audit_log inside an explicit transaction block."""
    details_payload = details or {}

    # Open an explicit transaction block required for table locking
    async with conn.transaction():
        await conn.execute("LOCK TABLE audit_log IN SHARE ROW EXCLUSIVE MODE")

        prev_hash: str | None = await conn.fetchval(
            "SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1"
        )

        entry_hash = _compute_entry_hash(
            prev_hash=prev_hash,
            document_id=document_id,
            actor_id=actor_id,
            action=action,
            details=details_payload,
        )

        await conn.execute(
            """
            INSERT INTO audit_log (document_id, actor_id, action, details, prev_hash, entry_hash)
            VALUES ($1, $2, $3, $4::jsonb, $5, $6)
            """,
            document_id,
            actor_id,
            action,
            json.dumps(details_payload),
            prev_hash,
            entry_hash,
        )

    return entry_hash

'''
async def write_audit_entry(
    conn: asyncpg.Connection,
    document_id: int,
    actor_id: int,
    action: str,
    details: dict[str, Any],
) -> str:
    """Appends an immutable entry to the chain of custody audit log."""
    details_payload = details or {}
    await conn.execute("LOCK TABLE audit_log IN SHARE ROW EXCLUSIVE MODE")
    prev_hash: str | None = await conn.fetchval(
        "SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1"
    )

    entry_hash = _compute_entry_hash(
        prev_hash=prev_hash,
        document_id=document_id,
        actor_id=actor_id,
        action=action,
        details=details_payload,
    )

    await conn.execute(
        """
        INSERT INTO audit_log (document_id, actor_id, action, details, prev_hash, entry_hash)
        VALUES ($1, $2, $3, $4::jsonb, $5, $6)
        """,
        document_id, actor_id, action, json.dumps(details_payload), prev_hash, entry_hash,
    )
    return entry_hash
'''
async def log_audit_event(
    conn: asyncpg.Connection, 
    document_id: int, 
    user_id: int, 
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