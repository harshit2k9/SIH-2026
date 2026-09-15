-- 01_create_tables.sql
BEGIN;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE departments (
 id UUID PRIMARY KEY, name VARCHAR(255) NOT NULL, code VARCHAR(50) NOT NULL UNIQUE,
 parent_id UUID REFERENCES departments(id), created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE users (
 id UUID PRIMARY KEY, full_name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL UNIQUE,
 badge_number VARCHAR(100) UNIQUE, security_clearance_level INT NOT NULL,
 is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE roles (
 id UUID PRIMARY KEY, name VARCHAR(100) NOT NULL UNIQUE, permissions JSONB NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE user_departments (
 id UUID PRIMARY KEY, user_id UUID NOT NULL REFERENCES users(id),
 department_id UUID NOT NULL REFERENCES departments(id), role_id UUID NOT NULL REFERENCES roles(id),
 is_primary BOOLEAN NOT NULL DEFAULT FALSE, assigned_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT uq_user_department_role UNIQUE(user_id, department_id, role_id)
);
CREATE TABLE evidence_providers (
 id UUID PRIMARY KEY, provider_type VARCHAR(100) NOT NULL, full_name_or_org VARCHAR(255) NOT NULL,
 contact_info JSONB, identification_number VARCHAR(100), clearance_verified BOOLEAN NOT NULL DEFAULT FALSE,
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE cases (
 id UUID PRIMARY KEY, case_number VARCHAR(100) NOT NULL UNIQUE, title VARCHAR(255) NOT NULL,
 description TEXT, classification_level INT NOT NULL, status VARCHAR(50) NOT NULL,
 primary_department_id UUID NOT NULL REFERENCES departments(id), lead_investigator_id UUID REFERENCES users(id),
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by UUID REFERENCES users(id)
);
CREATE TABLE evidence_items (
 id UUID PRIMARY KEY, case_id UUID NOT NULL REFERENCES cases(id), evidence_number VARCHAR(100) NOT NULL UNIQUE,
 provider_id UUID REFERENCES evidence_providers(id), title VARCHAR(255) NOT NULL, evidence_type VARCHAR(100) NOT NULL,
 storage_location VARCHAR(500), current_status VARCHAR(100) NOT NULL, seized_at TIMESTAMPTZ,
 seized_by_user_id UUID REFERENCES users(id), created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 created_by UUID REFERENCES users(id)
);
CREATE TABLE evidence_custody_transfers (
 id UUID PRIMARY KEY, evidence_item_id UUID NOT NULL REFERENCES evidence_items(id),
 released_by_user_id UUID NOT NULL REFERENCES users(id), received_by_user_id UUID NOT NULL REFERENCES users(id),
 purpose TEXT NOT NULL, transfer_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 physical_condition_notes TEXT
);
CREATE TABLE documents (
 id UUID PRIMARY KEY, case_id UUID NOT NULL REFERENCES cases(id), evidence_item_id UUID REFERENCES evidence_items(id),
 document_number VARCHAR(100) NOT NULL UNIQUE, title VARCHAR(255) NOT NULL, document_type VARCHAR(100) NOT NULL,
 confidentiality_level INT NOT NULL, current_version INT NOT NULL DEFAULT 1,
 created_by UUID NOT NULL REFERENCES users(id), created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_by UUID REFERENCES users(id), updated_at TIMESTAMPTZ, is_locked BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE document_versions (
 id UUID PRIMARY KEY, document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
 version_number INT NOT NULL, storage_uri VARCHAR(1000) NOT NULL, file_size_bytes BIGINT NOT NULL,
 file_mime_type VARCHAR(255) NOT NULL, sha256_checksum VARCHAR(255) NOT NULL, kms_key_id VARCHAR(255),
 uploaded_by UUID NOT NULL REFERENCES users(id), uploaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT uq_document_version UNIQUE(document_id, version_number)
);
CREATE TABLE document_ai_metadata (
 id UUID PRIMARY KEY, version_id UUID NOT NULL UNIQUE REFERENCES document_versions(id) ON DELETE CASCADE,
 ocr_extracted_text TEXT, ai_summary TEXT, extracted_entities JSONB, vector_embedding_id VARCHAR(255),
 processed_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by UUID REFERENCES users(id)
);
CREATE TABLE inter_department_shares (
 id UUID PRIMARY KEY, document_id UUID NOT NULL REFERENCES documents(id),
 source_department_id UUID NOT NULL REFERENCES departments(id), target_department_id UUID NOT NULL REFERENCES departments(id),
 granted_by_user_id UUID NOT NULL REFERENCES users(id), access_level VARCHAR(100) NOT NULL, reason TEXT,
 valid_from TIMESTAMPTZ NOT NULL, expires_at TIMESTAMPTZ, status VARCHAR(50) NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by UUID REFERENCES users(id)
);
CREATE TABLE chain_of_custody_logs (
 id UUID PRIMARY KEY, case_id UUID NOT NULL REFERENCES cases(id), document_id UUID REFERENCES documents(id),
 evidence_id UUID REFERENCES evidence_items(id), actor_id UUID NOT NULL REFERENCES users(id),
 actor_department_id UUID NOT NULL REFERENCES departments(id), action VARCHAR(100) NOT NULL,
 ip_address VARCHAR(100), user_agent TEXT, previous_log_hash VARCHAR(255), current_log_hash VARCHAR(255),
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by UUID REFERENCES users(id)
);
CREATE TABLE digital_signatures (
 id UUID PRIMARY KEY, document_version_id UUID NOT NULL REFERENCES document_versions(id),
 signer_id UUID NOT NULL REFERENCES users(id), signer_department_id UUID NOT NULL REFERENCES departments(id),
 signature_hash TEXT NOT NULL, cert_serial_number VARCHAR(255), timestamp_seal TEXT, signed_at TIMESTAMPTZ NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by UUID REFERENCES users(id)
);
CREATE TABLE court_benches (
 id UUID PRIMARY KEY, department_id UUID NOT NULL REFERENCES departments(id), bench_name VARCHAR(255) NOT NULL,
 bench_type VARCHAR(100) NOT NULL, presiding_judge_id UUID NOT NULL REFERENCES users(id),
 is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 created_by UUID REFERENCES users(id)
);
CREATE TABLE court_hearings (
 id UUID PRIMARY KEY, case_id UUID NOT NULL REFERENCES cases(id), bench_id UUID NOT NULL REFERENCES court_benches(id),
 hearing_date TIMESTAMPTZ NOT NULL, hearing_purpose VARCHAR(255), status VARCHAR(100) NOT NULL,
 adjournment_reason TEXT, next_hearing_date TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 created_by UUID REFERENCES users(id)
);
CREATE TABLE order_sheets (
 id UUID PRIMARY KEY, case_id UUID NOT NULL REFERENCES cases(id),
 hearing_id UUID NOT NULL UNIQUE REFERENCES court_hearings(id), order_sheet_number VARCHAR(100) NOT NULL UNIQUE,
 proceeding_summary TEXT, advocates_present JSONB, accused_presence_status VARCHAR(100),
 document_id UUID REFERENCES documents(id), recorded_by_user_id UUID NOT NULL REFERENCES users(id),
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by UUID REFERENCES users(id)
);
CREATE TABLE court_orders (
 id UUID PRIMARY KEY, case_id UUID NOT NULL REFERENCES cases(id), hearing_id UUID NOT NULL REFERENCES court_hearings(id),
 order_number VARCHAR(100) NOT NULL UNIQUE, order_type VARCHAR(100) NOT NULL, order_summary TEXT,
 issuing_judge_id UUID NOT NULL REFERENCES users(id), document_id UUID UNIQUE REFERENCES documents(id),
 effective_date TIMESTAMPTZ, expiry_date TIMESTAMPTZ, enforcement_status VARCHAR(100),
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by UUID REFERENCES users(id)
);
CREATE TABLE warrants_and_summons (
 id UUID PRIMARY KEY, court_order_id UUID NOT NULL REFERENCES court_orders(id), case_id UUID NOT NULL REFERENCES cases(id),
 notice_type VARCHAR(100) NOT NULL, target_person_details JSONB, assigned_police_station_id UUID REFERENCES departments(id),
 executing_officer_id UUID REFERENCES users(id), execution_status VARCHAR(100), return_date TIMESTAMPTZ,
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by UUID REFERENCES users(id)
);
CREATE TABLE case_stage_history (
 id UUID PRIMARY KEY, case_id UUID NOT NULL REFERENCES cases(id), previous_stage VARCHAR(100),
 new_stage VARCHAR(100) NOT NULL, changed_by_order_id UUID REFERENCES court_orders(id),
 changed_by_user_id UUID NOT NULL REFERENCES users(id), remarks TEXT,
 changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMIT;
