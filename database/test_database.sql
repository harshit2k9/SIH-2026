-- ============================================================
-- SIH 2026 - Idempotent Test Data Population Script
-- ALL UUIDs are now strictly valid hexadecimal (0-9, a-f)
-- ============================================================

-- 1. DEPARTMENTS
INSERT INTO public.departments (id, name, code, parent_id, created_at) VALUES
('10000000-0000-0000-0000-000000000001', 'Cyber Crime Division', 'CCD', NULL, NOW()),
('10000000-0000-0000-0000-000000000002', 'Homicide Department', 'HMD', NULL, NOW()),
('10000000-0000-0000-0000-000000000003', 'Financial Crimes Unit', 'FCU', NULL, NOW()),
('10000000-0000-0000-0000-000000000004', 'Narcotics Bureau', 'NRC', NULL, NOW()),
('10000000-0000-0000-0000-000000000005', 'Forensic Science Lab', 'FSL', '10000000-0000-0000-0000-000000000001', NOW()),
('10000000-0000-0000-0000-000000000006', 'Digital Evidence Unit', 'DEU', '10000000-0000-0000-0000-000000000001', NOW())
ON CONFLICT (id) DO NOTHING;

-- 2. USERS
INSERT INTO public.users (id, full_name, email, badge_number, security_clearance_level, is_active, created_at) VALUES
('20000000-0000-0000-0000-000000000001', 'Rajesh Kumar Sharma', 'rajesh.sharma@police.gov.in', 'PB-2019-001', 5, true, NOW()),
('20000000-0000-0000-0000-000000000002', 'Priya Singh', 'priya.singh@police.gov.in', 'PB-2020-045', 4, true, NOW()),
('20000000-0000-0000-0000-000000000003', 'Amit Patel', 'amit.patel@police.gov.in', 'PB-2018-112', 5, true, NOW()),
('20000000-0000-0000-0000-000000000004', 'Sneha Reddy', 'sneha.reddy@police.gov.in', 'PB-2021-078', 3, true, NOW()),
('20000000-0000-0000-0000-000000000005', 'Vikram Malhotra', 'vikram.malhotra@police.gov.in', 'PB-2017-023', 5, true, NOW()),
('20000000-0000-0000-0000-000000000006', 'Anjali Deshmukh', 'anjali.deshmukh@police.gov.in', 'PB-2022-134', 3, true, NOW()),
('20000000-0000-0000-0000-000000000007', 'Justice R.K. Verma', 'rk.verma@judiciary.gov.in', 'JD-2015-008', 5, true, NOW()),
('20000000-0000-0000-0000-000000000008', 'Justice M. Lakshmi', 'm.lakshmi@judiciary.gov.in', 'JD-2016-012', 5, true, NOW())
ON CONFLICT (id) DO NOTHING;

-- 3. ROLES
INSERT INTO public.roles (id, name, permissions) VALUES
('30000000-0000-0000-0000-000000000001', 'Super Admin', '["all"]'),
('30000000-0000-0000-0000-000000000002', 'Investigator', '["case.read", "case.write", "document.upload", "document.read", "evidence.manage"]'),
('30000000-0000-0000-0000-000000000003', 'Junior Officer', '["case.read", "document.read", "evidence.view"]'),
('30000000-0000-0000-0000-000000000004', 'Forensic Analyst', '["case.read", "document.upload", "evidence.analyze", "forensic.report"]'),
('30000000-0000-0000-0000-000000000005', 'Judge', '["case.read", "court.order.write", "warrant.issue", "all.departments.read"]'),
('30000000-0000-0000-0000-000000000006', 'Clerk', '["case.read", "document.read", "court.hearing.schedule"]')
ON CONFLICT (id) DO NOTHING;

-- 4. USER_DEPARTMENTS
INSERT INTO public.user_departments (id, user_id, department_id, role_id, is_primary, assigned_at) VALUES
('40000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000002', true, NOW()),
('40000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000002', true, NOW()),
('40000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000002', true, NOW()),
('40000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000004', true, NOW()),
('40000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000002', true, NOW()),
('40000000-0000-0000-0000-000000000006', '20000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000006', '30000000-0000-0000-0000-000000000003', true, NOW()),
('40000000-0000-0000-0000-000000000007', '20000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000005', true, NOW()),
('40000000-0000-0000-0000-000000000008', '20000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000005', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- 5. EVIDENCE PROVIDERS
INSERT INTO public.evidence_providers (id, provider_type, full_name_or_org, contact_info, identification_number, clearance_verified, created_at) VALUES
('50000000-0000-0000-0000-000000000001', 'individual', 'Ramesh Gupta', '{"phone": "+91-9876543210", "email": "ramesh.g@email.com", "address": "45, MG Road, Delhi"}', 'AADHAAR-1234-5678-9012', true, NOW()),
('50000000-0000-0000-0000-000000000002', 'organization', 'TechCorp India Pvt Ltd', '{"phone": "+91-11-23456789", "email": "legal@techcorp.in", "address": "Cyber City, Gurugram"}', 'CIN-U72200DL2015PTC123456', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- 6. CASES
INSERT INTO public.cases (id, case_number, title, description, classification_level, status, primary_department_id, lead_investigator_id, created_at) VALUES
('60000000-0000-0000-0000-000000000001', 'CCD-2026-001', 'Cyber Fraud - Online Banking Scam', 'Large-scale phishing operation', 4, 'active', '10000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', NOW()),
('60000000-0000-0000-0000-000000000002', 'HMD-2026-045', 'Murder Investigation - Sector 15', 'Homicide case with multiple suspects', 5, 'active', '10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000002', NOW())
ON CONFLICT (id) DO NOTHING;

-- 7. EVIDENCE ITEMS
INSERT INTO public.evidence_items (id, case_id, evidence_number, provider_id, title, evidence_type, storage_location, current_status, seized_at, seized_by_user_id) VALUES
('70000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', 'EVD-CCD-001-01', '50000000-0000-0000-0000-000000000001', 'Suspect Laptop - Dell Inspiron', 'digital', 'Digital Evidence Vault - Rack A3', 'in_custody', NOW() - INTERVAL '15 days', '20000000-0000-0000-0000-000000000001'),
('70000000-0000-0000-0000-000000000002', '60000000-0000-0000-0000-000000000002', 'EVD-HMD-045-01', '50000000-0000-0000-0000-000000000001', 'Weapon - Kitchen Knife', 'physical', 'Forensic Storage - Locker 12', 'analyzed', NOW() - INTERVAL '7 days', '20000000-0000-0000-0000-000000000002')
ON CONFLICT (id) DO NOTHING;

-- 8. DOCUMENTS
INSERT INTO public.documents (id, case_id, evidence_item_id, document_number, title, document_type, confidentiality_level, current_version, created_by, created_at, is_locked) VALUES
('80000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', '70000000-0000-0000-0000-000000000001', 'DOC-CCD-001-001', 'First Information Report', 'FIR', 3, 1, '20000000-0000-0000-0000-000000000001', NOW() - INTERVAL '15 days', false),
('80000000-0000-0000-0000-000000000002', '60000000-0000-0000-0000-000000000002', '70000000-0000-0000-0000-000000000002', 'DOC-HMD-045-001', 'Post-Mortem Report', 'Forensic Report', 4, 1, '20000000-0000-0000-0000-000000000004', NOW() - INTERVAL '5 days', false)
ON CONFLICT (id) DO NOTHING;

-- 9. DOCUMENT VERSIONS
INSERT INTO public.document_versions (id, document_id, version_number, storage_uri, file_size_bytes, file_mime_type, sha256_checksum, kms_key_id, uploaded_by, uploaded_at) VALUES
('90000000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000001', 1, 'case_60000000-0000-0000-0000-000000000001/80000000-0000-0000-0000-000000000001_v1.pdf', 2458624, 'application/pdf', 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456', 'key-001', '20000000-0000-0000-0000-000000000001', NOW() - INTERVAL '15 days'),
('90000000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000002', 1, 'case_60000000-0000-0000-0000-000000000002/80000000-0000-0000-0000-000000000002_v1.pdf', 3567890, 'application/pdf', 'd4e5f6789012345678901234567890123abcdef1234567890abcdef123456789', 'key-002', '20000000-0000-0000-0000-000000000004', NOW() - INTERVAL '5 days')
ON CONFLICT ON CONSTRAINT document_versions_document_id_version_number_key DO NOTHING;

-- 10. CHAIN OF CUSTODY LOGS
INSERT INTO public.chain_of_custody_logs (id, case_id, document_id, evidence_id, actor_id, actor_department_id, action, ip_address, user_agent, previous_log_hash, current_log_hash, created_at) VALUES
('a0000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000001', '70000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'DOCUMENT_UPLOADED', '192.168.1.100', 'Mozilla/5.0', NULL, 'hash_col_001_a1b2c3d4e5f6789012345678901234567890abcdef', NOW() - INTERVAL '15 days'),
('a0000000-0000-0000-0000-000000000002', '60000000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000002', '70000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000005', 'DOCUMENT_UPLOADED', '192.168.1.105', 'Mozilla/5.0', 'hash_col_001_a1b2c3d4e5f6789012345678901234567890abcdef', 'hash_col_002_b2c3d4e5f67890123456789012345678901abcdef', NOW() - INTERVAL '5 days')
ON CONFLICT (id) DO NOTHING;

-- 11. REVOKED TOKENS
INSERT INTO public.revoked_tokens (token_jti, revoked_at, expires_at) VALUES
('jti-revoked-001-a1b2c3d4e5f6', NOW() - INTERVAL '2 days', NOW() + INTERVAL '28 days')
ON CONFLICT (token_jti) DO NOTHING;