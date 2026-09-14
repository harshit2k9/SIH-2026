"""
Append-only, hash-chained audit log. Each entry's hash incorporates the
previous entry's hash, so altering any historical row invalidates every
entry after it — providing tamper-evidence for chain-of-custody.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any
import asyncpg

# Fixed integer for the advisory lock to prevent hash-chain forking
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
    details: dict[str, Any],
    timestamp: str,
) -> str:
    """Computes SHA-256 hash of the audit payload. All fields are included to prevent contextual tampering."""
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
            "details": details,
            "timestamp": timestamp,
        },
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

async def write_audit_entry(
    conn: asyncpg.Connection,
    case_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_department_id: uuid.UUID,
    action: str,
    document_id: uuid.UUID | None = None,
    evidence_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    details: dict[str, Any] | None = None,
) -> str:
    """Writes a hash-chained entry to chain_of_custody_logs using advisory locks."""
    details_payload = details or {}
    current_time = datetime.now(timezone.utc).isoformat()
    
    # Transaction-scoped advisory lock prevents race conditions in hash chain generation
    await conn.execute("SELECT pg_advisory_xact_lock($1)", AUDIT_CHAIN_LOCK_ID)
    
    prev_hash: str | None = await conn.fetchval(
        "SELECT current_log_hash FROM chain_of_custody_logs ORDER BY created_at DESC LIMIT 1"
    )
    
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
        details=details_payload,
        timestamp=current_time,
    )
    
    await conn.execute(
        """
        INSERT INTO chain_of_custody_logs 
        (case_id, document_id, evidence_id, actor_id, actor_department_id, 
         action, ip_address, user_agent, previous_log_hash, current_log_hash, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """,
        case_id, document_id, evidence_id, actor_id, actor_department_id,
        action, ip_address, user_agent, prev_hash, entry_hash, current_time
    )
    return entry_hash

async def log_audit_event(
    conn: asyncpg.Connection,
    case_id: uuid.UUID,
    document_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_department_id: uuid.UUID,
    action: str,
    ip_address: str,
    user_agent: str | None = None,
    extra_details: dict[str, Any] | None = None,
) -> str:
    """Wrapper for simple audit events without evidence_id."""
    details = extra_details or {}
    details["ip_address"] = ip_address
    return await write_audit_entry(
        conn=conn,
        case_id=case_id,
        document_id=document_id,
        actor_id=actor_id,
        actor_department_id=actor_department_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
    )