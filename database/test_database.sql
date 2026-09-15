-- ============================================================
-- SIH 2026 - Comprehensive Test Data Population Script
-- Covers ALL tables in SIH_DATABASE.sql
-- ALL UUIDs are strictly valid hexadecimal (0-9, a-f)
-- Idempotent: Safe to run multiple times (ON CONFLICT DO NOTHING)
-- ============================================================

-- ============================================================
-- 1. DEPARTMENTS (6 departments with hierarchy)
-- ============================================================
INSERT INTO public.departments (id, name, code, parent_id, created_at) VALUES
('10000000-0000-0000-0000-000000000001', 'Cyber Crime Division', 'CCD', NULL, NOW()),
('10000000-0000-0000-0000-000000000002', 'Homicide Department', 'HMD', NULL, NOW()),
('10000000-0000-0000-0000-000000000003', 'Financial Crimes Unit', 'FCU', NULL, NOW()),
('10000000-0000-0000-0000-000000000004', 'Narcotics Bureau', 'NRC', NULL, NOW()),
('10000000-0000-0000-0000-000000000005', 'Forensic Science Lab', 'FSL', '10000000-0000-0000-0000-000000000001', NOW()),
('10000000-0000-0000-0000-000000000006', 'Digital Evidence Unit', 'DEU', '10000000-0000-0000-0000-000000000001', NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 2. ROLES (7 roles - including 'admin' for our code)
-- ============================================================
INSERT INTO public.roles (id, name, permissions) VALUES
('30000000-0000-0000-0000-000000000001', 'admin', '["all", "admin"]'),
('30000000-0000-0000-0000-000000000002', 'investigator', '["case.read", "case.write", "document.upload", "document.read", "evidence.manage"]'),
('30000000-0000-0000-0000-000000000003', 'junior_officer', '["case.read", "document.read", "evidence.view"]'),
('30000000-0000-0000-0000-000000000004', 'forensic_analyst', '["case.read", "document.upload", "evidence.analyze", "forensic.report"]'),
('30000000-0000-0000-0000-000000000005', 'judge', '["case.read", "court.order.write", "warrant.issue", "all.departments.read"]'),
('30000000-0000-0000-0000-000000000006', 'clerk', '["case.read", "document.read", "court.hearing.schedule"]'),
('30000000-0000-0000-0000-000000000007', 'super_admin', '["all", "admin", "system.config"]')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 3. USERS (10 operational users)
-- ============================================================
INSERT INTO public.users (id, full_name, email, badge_number, security_clearance_level, is_active, created_at) VALUES
('20000000-0000-0000-0000-000000000001', 'Rajesh Kumar Sharma', 'rajesh.sharma@police.gov.in', 'PB-2019-001', 5, true, NOW()),
('20000000-0000-0000-0000-000000000002', 'Priya Singh', 'priya.singh@police.gov.in', 'PB-2020-045', 4, true, NOW()),
('20000000-0000-0000-0000-000000000003', 'Amit Patel', 'amit.patel@police.gov.in', 'PB-2018-112', 5, true, NOW()),
('20000000-0000-0000-0000-000000000004', 'Sneha Reddy', 'sneha.reddy@police.gov.in', 'PB-2021-078', 3, true, NOW()),
('20000000-0000-0000-0000-000000000005', 'Vikram Malhotra', 'vikram.malhotra@police.gov.in', 'PB-2017-023', 5, true, NOW()),
('20000000-0000-0000-0000-000000000006', 'Anjali Deshmukh', 'anjali.deshmukh@police.gov.in', 'PB-2022-134', 3, true, NOW()),
('20000000-0000-0000-0000-000000000007', 'Justice R.K. Verma', 'rk.verma@judiciary.gov.in', 'JD-2015-008', 5, true, NOW()),
('20000000-0000-0000-0000-000000000008', 'Justice M. Lakshmi', 'm.lakshmi@judiciary.gov.in', 'JD-2016-012', 5, true, NOW()),
('20000000-0000-0000-0000-000000000009', 'System Administrator', 'admin@sddms.gov.in', 'ADMIN-001', 5, true, NOW()),
('20000000-0000-0000-0000-000000000010', 'Court Clerk Suresh', 'suresh.clerk@court.gov.in', 'CLK-2023-001', 2, true, NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 4. USER_DEPARTMENTS (10 assignments)
-- ============================================================
INSERT INTO public.user_departments (id, user_id, department_id, role_id, is_primary, assigned_at) VALUES
-- Rajesh - Cyber Crime Investigator
('40000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000002', true, NOW()),
-- Priya - Homicide Investigator
('40000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000002', true, NOW()),
-- Amit - Financial Crimes Investigator
('40000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000002', true, NOW()),
-- Sneha - Forensic Analyst
('40000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000004', true, NOW()),
-- Vikram - Narcotics Investigator
('40000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000002', true, NOW()),
-- Anjali - Junior Officer
('40000000-0000-0000-0000-000000000006', '20000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000006', '30000000-0000-0000-0000-000000000003', true, NOW()),
-- Justice Verma - Judge (Cyber Crime)
('40000000-0000-0000-0000-000000000007', '20000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000005', true, NOW()),
-- Justice Lakshmi - Judge (Homicide)
('40000000-0000-0000-0000-000000000008', '20000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000005', true, NOW()),
-- Admin - System Administrator
('40000000-0000-0000-0000-000000000009', '20000000-0000-0000-0000-000000000009', '10000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', true, NOW()),
-- Suresh - Court Clerk
('40000000-0000-0000-0000-000000000010', '20000000-0000-0000-0000-000000000010', '10000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000006', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 5. EVIDENCE PROVIDERS
-- ============================================================
INSERT INTO public.evidence_providers (id, provider_type, full_name_or_org, contact_info, identification_number, clearance_verified, created_at) VALUES
('50000000-0000-0000-0000-000000000001', 'individual', 'Ramesh Gupta', '{"phone": "+91-9876543210", "email": "ramesh.g@email.com", "address": "45, MG Road, Delhi"}', 'AADHAAR-1234-5678-9012', true, NOW()),
('50000000-0000-0000-0000-000000000002', 'organization', 'TechCorp India Pvt Ltd', '{"phone": "+91-11-23456789", "email": "legal@techcorp.in", "address": "Cyber City, Gurugram"}', 'CIN-U72200DL2015PTC123456', true, NOW()),
('50000000-0000-0000-0000-000000000003', 'individual', 'Sunita Devi', '{"phone": "+91-9988776655", "email": "sunita.d@email.com", "address": "Sector 15, Noida"}', 'AADHAAR-9876-5432-1098', true, NOW()),
('50000000-0000-0000-0000-000000000004', 'organization', 'State Bank of India', '{"phone": "+91-11-23450000", "email": "fraud@sbi.co.in", "address": "SBI HQ, Mumbai"}', 'BANK-SBI-001', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 6. CASES (4 cases across departments)
-- ============================================================
INSERT INTO public.cases (id, case_number, title, description, classification_level, status, primary_department_id, lead_investigator_id, created_at) VALUES
('60000000-0000-0000-0000-000000000001', 'CCD-2026-001', 'Cyber Fraud - Online Banking Scam', 'Large-scale phishing operation targeting SBI customers. Multiple victims reported unauthorized transactions totaling Rs. 2.5 crores.', 4, 'active', '10000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', NOW() - INTERVAL '15 days'),
('60000000-0000-0000-0000-000000000002', 'HMD-2026-045', 'Murder Investigation - Sector 15', 'Homicide case with multiple suspects. Victim found in residential apartment. Weapon recovered.', 5, 'active', '10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000002', NOW() - INTERVAL '7 days'),
('60000000-0000-0000-0000-000000000003', 'FCU-2026-012', 'Money Laundering - Shell Companies', 'Investigation into suspected money laundering through network of shell companies. Multiple bank accounts under scrutiny.', 5, 'active', '10000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000003', NOW() - INTERVAL '30 days'),
('60000000-0000-0000-0000-000000000004', 'NRC-2026-008', 'Drug Trafficking - Interstate Racket', 'Interstate drug trafficking network busted. Consignments seized from multiple locations.', 4, 'active', '10000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000005', NOW() - INTERVAL '10 days')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 7. EVIDENCE ITEMS
-- ============================================================
INSERT INTO public.evidence_items (id, case_id, evidence_number, provider_id, title, evidence_type, storage_location, current_status, seized_at, seized_by_user_id) VALUES
('70000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', 'EVD-CCD-001-01', '50000000-0000-0000-0000-000000000001', 'Suspect Laptop - Dell Inspiron', 'digital', 'Digital Evidence Vault - Rack A3', 'in_custody', NOW() - INTERVAL '15 days', '20000000-0000-0000-0000-000000000001'),
('70000000-0000-0000-0000-000000000002', '60000000-0000-0000-0000-000000000002', 'EVD-HMD-045-01', '50000000-0000-0000-0000-000000000003', 'Weapon - Kitchen Knife', 'physical', 'Forensic Storage - Locker 12', 'analyzed', NOW() - INTERVAL '7 days', '20000000-0000-0000-0000-000000000002'),
('70000000-0000-0000-0000-000000000003', '60000000-0000-0000-0000-000000000001', 'EVD-CCD-001-02', '50000000-0000-0000-0000-000000000004', 'Bank Transaction Records', 'digital', 'Digital Evidence Vault - Rack A4', 'in_custody', NOW() - INTERVAL '14 days', '20000000-0000-0000-0000-000000000001'),
('70000000-0000-0000-0000-000000000004', '60000000-0000-0000-0000-000000000003', 'EVD-FCU-012-01', '50000000-0000-0000-0000-000000000002', 'Company Registration Documents', 'physical', 'Evidence Room B - Shelf 7', 'in_custody', NOW() - INTERVAL '28 days', '20000000-0000-0000-0000-000000000003'),
('70000000-0000-0000-0000-000000000005', '60000000-0000-0000-0000-000000000004', 'EVD-NRC-008-01', '50000000-0000-0000-0000-000000000003', 'Seized Narcotics - 5kg', 'physical', 'Narcotics Vault - Secure Container 3', 'analyzed', NOW() - INTERVAL '10 days', '20000000-0000-0000-0000-000000000005')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 8. EVIDENCE CUSTODY TRANSFERS
-- ============================================================
INSERT INTO public.evidence_custody_transfers (id, evidence_item_id, released_by_user_id, received_by_user_id, purpose, transfer_timestamp, physical_condition_notes) VALUES
('71000000-0000-0000-0000-000000000001', '70000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000004', 'Forensic analysis of hard drive', NOW() - INTERVAL '12 days', 'Sealed evidence bag intact. No visible damage.'),
('71000000-0000-0000-0000-000000000002', '70000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000004', 'Fingerprint and DNA analysis', NOW() - INTERVAL '5 days', 'Evidence bag sealed. Knife in protective casing.')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 9. DOCUMENTS
-- ============================================================
INSERT INTO public.documents (id, case_id, evidence_item_id, document_number, title, document_type, confidentiality_level, current_version, created_by, created_at, is_locked) VALUES
('80000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', '70000000-0000-0000-0000-000000000001', 'DOC-CCD-001-001', 'First Information Report - Cyber Fraud', 'FIR', 3, 1, '20000000-0000-0000-0000-000000000001', NOW() - INTERVAL '15 days', false),
('80000000-0000-0000-0000-000000000002', '60000000-0000-0000-0000-000000000002', '70000000-0000-0000-0000-000000000002', 'DOC-HMD-045-001', 'Post-Mortem Report', 'Forensic Report', 4, 1, '20000000-0000-0000-0000-000000000004', NOW() - INTERVAL '5 days', false),
('80000000-0000-0000-0000-000000000003', '60000000-0000-0000-0000-000000000001', NULL, 'DOC-CCD-001-002', 'Witness Statement - Ramesh Gupta', 'Witness Statement', 3, 1, '20000000-0000-0000-0000-000000000001', NOW() - INTERVAL '13 days', false),
('80000000-0000-0000-0000-000000000004', '60000000-0000-0000-0000-000000000003', '70000000-0000-0000-0000-000000000004', 'DOC-FCU-012-001', 'Charge Sheet - Money Laundering', 'ChargeSheet', 5, 1, '20000000-0000-0000-0000-000000000003', NOW() - INTERVAL '20 days', false),
('80000000-0000-0000-0000-000000000005', '60000000-0000-0000-0000-000000000002', NULL, 'DOC-HMD-045-002', 'Legal Notice to Accused', 'Legal Notice', 3, 1, '20000000-0000-0000-0000-000000000002', NOW() - INTERVAL '3 days', false),
('80000000-0000-0000-0000-000000000006', '60000000-0000-0000-0000-000000000004', '70000000-0000-0000-0000-000000000005', 'DOC-NRC-008-001', 'Forensic Analysis - Drug Composition', 'Forensic Report', 4, 1, '20000000-0000-0000-0000-000000000004', NOW() - INTERVAL '8 days', false)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 10. DOCUMENT VERSIONS
-- ============================================================
INSERT INTO public.document_versions (id, document_id, version_number, storage_uri, file_size_bytes, file_mime_type, sha256_checksum, kms_key_id, uploaded_by, uploaded_at) VALUES
('90000000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000001', 1, 'case_60000000-0000-0000-0000-000000000001/80000000-0000-0000-0000-000000000001_v1.pdf', 2458624, 'application/pdf', 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456', 'key-001', '20000000-0000-0000-0000-000000000001', NOW() - INTERVAL '15 days'),
('90000000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000002', 1, 'case_60000000-0000-0000-0000-000000000002/80000000-0000-0000-0000-000000000002_v1.pdf', 3567890, 'application/pdf', 'd4e5f6789012345678901234567890123abcdef1234567890abcdef123456789', 'key-002', '20000000-0000-0000-0000-000000000004', NOW() - INTERVAL '5 days'),
('90000000-0000-0000-0000-000000000003', '80000000-0000-0000-0000-000000000003', 1, 'case_60000000-0000-0000-0000-000000000001/80000000-0000-0000-0000-000000000003_v1.pdf', 1024000, 'application/pdf', 'b2c3d4e5f67890123456789012345678901234abcdef1234567890abcdef12', 'key-001', '20000000-0000-0000-0000-000000000001', NOW() - INTERVAL '13 days'),
('90000000-0000-0000-0000-000000000004', '80000000-0000-0000-0000-000000000004', 1, 'case_60000000-0000-0000-0000-000000000003/80000000-0000-0000-0000-000000000004_v1.pdf', 5242880, 'application/pdf', 'c3d4e5f6789012345678901234567890123456abcdef1234567890abcdef12', 'key-003', '20000000-0000-0000-0000-000000000003', NOW() - INTERVAL '20 days'),
('90000000-0000-0000-0000-000000000005', '80000000-0000-0000-0000-000000000005', 1, 'case_60000000-0000-0000-0000-000000000002/80000000-0000-0000-0000-000000000005_v1.pdf', 512000, 'application/pdf', 'e5f67890123456789012345678901234567890abcdef1234567890abcdef1234', 'key-002', '20000000-0000-0000-0000-000000000002', NOW() - INTERVAL '3 days'),
('90000000-0000-0000-0000-000000000006', '80000000-0000-0000-0000-000000000006', 1, 'case_60000000-0000-0000-0000-000000000004/80000000-0000-0000-0000-000000000006_v1.pdf', 4194304, 'application/pdf', 'f6789012345678901234567890123456789012abcdef1234567890abcdef1234', 'key-004', '20000000-0000-0000-0000-000000000004', NOW() - INTERVAL '8 days')
ON CONFLICT ON CONSTRAINT document_versions_document_id_version_number_key DO NOTHING;

-- ============================================================
-- 11. CHAIN OF CUSTODY LOGS (Hash-chained audit trail)
-- ============================================================
INSERT INTO public.chain_of_custody_logs (id, case_id, document_id, evidence_id, actor_id, actor_department_id, action, ip_address, user_agent, previous_log_hash, current_log_hash, created_at) VALUES
('a0000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000001', '70000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'DOCUMENT_UPLOADED', '192.168.1.100', 'Mozilla/5.0', NULL, 'hash_gen_001_a1b2c3d4e5f6789012345678901234567890abcdef', NOW() - INTERVAL '15 days'),
('a0000000-0000-0000-0000-000000000002', '60000000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000003', NULL, '20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'DOCUMENT_UPLOADED', '192.168.1.100', 'Mozilla/5.0', 'hash_gen_001_a1b2c3d4e5f6789012345678901234567890abcdef', 'hash_gen_002_b2c3d4e5f678901234567890123456789012abcdef', NOW() - INTERVAL '13 days'),
('a0000000-0000-0000-0000-000000000003', '60000000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000002', '70000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000005', 'DOCUMENT_UPLOADED', '192.168.1.105', 'Mozilla/5.0', 'hash_gen_002_b2c3d4e5f678901234567890123456789012abcdef', 'hash_gen_003_c3d4e5f67890123456789012345678901234abcdef', NOW() - INTERVAL '5 days'),
('a0000000-0000-0000-0000-000000000004', '60000000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000005', NULL, '20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', 'DOCUMENT_UPLOADED', '192.168.1.102', 'Mozilla/5.0', 'hash_gen_003_c3d4e5f67890123456789012345678901234abcdef', 'hash_gen_004_d4e5f6789012345678901234567890123456abcdef', NOW() - INTERVAL '3 days'),
('a0000000-0000-0000-0000-000000000005', '60000000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000001', NULL, '20000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000001', 'PRESIGNED_URL_GENERATED', '192.168.2.10', 'Mozilla/5.0', 'hash_gen_004_d4e5f6789012345678901234567890123456abcdef', 'hash_gen_005_e5f678901234567890123456789012345678abcdef', NOW() - INTERVAL '2 days')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 12. COURT BENCHES
-- ============================================================
INSERT INTO public.court_benches (id, department_id, bench_name, bench_type, presiding_judge_id, is_active) VALUES
('b0000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'Cyber Crime Court - Delhi', 'special', '20000000-0000-0000-0000-000000000007', true),
('b0000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', 'Sessions Court - Delhi', 'sessions', '20000000-0000-0000-0000-000000000008', true)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 13. COURT HEARINGS
-- ============================================================
INSERT INTO public.court_hearings (id, case_id, bench_id, hearing_date, hearing_purpose, status, adjournment_reason, next_hearing_date, created_at) VALUES
('b1000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', NOW() + INTERVAL '5 days', 'Bail Hearing', 'scheduled', NULL, NULL, NOW() - INTERVAL '2 days'),
('b1000000-0000-0000-0000-000000000002', '60000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000002', NOW() + INTERVAL '10 days', 'Evidence Examination', 'scheduled', NULL, NULL, NOW() - INTERVAL '1 day'),
('b1000000-0000-0000-0000-000000000003', '60000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', NOW() - INTERVAL '3 days', 'Initial Hearing', 'completed', NULL, NOW() + INTERVAL '5 days', NOW() - INTERVAL '10 days')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 14. COURT ORDERS
-- ============================================================
INSERT INTO public.court_orders (id, case_id, hearing_id, order_number, order_type, order_summary, issuing_judge_id, document_id, effective_date, expiry_date, enforcement_status, created_at) VALUES
('b2000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000003', 'ORD-CCD-2026-001', 'BAIL', 'Bail granted with conditions. Accused to surrender passport.', '20000000-0000-0000-0000-000000000007', NULL, NOW() - INTERVAL '3 days', NULL, 'enforced', NOW() - INTERVAL '3 days'),
('b2000000-0000-0000-0000-000000000002', '60000000-0000-0000-0000-000000000002', NULL, 'ORD-HMD-2026-045', 'SEARCH_WARRANT', 'Warrant issued for search of accused residence at Sector 15.', '20000000-0000-0000-0000-000000000008', NULL, NOW() - INTERVAL '5 days', NOW() + INTERVAL '25 days', 'executed', NOW() - INTERVAL '5 days')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 15. ORDER SHEETS
-- ============================================================
INSERT INTO public.order_sheets (id, case_id, hearing_id, order_sheet_number, proceeding_summary, advocates_present, accused_presence_status, document_id, recorded_by_user_id, created_at) VALUES
('b3000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000003', 'OS-CCD-2026-001', 'Bail hearing conducted. Prosecution presented initial evidence. Defense argued for bail on medical grounds.', '[{"name": "Adv. Suresh Patel", "for": "Prosecution"}, {"name": "Adv. Meena Joshi", "for": "Accused"}]', 'present', NULL, '20000000-0000-0000-0000-000000000010', NOW() - INTERVAL '3 days')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 16. CASE STAGE HISTORY
-- ============================================================
INSERT INTO public.case_stage_history (id, case_id, previous_stage, new_stage, changed_by_order_id, changed_by_user_id, remarks, changed_at) VALUES
('b4000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', NULL, 'investigation', NULL, '20000000-0000-0000-0000-000000000001', 'FIR registered. Investigation initiated.', NOW() - INTERVAL '15 days'),
('b4000000-0000-0000-0000-000000000002', '60000000-0000-0000-0000-000000000001', 'investigation', 'charge_framed', 'b2000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000007', 'Charge sheet filed in court.', NOW() - INTERVAL '3 days'),
('b4000000-0000-0000-0000-000000000003', '60000000-0000-0000-0000-000000000002', NULL, 'investigation', NULL, '20000000-0000-0000-0000-000000000002', 'FIR registered. Murder investigation started.', NOW() - INTERVAL '7 days')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 17. DIGITAL SIGNATURES
-- ============================================================
INSERT INTO public.digital_signatures (id, document_version_id, signer_id, signer_department_id, signature_hash, cert_serial_number, timestamp_seal, signed_at) VALUES
('b5000000-0000-0000-0000-000000000001', '90000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'sig_hash_a1b2c3d4e5f6789012345678901234567890abcdef1234567890', 'CERT-2026-001', 'tsp_seal_001', NOW() - INTERVAL '15 days'),
('b5000000-0000-0000-0000-000000000002', '90000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000005', 'sig_hash_b2c3d4e5f67890123456789012345678901234abcdef1234567890', 'CERT-2026-002', 'tsp_seal_002', NOW() - INTERVAL '5 days')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 18. DOCUMENT AI METADATA
-- ============================================================
INSERT INTO public.document_ai_metadata (id, version_id, ocr_extracted_text, ai_summary, extracted_entities, vector_embedding_id, processed_at) VALUES
('b6000000-0000-0000-0000-000000000001', '90000000-0000-0000-0000-000000000001', 'First Information Report under section 420, 406 IPC...', 'FIR registered for cyber fraud involving online banking scam. Multiple victims affected.', '{"sections": ["420 IPC", "406 IPC"], "victim_count": 15, "amount_involved": "2.5 crores"}', 'vec_001', NOW() - INTERVAL '14 days'),
('b6000000-0000-0000-0000-000000000002', '90000000-0000-0000-0000-000000000002', 'Post-Mortem Report... Cause of death: Single stab wound...', 'Post-mortem confirms single stab wound to chest as cause of death. Time of death estimated at 10 PM.', '{"cause_of_death": "stab wound", "time_of_death": "22:00", "weapon_type": "sharp object"}', 'vec_002', NOW() - INTERVAL '4 days')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 19. INTER-DEPARTMENT SHARES
-- ============================================================
INSERT INTO public.inter_department_shares (id, document_id, source_department_id, target_department_id, granted_by_user_id, access_level, reason, valid_from, expires_at, status) VALUES
('b7000000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000001', 'read', 'Forensic analysis of digital evidence required', NOW() - INTERVAL '10 days', NOW() + INTERVAL '20 days', 'active'),
('b7000000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000002', 'read', 'Cross-department reference for cyber crime linkage', NOW() - INTERVAL '3 days', NOW() + INTERVAL '27 days', 'active')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 20. WARRANTS AND SUMMONS
-- ============================================================
INSERT INTO public.warrants_and_summons (id, court_order_id, case_id, notice_type, target_person_details, assigned_police_station_id, executing_officer_id, execution_status, return_date, created_at) VALUES
('b8000000-0000-0000-0000-000000000001', 'b2000000-0000-0000-0000-000000000002', '60000000-0000-0000-0000-000000000002', 'SEARCH_WARRANT', '{"name": "Ajay Kumar", "address": "Flat 302, Sector 15, Noida", "description": "Primary suspect"}', '10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000002', 'executed', NOW() - INTERVAL '4 days', NOW() - INTERVAL '5 days'),
('b8000000-0000-0000-0000-000000000002', 'b2000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', 'SUMMONS', '{"name": "Vijay Singh", "address": "45, Lajpat Nagar, Delhi", "role": "witness"}', '10000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', 'pending', NOW() + INTERVAL '7 days', NOW() - INTERVAL '1 day')
ON CONFLICT (id) DO NOTHING;


-- ============================================================
-- 21. REVOKED TOKENS
-- ============================================================
INSERT INTO public.revoked_tokens (token_jti, revoked_at, expires_at) VALUES
('jti-revoked-001-a1b2c3d4e5f6', NOW() - INTERVAL '2 days', NOW() + INTERVAL '28 days'),
('jti-revoked-002-b2c3d4e5f6a7', NOW() - INTERVAL '1 day', NOW() + INTERVAL '29 days')
ON CONFLICT (token_jti) DO NOTHING;

-- ============================================================
-- 22. USER MAPPING (Bridge between registration and operational)
-- ============================================================
-- Note: This table bridges the registration users (Integer ID) with operational users (UUID)
-- For test data, we map registration user IDs 1-3 to operational users
-- In production, these are created automatically by provision_operational_user()

-- First, ensure the user_mapping table exists
CREATE TABLE IF NOT EXISTS public.user_mapping (
    registration_user_id INTEGER NOT NULL,
    operational_user_id UUID NOT NULL REFERENCES public.users(id),
    mapped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (registration_user_id)
);

-- Insert test mappings (registration_user_id 1,2,3 mapped to operational users)
INSERT INTO public.user_mapping (registration_user_id, operational_user_id) VALUES
(1, '20000000-0000-0000-0000-000000000001'),
(2, '20000000-0000-0000-0000-000000000002'),
(3, '20000000-0000-0000-0000-000000000003')
ON CONFLICT (registration_user_id) DO NOTHING;

-- ============================================================
-- VERIFICATION QUERIES (Run these to verify data)
-- ============================================================

-- Uncomment to verify:
-- SELECT 'departments' as table_name, COUNT(*) as count FROM public.departments
-- UNION ALL SELECT 'users', COUNT(*) FROM public.users
-- UNION ALL SELECT 'roles', COUNT(*) FROM public.roles
-- UNION ALL SELECT 'user_departments', COUNT(*) FROM public.user_departments
-- UNION ALL SELECT 'cases', COUNT(*) FROM public.cases
-- UNION ALL SELECT 'documents', COUNT(*) FROM public.documents
-- UNION ALL SELECT 'document_versions', COUNT(*) FROM public.document_versions
-- UNION ALL SELECT 'chain_of_custody_logs', COUNT(*) FROM public.chain_of_custody_logs
-- UNION ALL SELECT 'user_mapping', COUNT(*) FROM public.user_mapping;

