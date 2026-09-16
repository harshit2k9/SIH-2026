-- 07_db_encryption.sql

BEGIN;

-- PostgreSQL cryptographic functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

COMMIT;

-- ============================================================
-- TEST 1: Confirm pgcrypto is installed
-- ============================================================
SELECT extname, extversion
FROM pg_extension
WHERE extname = 'pgcrypto';


-- ============================================================
-- TEST 2: Demonstrate field-level encryption
-- ============================================================
-- IMPORTANT:
-- This is a DEMO only. Never hard-code a production encryption
-- key in SQL, source code, GitHub, or the database.

CREATE TEMP TABLE encryption_demo (
    id UUID PRIMARY KEY,
    encrypted_value BYTEA NOT NULL
);

INSERT INTO encryption_demo (id, encrypted_value)
VALUES (
    gen_random_uuid(),
    pgp_sym_encrypt(
        'Sensitive demonstration value',
        'DEMO_ONLY_KEY'
    )
);

-- The stored value is encrypted binary data.
SELECT id, encrypted_value
FROM encryption_demo;


-- ============================================================
-- TEST 3: Decrypt the demonstration value
-- ============================================================
SELECT
    id,
    pgp_sym_decrypt(encrypted_value, 'DEMO_ONLY_KEY')
        AS decrypted_value
FROM encryption_demo;


-- ============================================================
-- TEST 4: Verify that encrypted value is not plaintext
-- ============================================================
SELECT
    id,
    CASE
        WHEN encrypted_value::text LIKE '%Sensitive demonstration value%'
            THEN 'PLAINTEXT FOUND'
        ELSE 'ENCRYPTED DATA'
    END AS storage_check
FROM encryption_demo;


-- ============================================================
-- PROJECT DESIGN CHECK
-- ============================================================
-- Your document_versions table already contains:
--   storage_uri
--   sha256_checksum
--   kms_key_id
--
-- sha256_checksum = integrity/tamper detection
-- kms_key_id      = identifier for the encryption key
--
-- The actual document encryption key should be managed by the
-- backend/KMS, not stored directly in this SQL file.


-- ============================================================
-- OPTIONAL: Check the KMS key identifiers currently stored
-- ============================================================
SELECT
    id,
    document_id,
    version_number,
    kms_key_id
FROM document_versions
ORDER BY document_id, version_number;


-- ============================================================
-- SECURITY NOTES
-- ============================================================
-- 1. Use TLS/SSL for PostgreSQL client-server communication.
-- 2. Do not store production encryption keys in PostgreSQL.
-- 3. Do not commit encryption keys to GitHub.
-- 4. Use a KMS/secret-management system for production keys.
-- 5. Hashing and encryption are different:
--      SHA-256 -> integrity
--      Encryption -> confidentiality
-- 6. Document/PDF/image encryption should happen in the
--    application/storage layer, with kms_key_id recorded here.
