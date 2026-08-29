-- ============================================================
-- Secure Digital Document Management System - PostgreSQL Schema
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL PRIMARY KEY,
    username    VARCHAR(100) UNIQUE NOT NULL,
    role        VARCHAR(50)  NOT NULL,             -- e.g. 'investigator', 'admin', 'reviewer'
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cases (
    id          BIGSERIAL PRIMARY KEY,
    case_number VARCHAR(100) UNIQUE NOT NULL,
    title       VARCHAR(255) NOT NULL,
    status      VARCHAR(20)  NOT NULL DEFAULT 'open',
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Who is allowed to upload/view documents for which case
CREATE TABLE IF NOT EXISTS case_assignments (
    id          BIGSERIAL PRIMARY KEY,
    case_id     BIGINT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    can_upload  BOOLEAN NOT NULL DEFAULT FALSE,
    can_view    BOOLEAN NOT NULL DEFAULT TRUE,
    assigned_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (case_id, user_id)
);

-- ---------------------------------------------------------------
-- Core documents table (your fields, unmodified, + integrity hash)
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
    id                  BIGSERIAL PRIMARY KEY,
    case_id             BIGINT NOT NULL REFERENCES cases(id),
    title               VARCHAR(255) NOT NULL,
    document_type       VARCHAR(50)  NOT NULL,
    original_filename   VARCHAR(255) NOT NULL,
    uploaded_by         BIGINT NOT NULL REFERENCES users(id),
    status              VARCHAR(20)  NOT NULL DEFAULT 'active',
    storage_key         TEXT         NOT NULL,      -- path/key inside MinIO bucket
    mime_type           VARCHAR(100) NOT NULL,
    file_size_bytes     BIGINT       NOT NULL,
    sha256_hash         CHAR(64)     NOT NULL,       -- integrity fingerprint, indexed for dedupe/verification
    created_at          TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_case_id      ON documents(case_id);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by  ON documents(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_documents_sha256       ON documents(sha256_hash);

-- ---------------------------------------------------------------
-- Hash-chained, append-only audit log (chain-of-custody evidence)
-- Each row's entry_hash = SHA256(prev_hash || serialized row data)
-- Tampering with any historical row breaks every subsequent hash.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_log (
    id           BIGSERIAL PRIMARY KEY,
    document_id  BIGINT REFERENCES documents(id),
    actor_id     BIGINT NOT NULL REFERENCES users(id),
    action       VARCHAR(50) NOT NULL,          -- UPLOAD, VIEW, DOWNLOAD, ARCHIVE, DELETE_REQUEST...
    details      JSONB,
    prev_hash    CHAR(64),
    entry_hash   CHAR(64) NOT NULL,
    created_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_document_id ON audit_log(document_id);

-- Revoked JWTs (jti blacklist) — avoids a hard Redis dependency for the hackathon build.
-- Swap for Redis SET with TTL in production for O(1) lookups at scale.
CREATE TABLE IF NOT EXISTS revoked_tokens (
    jti         UUID PRIMARY KEY,
    revoked_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMP NOT NULL
);
