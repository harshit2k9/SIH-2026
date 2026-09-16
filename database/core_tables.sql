-- ============================================================
-- 01_create_tables.sql
-- Secure Legal / Investigation Document Management System
-- PostgreSQL
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ============================================================
-- 1. DEPARTMENTS
-- ============================================================

CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    code VARCHAR UNIQUE NOT NULL,
    parent_id UUID REFERENCES departments(id),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID
);


-- ============================================================
-- 2. USERS
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    badge_number VARCHAR UNIQUE,
    security_clearance_level INT,
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);


-- ============================================================
-- 3. ROLES
-- ============================================================

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR UNIQUE NOT NULL,
    permissions JSONB,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);


-- ============================================================
-- 4. USER_DEPARTMENTS
-- ============================================================

CREATE TABLE user_departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    department_id UUID NOT NULL REFERENCES departments(id),
    role_id UUID NOT NULL REFERENCES roles(id),

    is_primary BOOLEAN DEFAULT FALSE,
    assigned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (user_id, department_id, role_id)
);


-- ============================================================
-- 5. EVIDENCE_PROVIDERS
-- ============================================================

CREATE TABLE evidence_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_type VARCHAR NOT NULL,
    full_name_or_org VARCHAR NOT NULL,
    contact_info JSONB,
    identification_number VARCHAR,
    clearance_verified BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);


-- ============================================================
-- 6. CASES
-- ============================================================

CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number VARCHAR UNIQUE NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    classification_level INT,
    status VARCHAR NOT NULL,

    primary_department_id UUID NOT NULL
        REFERENCES departments(id),

    lead_investigator_id UUID
        REFERENCES users(id),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);


-- ============================================================
-- 7. EVIDENCE_ITEMS
-- ============================================================

CREATE TABLE evidence_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    case_id UUID NOT NULL
        REFERENCES cases(id),

    evidence_number VARCHAR UNIQUE NOT NULL,

    provider_id UUID
        REFERENCES evidence_providers(id),

    title VARCHAR NOT NULL,
    evidence_type VARCHAR NOT NULL,
    storage_location VARCHAR,
    current_status VARCHAR NOT NULL,

    seized_at TIMESTAMPTZ,

    seized_by_user_id UUID
        REFERENCES users(id),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);


-- ============================================================
-- 8. EVIDENCE_CUSTODY_TRANSFERS
-- ============================================================

CREATE TABLE evidence_custody_transfers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    evidence_item_id UUID NOT NULL
        REFERENCES evidence_items(id),

    released_by_user_id UUID
        REFERENCES users(id),

    received_by_user_id UUID
        REFERENCES users(id),

    purpose TEXT,

    transfer_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    physical_condition_notes TEXT
);


-- ============================================================
-- 9. DOCUMENTS
-- ============================================================

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    case_id UUID NOT NULL
        REFERENCES cases(id),

    evidence_item_id UUID
        REFERENCES evidence_items(id),

    document_number VARCHAR UNIQUE NOT NULL,
    title VARCHAR NOT NULL,
    document_type VARCHAR NOT NULL,

    confidentiality_level INT,
    current_version INT,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    is_locked BOOLEAN DEFAULT FALSE
);


-- ============================================================
-- 10. DOCUMENT_VERSIONS
-- ============================================================

CREATE TABLE document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_id UUID NOT NULL
        REFERENCES documents(id),

    version_number INT NOT NULL,

    storage_uri VARCHAR NOT NULL,
    file_size_bytes BIGINT,
    file_mime_type VARCHAR,
    sha256_checksum VARCHAR,
    kms_key_id VARCHAR,

    uploaded_by UUID REFERENCES users(id),
    uploaded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (document_id, version_number)
);


-- ============================================================
-- 11. DOCUMENT_AI_METADATA
-- ============================================================

CREATE TABLE document_ai_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    version_id UUID NOT NULL
        REFERENCES document_versions(id),

    ocr_extracted_text TEXT,
    ai_summary TEXT,
    extracted_entities JSONB,
    vector_embedding_id VARCHAR,
    processed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id),

    UNIQUE (version_id)
);


-- ============================================================
-- 12. INTER_DEPARTMENT_SHARES
-- ============================================================

CREATE TABLE inter_department_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_id UUID NOT NULL
        REFERENCES documents(id),

    source_department_id UUID NOT NULL
        REFERENCES departments(id),

    target_department_id UUID NOT NULL
        REFERENCES departments(id),

    granted_by_user_id UUID NOT NULL
        REFERENCES users(id),

    access_level VARCHAR NOT NULL,
    reason TEXT,

    valid_from TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,

    status VARCHAR NOT NULL,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);


-- ============================================================
-- 13. CHAIN_OF_CUSTODY_LOGS
-- Audit/history table — intentionally no updated_by/updated_at
-- ============================================================

CREATE TABLE chain_of_custody_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    case_id UUID NOT NULL
        REFERENCES cases(id),

    document_id UUID
        REFERENCES documents(id),

    evidence_id UUID
        REFERENCES evidence_items(id),

    actor_id UUID NOT NULL
        REFERENCES users(id),

    actor_department_id UUID NOT NULL
        REFERENCES departments(id),

    action VARCHAR NOT NULL,

    ip_address VARCHAR,
    user_agent TEXT,

    previous_log_hash VARCHAR,
    current_log_hash VARCHAR,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);


-- ============================================================
-- 14. DIGITAL_SIGNATURES
-- ============================================================

CREATE TABLE digital_signatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_version_id UUID NOT NULL
        REFERENCES document_versions(id),

    signer_id UUID NOT NULL
        REFERENCES users(id),

    signer_department_id UUID NOT NULL
        REFERENCES departments(id),

    signature_hash TEXT NOT NULL,
    cert_serial_number VARCHAR,
    timestamp_seal TEXT,

    signed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);


-- ============================================================
-- 15. COURT_BENCHES
-- ============================================================

CREATE TABLE court_benches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    department_id UUID NOT NULL
        REFERENCES departments(id),

    bench_name VARCHAR NOT NULL,
    bench_type VARCHAR NOT NULL,

    presiding_judge_id UUID NOT NULL
        REFERENCES users(id),

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);


-- ============================================================
-- 16. COURT_HEARINGS
-- ============================================================

CREATE TABLE court_hearings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    case_id UUID NOT NULL
        REFERENCES cases(id),

    bench_id UUID NOT NULL
        REFERENCES court_benches(id),

    hearing_date TIMESTAMPTZ NOT NULL,
    hearing_purpose VARCHAR NOT NULL,
    status VARCHAR NOT NULL,

    adjournment_reason TEXT,
    next_hearing_date TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);


-- ============================================================
-- 17. ORDER_SHEETS
-- ============================================================

CREATE TABLE order_sheets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    case_id UUID NOT NULL
        REFERENCES cases(id),

    hearing_id UUID UNIQUE NOT NULL
        REFERENCES court_hearings(id),

    order_sheet_number VARCHAR UNIQUE NOT NULL,

    proceeding_summary TEXT,
    advocates_present JSONB,
    accused_presence_status VARCHAR,

    document_id UUID
        REFERENCES documents(id),

    recorded_by_user_id UUID
        REFERENCES users(id),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);


-- ============================================================
-- 18. COURT_ORDERS
-- ============================================================

CREATE TABLE court_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    case_id UUID NOT NULL
        REFERENCES cases(id),

    hearing_id UUID
        REFERENCES court_hearings(id),

    order_number VARCHAR UNIQUE NOT NULL,
    order_type VARCHAR NOT NULL,
    order_summary TEXT,

    issuing_judge_id UUID NOT NULL
        REFERENCES users(id),

    document_id UUID UNIQUE
        REFERENCES documents(id),

    effective_date TIMESTAMPTZ,
    expiry_date TIMESTAMPTZ,

    enforcement_status VARCHAR,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);


-- ============================================================
-- 19. WARRANTS_AND_SUMMONS
-- ============================================================

CREATE TABLE warrants_and_summons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    court_order_id UUID NOT NULL
        REFERENCES court_orders(id),

    case_id UUID NOT NULL
        REFERENCES cases(id),

    notice_type VARCHAR NOT NULL,

    target_person_details JSONB,

    assigned_police_station_id UUID
        REFERENCES departments(id),

    executing_officer_id UUID
        REFERENCES users(id),

    execution_status VARCHAR NOT NULL,

    return_date TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);


-- ============================================================
-- 20. CASE_STAGE_HISTORY
-- History table — uses changed_at/changed_by_user_id
-- ============================================================

CREATE TABLE case_stage_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    case_id UUID NOT NULL
        REFERENCES cases(id),

    previous_stage VARCHAR,
    new_stage VARCHAR NOT NULL,

    changed_by_order_id UUID
        REFERENCES court_orders(id),

    changed_by_user_id UUID NOT NULL
        REFERENCES users(id),

    remarks TEXT,

    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- END OF 20 TABLES
-- ============================================================