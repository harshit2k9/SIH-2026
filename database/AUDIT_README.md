# Audit Ledger — chain_of_custody_logs Table

## Purpose
Records every sensitive action (view, upload, sign, delete) with who did it, when, and on what — using tamper-proof hash chaining.

## Security Layers
1. REVOKE UPDATE, DELETE — no one can modify or delete entries
2. Database Rules (block_deletes, block_updates) — extra engine-level protection
3. Hash Chaining — tampering breaks the chain and is detected
4. Automated Trigger Function (process_secure_audit_trail)

## Foreign Keys
Pending — users/cases/documents tables not yet available in this database. Will link once confirmed by team.

## Testing
hashtestt.js demonstrates full flow - verified working, tampering detected successfully.

## Status
✅ Table created and renamed to chain_of_custody_logs
✅ Tamper-proof rules active
✅ Hash chaining tested
⏳ Foreign key linking pending (users/cases/documents tables not in this database yet)