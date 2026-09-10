-- ============================================================
-- 04_seed_data.sql
-- Dummy development/test data for the 20-table database
-- ============================================================

BEGIN;

-- ============================================================
-- 1. DEPARTMENTS
-- ============================================================

INSERT INTO departments (name, code)
VALUES
    ('Cyber Crime Investigation Unit', 'CCIU'),
    ('District Court', 'COURT'),
    ('Central Police Station', 'CPS')
ON CONFLICT (code) DO NOTHING;


-- ============================================================
-- 2. ROLES
-- ============================================================

INSERT INTO roles (name, permissions)
VALUES
(
    'INVESTIGATOR',
    '{
        "case": {
            "view": true,
            "edit": true,
            "share": true,
            "delete": true
        },
        "document": {
            "view": true,
            "upload": true,
            "edit": true,
            "share": true
        }
    }'::jsonb
),
(
    'JUDGE',
    '{
        "case": {
            "view": true,
            "edit": false,
            "share": false,
            "delete": false
        },
        "document": {
            "view": true,
            "upload": false,
            "edit": false,
            "share": false
        }
    }'::jsonb
),
(
    'OFFICER',
    '{
        "case": {
            "view": true,
            "edit": true,
            "share": false,
            "delete": false
        },
        "document": {
            "view": true,
            "upload": true,
            "edit": true,
            "share": false
        }
    }'::jsonb
)
ON CONFLICT (name) DO NOTHING;


-- ============================================================
-- 3. USERS
-- ============================================================

INSERT INTO users
    (full_name, email, badge_number, security_clearance_level)
VALUES
    ('Aarav Sharma', 'aarav.investigator@example.com', 'BADGE-1001', 4),
    ('Priya Mehta', 'priya.judge@example.com', 'BADGE-2001', 5),
    ('Rohan Verma', 'rohan.officer@example.com', 'BADGE-3001', 3)
ON CONFLICT (email) DO NOTHING;


-- ============================================================
-- 4. USER_DEPARTMENTS
-- ============================================================

INSERT INTO user_departments
    (user_id, department_id, role_id, is_primary)
SELECT
    u.id,
    d.id,
    r.id,
    TRUE
FROM users u
JOIN departments d
    ON (
        (u.email = 'aarav.investigator@example.com'
         AND d.code = 'CCIU')
        OR
        (u.email = 'priya.judge@example.com'
         AND d.code = 'COURT')
        OR
        (u.email = 'rohan.officer@example.com'
         AND d.code = 'CPS')
    )
JOIN roles r
    ON (
        (u.email = 'aarav.investigator@example.com'
         AND r.name = 'INVESTIGATOR')
        OR
        (u.email = 'priya.judge@example.com'
         AND r.name = 'JUDGE')
        OR
        (u.email = 'rohan.officer@example.com'
         AND r.name = 'OFFICER')
    )
ON CONFLICT (user_id, department_id, role_id) DO NOTHING;


-- ============================================================
-- 5. EVIDENCE PROVIDER
-- ============================================================

INSERT INTO evidence_providers
    (provider_type, full_name_or_org, contact_info,
     identification_number, clearance_verified)
VALUES
(
    'POLICE',
    'Central Police Station',
    '{"phone": "+91-9000000000"}'::jsonb,
    'CPS-001',
    TRUE
);


-- ============================================================
-- 6. CASE
-- ============================================================

INSERT INTO cases
    (case_number, title, description,
     classification_level, status,
     primary_department_id, lead_investigator_id)
SELECT
    'FIR-2026-0001',
    'Cyber Fraud Investigation',
    'Dummy development case for testing the document management workflow.',
    3,
    'ACTIVE',
    d.id,
    u.id
FROM departments d
JOIN users u
    ON u.email = 'aarav.investigator@example.com'
WHERE d.code = 'CCIU'
ON CONFLICT (case_number) DO NOTHING;


-- ============================================================
-- 7. EVIDENCE ITEM
-- ============================================================

INSERT INTO evidence_items
    (case_id, evidence_number, provider_id,
     title, evidence_type, storage_location,
     current_status, seized_at, seized_by_user_id)
SELECT
    c.id,
    'EVD-2026-0001',
    ep.id,
    'Laptop used in investigation',
    'DIGITAL_DEVICE',
    'Secure Evidence Locker A-01',
    'IN_CUSTODY',
    CURRENT_TIMESTAMP,
    u.id
FROM cases c
JOIN evidence_providers ep
    ON ep.identification_number = 'CPS-001'
JOIN users u
    ON u.email = 'rohan.officer@example.com'
WHERE c.case_number = 'FIR-2026-0001'
ON CONFLICT (evidence_number) DO NOTHING;


-- ============================================================
-- 8. EVIDENCE CUSTODY TRANSFER
-- ============================================================

INSERT INTO evidence_custody_transfers
    (evidence_item_id,
     released_by_user_id,
     received_by_user_id,
     purpose,
     physical_condition_notes)
SELECT
    e.id,
    u1.id,
    u2.id,
    'Transfer for forensic examination',
    'Device received in sealed condition.'
FROM evidence_items e
JOIN users u1
    ON u1.email = 'rohan.officer@example.com'
JOIN users u2
    ON u2.email = 'aarav.investigator@example.com'
WHERE e.evidence_number = 'EVD-2026-0001'
AND NOT EXISTS (
    SELECT 1
    FROM evidence_custody_transfers ect
    WHERE ect.evidence_item_id = e.id
);


-- ============================================================
-- 9. DOCUMENT 1
-- ============================================================

INSERT INTO documents
    (case_id, evidence_item_id,
     document_number, title, document_type,
     confidentiality_level, current_version,
     created_by)
SELECT
    c.id,
    e.id,
    'DOC-2026-0001',
    'Investigation Report',
    'INVESTIGATION_REPORT',
    4,
    1,
    u.id
FROM cases c
JOIN evidence_items e
    ON e.evidence_number = 'EVD-2026-0001'
JOIN users u
    ON u.email = 'aarav.investigator@example.com'
WHERE c.case_number = 'FIR-2026-0001'
ON CONFLICT (document_number) DO NOTHING;


-- ============================================================
-- 10. DOCUMENT 2
-- ============================================================

INSERT INTO documents
    (case_id,
     document_number, title, document_type,
     confidentiality_level, current_version,
     created_by)
SELECT
    c.id,
    'DOC-2026-0002',
    'Court Order Document',
    'COURT_ORDER',
    5,
    1,
    u.id
FROM cases c
JOIN users u
    ON u.email = 'priya.judge@example.com'
WHERE c.case_number = 'FIR-2026-0001'
ON CONFLICT (document_number) DO NOTHING;


-- ============================================================
-- 11. DOCUMENT VERSIONS
-- ============================================================

INSERT INTO document_versions
    (document_id, version_number, storage_uri,
     file_size_bytes, file_mime_type,
     sha256_checksum, kms_key_id, uploaded_by)
SELECT
    d.id,
    1,
    'minio://legal-documents/DOC-2026-0001/v1.pdf',
    245760,
    'application/pdf',
    'dummy-sha256-checksum-document-0001',
    'kms-key-demo-001',
    u.id
FROM documents d
JOIN users u
    ON u.email = 'aarav.investigator@example.com'
WHERE d.document_number = 'DOC-2026-0001'
ON CONFLICT (document_id, version_number) DO NOTHING;


INSERT INTO document_versions
    (document_id, version_number, storage_uri,
     file_size_bytes, file_mime_type,
     sha256_checksum, kms_key_id, uploaded_by)
SELECT
    d.id,
    1,
    'minio://legal-documents/DOC-2026-0002/v1.pdf',
    128000,
    'application/pdf',
    'dummy-sha256-checksum-document-0002',
    'kms-key-demo-002',
    u.id
FROM documents d
JOIN users u
    ON u.email = 'priya.judge@example.com'
WHERE d.document_number = 'DOC-2026-0002'
ON CONFLICT (document_id, version_number) DO NOTHING;


-- ============================================================
-- 12. AI METADATA
-- ============================================================

INSERT INTO document_ai_metadata
    (version_id, ocr_extracted_text,
     ai_summary, extracted_entities,
     vector_embedding_id, processed_at)
SELECT
    dv.id,
    'Dummy OCR extracted text for development testing.',
    'Dummy AI summary of the investigation document.',
    '{"case_number":"FIR-2026-0001","document_type":"INVESTIGATION_REPORT"}'::jsonb,
    'embedding-demo-001',
    CURRENT_TIMESTAMP
FROM document_versions dv
JOIN documents d
    ON d.id = dv.document_id
WHERE d.document_number = 'DOC-2026-0001'
AND NOT EXISTS (
    SELECT 1
    FROM document_ai_metadata dam
    WHERE dam.version_id = dv.id
);


-- ============================================================
-- 13. INTER-DEPARTMENT SHARE
-- ============================================================

INSERT INTO inter_department_shares
    (document_id,
     source_department_id,
     target_department_id,
     granted_by_user_id,
     access_level,
     reason,
     valid_from,
     expires_at,
     status)
SELECT
    doc.id,
    source.id,
    target.id,
    u.id,
    'view',
    'Required for court review.',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP + INTERVAL '30 days',
    'active'
FROM documents doc
JOIN departments source
    ON source.code = 'CCIU'
JOIN departments target
    ON target.code = 'COURT'
JOIN users u
    ON u.email = 'aarav.investigator@example.com'
WHERE doc.document_number = 'DOC-2026-0001'
AND NOT EXISTS (
    SELECT 1
    FROM inter_department_shares s
    WHERE s.document_id = doc.id
      AND s.target_department_id = target.id
);


-- ============================================================
-- 14. CHAIN OF CUSTODY LOG
-- ============================================================

INSERT INTO chain_of_custody_logs
    (case_id,
     document_id,
     evidence_id,
     actor_id,
     actor_department_id,
     action,
     ip_address,
     user_agent,
     previous_log_hash,
     current_log_hash)
SELECT
    c.id,
    d.id,
    e.id,
    u.id,
    dep.id,
    'DOCUMENT_UPLOADED',
    '127.0.0.1',
    'Prototype Browser',
    NULL,
    'demo-current-log-hash-001'
FROM cases c
JOIN documents d
    ON d.document_number = 'DOC-2026-0001'
JOIN evidence_items e
    ON e.evidence_number = 'EVD-2026-0001'
JOIN users u
    ON u.email = 'aarav.investigator@example.com'
JOIN departments dep
    ON dep.code = 'CCIU'
WHERE c.case_number = 'FIR-2026-0001';


-- ============================================================
-- 15. DIGITAL SIGNATURE
-- ============================================================

INSERT INTO digital_signatures
    (document_version_id,
     signer_id,
     signer_department_id,
     signature_hash,
     cert_serial_number,
     timestamp_seal)
SELECT
    dv.id,
    u.id,
    d.id,
    'demo-signature-hash-001',
    'CERT-DEMO-001',
    'DEMO-TIMESTAMP-SEAL'
FROM document_versions dv
JOIN documents doc
    ON doc.id = dv.document_id
JOIN users u
    ON u.email = 'priya.judge@example.com'
JOIN departments d
    ON d.code = 'COURT'
WHERE doc.document_number = 'DOC-2026-0002'
AND NOT EXISTS (
    SELECT 1
    FROM digital_signatures ds
    WHERE ds.document_version_id = dv.id
);


-- ============================================================
-- 16. COURT BENCH
-- ============================================================

INSERT INTO court_benches
    (department_id, bench_name, bench_type,
     presiding_judge_id, is_active)
SELECT
    d.id,
    'Cyber Crime Bench',
    'DISTRICT_COURT',
    u.id,
    TRUE
FROM departments d
JOIN users u
    ON u.email = 'priya.judge@example.com'
WHERE d.code = 'COURT'
AND NOT EXISTS (
    SELECT 1
    FROM court_benches cb
    WHERE cb.bench_name = 'Cyber Crime Bench'
);


-- ============================================================
-- 17. COURT HEARING
-- ============================================================

INSERT INTO court_hearings
    (case_id, bench_id, hearing_date,
     hearing_purpose, status,
     next_hearing_date)
SELECT
    c.id,
    cb.id,
    CURRENT_TIMESTAMP + INTERVAL '7 days',
    'Initial hearing',
    'SCHEDULED',
    CURRENT_TIMESTAMP + INTERVAL '30 days'
FROM cases c
JOIN court_benches cb
    ON cb.bench_name = 'Cyber Crime Bench'
WHERE c.case_number = 'FIR-2026-0001'
AND NOT EXISTS (
    SELECT 1
    FROM court_hearings ch
    WHERE ch.case_id = c.id
);


-- ============================================================
-- 18. ORDER SHEET
-- ============================================================

INSERT INTO order_sheets
    (case_id, hearing_id,
     order_sheet_number,
     proceeding_summary,
     advocates_present,
     accused_presence_status,
     document_id,
     recorded_by_user_id)
SELECT
    c.id,
    h.id,
    'OS-2026-0001',
    'Initial hearing proceedings recorded for development testing.',
    '{"prosecution":"Present","defence":"Present"}'::jsonb,
    'PRESENT',
    d.id,
    u.id
FROM cases c
JOIN court_hearings h
    ON h.case_id = c.id
JOIN documents d
    ON d.document_number = 'DOC-2026-0002'
JOIN users u
    ON u.email = 'priya.judge@example.com'
WHERE c.case_number = 'FIR-2026-0001'
AND NOT EXISTS (
    SELECT 1
    FROM order_sheets os
    WHERE os.order_sheet_number = 'OS-2026-0001'
);


-- ============================================================
-- 19. COURT ORDER
-- ============================================================

INSERT INTO court_orders
    (case_id, hearing_id,
     order_number,
     order_type,
     order_summary,
     issuing_judge_id,
     document_id,
     effective_date,
     enforcement_status)
SELECT
    c.id,
    h.id,
    'ORDER-2026-0001',
    'DIRECTION',
    'Dummy court order for prototype testing.',
    u.id,
    d.id,
    CURRENT_TIMESTAMP,
    'PENDING'
FROM cases c
JOIN court_hearings h
    ON h.case_id = c.id
JOIN users u
    ON u.email = 'priya.judge@example.com'
JOIN documents d
    ON d.document_number = 'DOC-2026-0002'
WHERE c.case_number = 'FIR-2026-0001'
AND NOT EXISTS (
    SELECT 1
    FROM court_orders co
    WHERE co.order_number = 'ORDER-2026-0001'
);


-- ============================================================
-- 20. WARRANT / SUMMONS
-- ============================================================

INSERT INTO warrants_and_summons
    (court_order_id,
     case_id,
     notice_type,
     target_person_details,
     assigned_police_station_id,
     executing_officer_id,
     execution_status,
     return_date)
SELECT
    co.id,
    c.id,
    'SUMMONS',
    '{"name":"Demo Respondent","address":"Demo Address"}'::jsonb,
    dep.id,
    u.id,
    'PENDING',
    CURRENT_TIMESTAMP + INTERVAL '15 days'
FROM court_orders co
JOIN cases c
    ON c.id = co.case_id
JOIN departments dep
    ON dep.code = 'CPS'
JOIN users u
    ON u.email = 'rohan.officer@example.com'
WHERE co.order_number = 'ORDER-2026-0001'
AND NOT EXISTS (
    SELECT 1
    FROM warrants_and_summons ws
    WHERE ws.court_order_id = co.id
);


-- ============================================================
-- 21. CASE STAGE HISTORY
-- ============================================================

INSERT INTO case_stage_history
    (case_id,
     previous_stage,
     new_stage,
     changed_by_order_id,
     changed_by_user_id,
     remarks)
SELECT
    c.id,
    'INVESTIGATION',
    'COURT_PROCEEDINGS',
    co.id,
    u.id,
    'Case moved to court proceedings for prototype testing.'
FROM cases c
JOIN court_orders co
    ON co.case_id = c.id
JOIN users u
    ON u.email = 'priya.judge@example.com'
WHERE c.case_number = 'FIR-2026-0001'
AND co.order_number = 'ORDER-2026-0001'
AND NOT EXISTS (
    SELECT 1
    FROM case_stage_history csh
    WHERE csh.case_id = c.id
      AND csh.new_stage = 'COURT_PROCEEDINGS'
);


COMMIT;