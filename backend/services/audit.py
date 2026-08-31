"""
Append-only, hash-chained audit log. Each entry's hash incorporates the
previous entry's hash, so altering any historical row invalidates every
entry after it — this gives tamper-evidence for chain-of-custody, which
matters a lot for anything that might end up in front of a court.

IMPORTANT: writes here must happen inside the SAME transaction as the
document insert (see routers/documents.py) so we never have a document
row with no corresponding audit trail, or vice versa.
"""
import hashlib
import json

import asyncpg


def _compute_entry_hash(prev_hash: str | None, document_id: int, actor_id: int,
                         action: str, details: dict) -> str:
    payload = json.dumps(
        {
            "prev_hash": prev_hash,
            "document_id": document_id,
            "actor_id": actor_id,
            "action": action,
            "details": details,
        },
        sort_keys=True,
    ).encode()
    return hashlib.sha256(payload).hexdigest()


async def write_audit_entry(
    conn: asyncpg.Connection,
    document_id: int,
    actor_id: int,
    action: str,
    details: dict,
) -> str:
    prev_hash = await conn.fetchval(
        "SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1"
    )
    entry_hash = _compute_entry_hash(prev_hash, document_id, actor_id, action, details)

    await conn.execute(
        """
        INSERT INTO audit_log (document_id, actor_id, action, details, prev_hash, entry_hash)
        VALUES ($1, $2, $3, $4::jsonb, $5, $6)
        """,
        document_id, actor_id, action, json.dumps(details), prev_hash, entry_hash,
    )
    return entry_hash
