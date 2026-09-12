-- ============================================================
-- SIH 2026 - Idempotent Test Data Population Script
-- Secure Digital Document Management System
-- Safe to run multiple times - won't create duplicates
-- ============================================================

-- ============================================================
-- 1. DEPARTMENTS
-- ============================================================
INSERT INTO public.departments (id, name, code, parent_id, created_at) VALUES
('d1111111-1111-1111-1111-111111111111', 'Cyber Crime Division', 'CCD', NULL, NOW()),
('d2222222-2222-2222-2222-222222222222', 'Homicide Department', 'HMD', NULL, NOW()),
('d3333333-3333-3333-3333-333333333333', 'Financial Crimes Unit', 'FCU', NULL, NOW()),
('d4444444-4444-4444-4444-444444444444', 'Narcotics Bureau', 'NRC', NULL, NOW()),
('d5555555-5555-5555-5555-555555555555', 'Forensic Science Lab', 'FSL', 'd1111111-1111-1111-1111-111111111111', NOW()),
('d6666666-6666-6666-6666-666666666666', 'Digital Evidence Unit', 'DEU', 'd1111111-1111-1111-1111-111111111111', NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 2. USERS (Investigators, Officers, Judges)
-- ============================================================
INSERT INTO public.users (id, full_name, email, badge_number, security_clearance_level, is_active, created_at) VALUES
('u1111111-1111-1111-1111-111111111111', 'Rajesh Kumar Sharma', 'rajesh.sharma@police.gov.in', 'PB-2019-001', 5, true, NOW()),
('u2222222-2222-2222-2222-222222222222', 'Priya Singh', 'priya.singh@police.gov.in', 'PB-2020-045', 4, true, NOW()),
('u3333333-3333-3333-3333-333333333333', 'Amit Patel', 'amit.patel@police.gov.in', 'PB-2018-112', 5, true, NOW()),
('u4444444-4444-4444-4444-444444444444', 'Sneha Reddy', 'sneha.reddy@police.gov.in', 'PB-2021-078', 3, true, NOW()),
('u5555555-5555-5555-5555-555555555555', 'Vikram Malhotra', 'vikram.malhotra@police.gov.in', 'PB-2017-023', 5, true, NOW()),
('u6666666-6666-6666-6666-666666666666', 'Anjali Deshmukh', 'anjali.deshmukh@police.gov.in', 'PB-2022-134', 3, true, NOW()),
('u7777777-7777-7777-7777-777777777777', 'Justice R.K. Verma', 'rk.verma@judiciary.gov.in', 'JD-2015-008', 5, true, NOW()),
('u8888888-8888-8888-8888-888888888888', 'Justice M. Lakshmi', 'm.lakshmi@judiciary.gov.in', 'JD-2016-012', 5, true, NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 3. ROLES
-- ============================================================
INSERT INTO public.roles (id, name, permissions) VALUES
('r1111111-1111-1111-1111-111111111111', 'Super Admin', '["all"]'),
('r2222222-2222-2222-2222-222222222222', 'Investigator', '["case.read", "case.write", "document.upload", "document.read", "evidence.manage"]'),
('r3333333-3333-3333-3333-333333333333', 'Junior Officer', '["case.read", "document.read", "evidence.view"]'),
('r4444444-4444-4444-4444-444444444444', 'Forensic Analyst', '["case.read", "document.upload", "evidence.analyze", "forensic.report"]'),
('r5555555-5555-5555-5555-555555555555', 'Judge', '["case.read", "court.order.write", "warrant.issue", "all.departments.read"]'),
('r6666666-6666-6666-6666-666666666666', 'Clerk', '["case.read", "document.read", "court.hearing.schedule"]')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 4. USER_DEPARTMENTS (Assign users to departments with roles)
-- ============================================================
INSERT INTO public.user_departments (id, user_id, department_id, role_id, is_primary, assigned_at) VALUES
('ud1111111-1111-1111-1111-11111111111', 'u1111111-1111-1111-1111-111111111111', 'd1111111-1111-1111-1111-111111111111', 'r2222222-2222-2222-2222-222222222222', true, NOW()),
('ud2222222-2222-2222-2222-22222222222', 'u2222222-2222-2222-2222-222222222222', 'd2222222-2222-2222-2222-222222222222', 'r2222222-2222-2222-2222-222222222222', true, NOW()),
('ud3333333-3333-3333-3333-33333333333', 'u3333333-3333-3333-3333-333333333333', 'd3333333-3333-3333-3333-333333333333', 'r2222222-2222-2222-2222-222222222222', true, NOW()),
('ud4444444-4444-4444-4444-44444444444', 'u4444444-4444-4444-4444-444444444444', 'd5555555-5555-5555-5555-555555555555', 'r4444444-4444-4444-4444-444444444444', true, NOW()),
('ud5555555-5555-5555-5555-55555555555', 'u5555555-5555-5555-5555-555555555555', 'd4444444-4444-4444-4444-444444444444', 'r2222222-2222-2222-2222-222222222222', true, NOW()),
('ud6666666-6666-6666-6666-66666666666', 'u6666666-6666-6666-6666-666666666666', 'd6666666-6666-6666-6666-666666666666', 'r3333333-3333-3333-3333-333333333333', true, NOW()),
('ud7777777-7777-7777-7777-77777777777', 'u7777777-7777-7777-7777-777777777777', 'd1111111-1111-1111-1111-111111111111', 'r5555555-5555-5555-5555-555555555555', true, NOW()),
('ud8888888-8888-8888-8888-88888888888', 'u8888888-8888-8888-8888-888888888888', 'd2222222-2222-2222-2222-222222222222', 'r5555555-5555-5555-5555-555555555555', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 5. EVIDENCE PROVIDERS
-- ============================================================
INSERT INTO public.evidence_providers (id, provider_type, full_name_or_org, contact_info, identification_number, clearance_verified, created_at) VALUES
('ep1111111-1111-1111-1111-1111111111', 'individual', 'Ramesh Gupta', '{"phone": "+91-9876543210", "email": "ramesh.g@email.com", "address": "45, MG Road, Delhi"}', 'AADHAAR-1234-5678-9012', true, NOW()),
('ep2222222-2222-2222-2222-2222222222', 'organization', 'TechCorp India Pvt Ltd', '{"phone": "+91-11-23456789", "email": "legal@techcorp.in", "address": "Cyber City, Gurugram"}', 'CIN-U72200DL2015PTC123456', true, NOW()),
('ep3333333-3333-3333-3333-3333333333', 'individual', 'Sunita Devi', '{"phone": "+91-9123456789", "email": "sunita.d@email.com", "address": "Village Ramnagar, UP"}', 'AADHAAR-9876-5432-1098', true, NOW()),
('ep4444444-4444-4444-4444-4444444444', 'organization', 'City Bank Ltd', '{"phone": "+91-22-87654321", "email": "compliance@citybank.in", "address": "Nariman Point, Mumbai"}', 'CIN-U65100MH2010PLC234567', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 6. CASES
-- ============================================================
INSERT INTO public.cases (id, case_number, title, description, classification_level, status, primary_department_id, lead_investigator_id, created_at) VALUES
('c1111111-1111-1111-1111-111111111111', 'CCD-2026-001', 'Cyber Fraud - Online Banking Scam', 'Large-scale phishing operation targeting bank customers through fake emails and websites', 4, 'active', 'd1111111-1111-1111-1111-111111111111', 'u1111111-1111-1111-1111-111111111111', NOW()),
('c2222222-2222-2222-2222-222222222222', 'HMD-2026-045', 'Murder Investigation - Sector 15', 'Homicide case with multiple suspects and forensic evidence required', 5, 'active', 'd2222222-2222-2222-2222-222222222222', 'u2222222-2222-2222-2222-222222222222', NOW()),
('c3333333-3333-3333-3333-333333333333', 'FCU-2026-112', 'Money Laundering - Shell Companies', 'Investigation into suspicious financial transactions through shell companies', 5, 'active', 'd3333333-3333-3333-3333-333333333333', 'u3333333-3333-3333-3333-333333333333', NOW()),
('c4444444-4444-4444-4444-444444444444', 'NRC-2026-078', 'Drug Trafficking Network', 'Inter-state narcotics smuggling operation', 4, 'active', 'd4444444-4444-4444-4444-444444444444', 'u5555555-5555-5555-5555-555555555555', NOW()),
('c5555555-5555-5555-5555-555555555555', 'CCD-2025-234', 'Data Breach - Corporate Espionage', 'Unauthorized access to confidential corporate data', 3, 'closed', 'd1111111-1111-1111-1111-111111111111', 'u1111111-1111-1111-1111-111111111111', NOW() - INTERVAL '6 months')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 7. EVIDENCE ITEMS
-- ============================================================
INSERT INTO public.evidence_items (id, case_id, evidence_number, provider_id, title, evidence_type, storage_location, current_status, seized_at, seized_by_user_id) VALUES
('ev1111111-1111-1111-1111-1111111111', 'c1111111-1111-1111-1111-111111111111', 'EVD-CCD-001-01', 'ep1111111-1111-1111-1111-1111111111', 'Suspect Laptop - Dell Inspiron', 'digital', 'Digital Evidence Vault - Rack A3', 'in_custody', NOW() - INTERVAL '15 days', 'u1111111-1111-1111-1111-111111111111'),
('ev2222222-2222-2222-2222-2222222222', 'c1111111-1111-1111-1111-111111111111', 'EVD-CCD-001-02', 'ep2222222-2222-2222-2222-2222222222', 'Server Logs - TechCorp', 'digital', 'Digital Evidence Vault - Rack B1', 'in_custody', NOW() - INTERVAL '14 days', 'u1111111-1111-1111-1111-111111111111'),
('ev3333333-3333-3333-3333-3333333333', 'c2222222-2222-2222-2222-222222222222', 'EVD-HMD-045-01', 'ep3333333-3333-3333-3333-3333333333', 'Weapon - Kitchen Knife', 'physical', 'Forensic Storage - Locker 12', 'analyzed', NOW() - INTERVAL '7 days', 'u2222222-2222-2222-2222-222222222222'),
('ev4444444-4444-4444-4444-4444444444', 'c2222222-2222-2222-2222-222222222222', 'EVD-HMD-045-02', NULL, 'Blood Sample - Crime Scene', 'biological', 'Forensic Lab - Freezer Unit 3', 'analyzed', NOW() - INTERVAL '7 days', 'u4444444-4444-4444-4444-444444444444'),
('ev5555555-5555-5555-5555-5555555555', 'c3333333-3333-3333-3333-333333333333', 'EVD-FCU-112-01', 'ep4444444-4444-4444-4444-4444444444', 'Bank Transaction Records', 'document', 'Evidence Archive - Box 445', 'in_custody', NOW() - INTERVAL '30 days', 'u3333333-3333-3333-3333-333333333333'),
('ev6666666-6666-6666-6666-6666666666', 'c4444444-4444-4444-4444-444444444444', 'EVD-NRC-078-01', NULL, 'Seized Narcotics - 5kg', 'physical', 'Secure Storage - Vault 2', 'in_custody', NOW() - INTERVAL '3 days', 'u5555555-5555-5555-5555-555555555555')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 8. DOCUMENTS
-- ============================================================
INSERT INTO public.documents (id, case_id, evidence_item_id, document_number, title, document_type, confidentiality_level, current_version, created_by, created_at, is_locked) VALUES
('doc1111111-1111-1111-1111-111111111', 'c1111111-1111-1111-1111-111111111111', 'ev1111111-1111-1111-1111-1111111111', 'DOC-CCD-001-001', 'First Information Report', 'FIR', 3, 1, 'u1111111-1111-1111-1111-111111111111', NOW() - INTERVAL '15 days', false),
('doc2222222-2222-2222-2222-222222222', 'c1111111-1111-1111-1111-111111111111', 'ev2222222-2222-2222-2222-2222222222', 'DOC-CCD-001-002', 'Digital Forensic Analysis Report', 'Forensic Report', 4, 1, 'u4444444-4444-4444-4444-444444444444', NOW() - INTERVAL '10 days', false),
('doc3333333-3333-3333-3333-333333333', 'c1111111-1111-1111-1111-111111111111', NULL, 'DOC-CCD-001-003', 'Witness Statement - Ramesh Gupta', 'Witness Statement', 3, 1, 'u1111111-1111-1111-1111-111111111111', NOW() - INTERVAL '12 days', false),
('doc4444444-4444-4444-4444-444444444', 'c2222222-2222-2222-2222-222222222222', 'ev3333333-3333-3333-3333-3333333333', 'DOC-HMD-045-001', 'Post-Mortem Report', 'Forensic Report', 4, 1, 'u4444444-4444-4444-4444-444444444444', NOW() - INTERVAL '5 days', false),
('doc5555555-5555-5555-5555-555555555', 'c2222222-2222-2222-2222-222222222222', NULL, 'DOC-HMD-045-002', 'Charge Sheet', 'ChargeSheet', 5, 1, 'u2222222-2222-2222-2222-222222222222', NOW() - INTERVAL '2 days', true),
('doc6666666-6666-6666-6666-666666666', 'c3333333-3333-3333-3333-333333333333', 'ev5555555-5555-5555-5555-5555555555', 'DOC-FCU-112-001', 'Financial Audit Report', 'Evidence', 5, 1, 'u3333333-3333-3333-3333-333333333333', NOW() - INTERVAL '25 days', false),
('doc7777777-7777-7777-7777-777777777', 'c4444444-4444-4444-4444-444444444444', 'ev6666666-6666-6666-6666-6666666666', 'DOC-NRC-078-001', 'Chemical Analysis Certificate', 'Forensic Report', 4, 1, 'u4444444-4444-4444-4444-444444444444', NOW() - INTERVAL '2 days', false),
('doc8888888-8888-8888-8888-888888888', 'c5555555-5555-5555-5555-555555555555', NULL, 'DOC-CCD-234-015', 'Case Closure Summary', 'Legal Notice', 2, 1, 'u1111111-1111-1111-1111-111111111111', NOW() - INTERVAL '1 month', true)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 9. DOCUMENT VERSIONS
-- ============================================================
INSERT INTO public.document_versions (id, document_id, version_number, storage_uri, file_size_bytes, file_mime_type, sha256_checksum, kms_key_id, uploaded_by, uploaded_at) VALUES
('dv1111111-1111-1111-1111-111111111', 'doc1111111-1111-1111-1111-111111111', 1, 'case_c1111111-1111-1111-1111-111111111111/doc1111111-1111-1111-1111-111111111/fir_v1.pdf', 2458624, 'application/pdf', 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456', 'key-001', 'u1111111-1111-1111-1111-111111111111', NOW() - INTERVAL '15 days'),
('dv2222222-2222-2222-2222-222222222', 'doc2222222-2222-2222-2222-222222222', 1, 'case_c1111111-1111-1111-1111-111111111111/doc2222222-2222-2222-2222-222222222/forensic_report_v1.pdf', 8945123, 'application/pdf', 'b2c3d4e5f67890123456789012345678901abcdef1234567890abcdef1234567', 'key-001', 'u4444444-4444-4444-4444-444444444444', NOW() - INTERVAL '10 days'),
('dv3333333-3333-3333-3333-333333333', 'doc3333333-3333-3333-3333-333333333', 1, 'case_c1111111-1111-1111-1111-111111111111/doc3333333-3333-3333-3333-333333333/witness_stmt_v1.pdf', 1245678, 'application/pdf', 'c3d4e5f678901234567890123456789012abcdef1234567890abcdef12345678', 'key-001', 'u1111111-1111-1111-1111-111111111111', NOW() - INTERVAL '12 days'),
('dv4444444-4444-4444-4444-444444444', 'doc4444444-4444-4444-4444-444444444', 1, 'case_c2222222-2222-2222-2222-222222222222/doc4444444-4444-4444-4444-444444444/postmortem_v1.pdf', 3567890, 'application/pdf', 'd4e5f6789012345678901234567890123abcdef1234567890abcdef123456789', 'key-002', 'u4444444-4444-4444-4444-444444444444', NOW() - INTERVAL '5 days'),
('dv5555555-5555-5555-5555-555555555', 'doc5555555-5555-5555-5555-555555555', 1, 'case_c2222222-2222-2222-2222-222222222222/doc5555555-5555-5555-5555-555555555/chargesheet_v1.pdf', 12456789, 'application/pdf', 'e5f67890123456789012345678901234abcdef1234567890abcdef1234567890', 'key-002', 'u2222222-2222-2222-2222-222222222222', NOW() - INTERVAL '2 days'),
('dv6666666-6666-6666-6666-666666666', 'doc6666666-6666-6666-6666-666666666', 1, 'case_c3333333-3333-3333-3333-333333333333/doc6666666-6666-6666-6666-666666666/audit_report_v1.xlsx', 5678901, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'f678901234567890123456789012345abcdef1234567890abcdef12345678901', 'key-003', 'u3333333-3333-3333-3333-333333333333', NOW() - INTERVAL '25 days'),
('dv7777777-7777-7777-7777-777777777', 'doc7777777-7777-7777-7777-777777777', 1, 'case_c4444444-4444-4444-4444-444444444444/doc7777777-7777-7777-7777-777777777/chemical_analysis_v1.pdf', 2345678, 'application/pdf', '6789012345678901234567890123456abcdef1234567890abcdef123456789012', 'key-004', 'u4444444-4444-4444-4444-444444444444', NOW() - INTERVAL '2 days'),
('dv8888888-8888-8888-8888-888888888', 'doc8888888-8888-8888-8888-888888888', 1, 'case_c5555555-5555-5555-5555-555555555555/doc8888888-8888-8888-8888-888888888/closure_summary_v1.pdf', 987654, 'application/pdf', '7890123456789012345678901234567abcdef1234567890abcdef1234567890123', 'key-001', 'u1111111-1111-1111-1111-111111111111', NOW() - INTERVAL '1 month')
ON CONFLICT ON CONSTRAINT document_versions_document_id_version_number_key DO NOTHING;

-- ============================================================
-- 10. CHAIN OF CUSTODY LOGS (Hash-chained audit trail)
-- ============================================================
INSERT INTO public.chain_of_custody_logs (id, case_id, document_id, evidence_id, actor_id, actor_department_id, action, ip_address, user_agent, previous_log_hash, current_log_hash, created_at) VALUES
('col1111111-1111-1111-1111-111111111', 'c1111111-1111-1111-1111-111111111111', NULL, NULL, 'u1111111-1111-1111-1111-111111111111', 'd1111111-1111-1111-1111-111111111111', 'CASE_CREATED', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', NULL, 'hash_col_001_a1b2c3d4e5f6789012345678901234567890abcdef', NOW() - INTERVAL '15 days'),
('col2222222-2222-2222-2222-222222222', 'c1111111-1111-1111-1111-111111111111', 'doc1111111-1111-1111-1111-111111111', NULL, 'u1111111-1111-1111-1111-111111111111', 'd1111111-1111-1111-1111-111111111111', 'DOCUMENT_UPLOADED', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'hash_col_001_a1b2c3d4e5f6789012345678901234567890abcdef', 'hash_col_002_b2c3d4e5f67890123456789012345678901abcdef', NOW() - INTERVAL '15 days'),
('col3333333-3333-3333-3333-333333333', 'c1111111-1111-1111-1111-111111111111', 'doc2222222-2222-2222-2222-222222222', NULL, 'u4444444-4444-4444-4444-444444444444', 'd5555555-5555-5555-5555-555555555555', 'DOCUMENT_UPLOADED', '192.168.1.105', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'hash_col_002_b2c3d4e5f67890123456789012345678901abcdef', 'hash_col_003_c3d4e5f678901234567890123456789012abcdef', NOW() - INTERVAL '10 days'),
('col4444444-4444-4444-4444-444444444', 'c1111111-1111-1111-1111-111111111111', 'doc1111111-1111-1111-1111-111111111', NULL, 'u1111111-1111-1111-1111-111111111111', 'd1111111-1111-1111-1111-111111111111', 'DOCUMENT_VIEWED', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'hash_col_003_c3d4e5f678901234567890123456789012abcdef', 'hash_col_004_d4e5f6789012345678901234567890123abcdef', NOW() - INTERVAL '9 days'),
('col5555555-5555-5555-5555-555555555', 'c2222222-2222-2222-2222-222222222222', 'doc4444444-4444-4444-4444-444444444', NULL, 'u4444444-4444-4444-4444-444444444444', 'd5555555-5555-5555-5555-555555555555', 'DOCUMENT_UPLOADED', '192.168.1.105', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'hash_col_004_d4e5f6789012345678901234567890123abcdef', 'hash_col_005_e5f67890123456789012345678901234abcdef', NOW() - INTERVAL '5 days'),
('col6666666-6666-6666-6666-666666666', 'c2222222-2222-2222-2222-222222222222', 'doc5555555-5555-5555-5555-555555555', NULL, 'u2222222-2222-2222-2222-222222222222', 'd2222222-2222-2222-2222-222222222222', 'DOCUMENT_LOCKED', '192.168.1.102', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'hash_col_005_e5f67890123456789012345678901234abcdef', 'hash_col_006_f678901234567890123456789012345abcdef', NOW() - INTERVAL '2 days')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 11. REVOKED TOKENS (For JWT security)
-- ============================================================
INSERT INTO public.revoked_tokens (token_jti, revoked_at, expires_at) VALUES
('jti-revoked-001-a1b2c3d4e5f6', NOW() - INTERVAL '2 days', NOW() + INTERVAL '28 days'),
('jti-revoked-002-b2c3d4e5f678', NOW() - INTERVAL '1 day', NOW() + INTERVAL '29 days'),
('jti-revoked-003-c3d4e5f67890', NOW() - INTERVAL '12 hours', NOW() + INTERVAL '29 days 12 hours')
ON CONFLICT (token_jti) DO NOTHING;

-- ============================================================
-- VERIFICATION QUERIES (Optional - for testing)
-- ============================================================
-- SELECT COUNT(*) FROM public.departments; -- Should return 6
-- SELECT COUNT(*) FROM public.users; -- Should return 8
-- SELECT COUNT(*) FROM public.roles; -- Should return 6
-- SELECT COUNT(*) FROM public.cases; -- Should return 5
-- SELECT COUNT(*) FROM public.documents; -- Should return 8
-- SELECT COUNT(*) FROM public.document_versions; -- Should return 8
-- SELECT COUNT(*) FROM public.chain_of_custody_logs; -- Should return 6

-- ============================================================
-- END OF IDEMPOTENT TEST DATA POPULATION
-- ============================================================