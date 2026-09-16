-- 04_seed_data.sql
-- Coherent sample data. Run after 01, 02 and 03.

BEGIN;

INSERT INTO evidence_providers (id,provider_type,full_name_or_org,contact_info,identification_number,clearance_verified) VALUES
('55555555-5555-5555-5555-555555555555','POLICE_OFFICER','Rahul Verma','{"phone":"+91-9000000001"}'::jsonb,'POL-001',TRUE);

INSERT INTO cases (id,case_number,title,description,classification_level,status,primary_department_id,lead_investigator_id,created_by) VALUES
('66666666-6666-6666-6666-666666666666','CASE-2026-0001','Digital Evidence Investigation',
'Investigation involving suspected unauthorized access to confidential digital records.',4,'OPEN',
'11111111-1111-1111-1111-111111111111','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee');

INSERT INTO evidence_items (id,case_id,evidence_number,provider_id,title,evidence_type,storage_location,current_status,seized_at,seized_by_user_id,created_by) VALUES
('77777777-7777-7777-7777-777777777777','66666666-6666-6666-6666-666666666666','EVD-2026-0001',
'55555555-5555-5555-5555-555555555555','Suspect Laptop','DIGITAL_DEVICE','Evidence Locker A-12','IN_CUSTODY',
CURRENT_TIMESTAMP,'cccccccc-cccc-cccc-cccc-cccccccccccc','cccccccc-cccc-cccc-cccc-cccccccccccc');

INSERT INTO evidence_custody_transfers (id,evidence_item_id,released_by_user_id,received_by_user_id,purpose,transfer_timestamp,physical_condition_notes) VALUES
('88888888-8888-8888-8888-888888888888','77777777-7777-7777-7777-777777777777',
'cccccccc-cccc-cccc-cccc-cccccccccccc','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
'Digital forensic examination',CURRENT_TIMESTAMP,'Device received in sealed condition.');

INSERT INTO documents (id,case_id,evidence_item_id,document_number,title,document_type,confidentiality_level,current_version,created_by,updated_by,updated_at,is_locked) VALUES
('99999999-9999-9999-9999-999999999999','66666666-6666-6666-6666-666666666666','77777777-7777-7777-7777-777777777777',
'DOC-2026-0001','Forensic Examination Report','EVIDENCE_REPORT',4,1,
'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',CURRENT_TIMESTAMP,FALSE),
('99999999-9999-9999-9999-999999999998','66666666-6666-6666-6666-666666666666',NULL,
'DOC-2026-0002','Investigation Summary','CASE_REPORT',3,1,
'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',CURRENT_TIMESTAMP,FALSE),
('99999999-9999-9999-9999-999999999997','66666666-6666-6666-6666-666666666666',NULL,
'DOC-2026-0003','Order Sheet Document','COURT_FILING',3,1,
'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb','bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',CURRENT_TIMESTAMP,FALSE),
('99999999-9999-9999-9999-999999999996','66666666-6666-6666-6666-666666666666',NULL,
'DOC-2026-0004','Court Order Document','COURT_ORDER',4,1,
'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb','bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',CURRENT_TIMESTAMP,TRUE);

INSERT INTO document_versions (id,document_id,version_number,storage_uri,file_size_bytes,file_mime_type,sha256_checksum,kms_key_id,uploaded_by) VALUES
('aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1','99999999-9999-9999-9999-999999999999',1,'s3://legal-dms/cases/CASE-2026-0001/forensic-report-v1.pdf',245760,'application/pdf','sha256-demo-checksum-forensic-report-v1','kms-demo-key-001','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
('aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa2','99999999-9999-9999-9999-999999999998',1,'s3://legal-dms/cases/CASE-2026-0001/investigation-summary-v1.pdf',163840,'application/pdf','sha256-demo-checksum-investigation-summary-v1','kms-demo-key-002','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
('aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa3','99999999-9999-9999-9999-999999999997',1,'s3://legal-dms/cases/CASE-2026-0001/order-sheet-v1.pdf',131072,'application/pdf','sha256-demo-checksum-order-sheet-v1','kms-demo-key-003','bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
('aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa4','99999999-9999-9999-9999-999999999996',1,'s3://legal-dms/cases/CASE-2026-0001/court-order-v1.pdf',147456,'application/pdf','sha256-demo-checksum-court-order-v1','kms-demo-key-004','bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb');

INSERT INTO document_ai_metadata (id,version_id,ocr_extracted_text,ai_summary,extracted_entities,vector_embedding_id,processed_at,created_by) VALUES
('bbbbbbb1-bbbb-bbbb-bbbb-bbbbbbbbbbb1','aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
'Digital forensic examination report for CASE-2026-0001.','Forensic report associated with the seized laptop.',
'{"case_number":"CASE-2026-0001","evidence_number":"EVD-2026-0001"}'::jsonb,'embedding-demo-001',CURRENT_TIMESTAMP,
'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee');

INSERT INTO inter_department_shares (id,document_id,source_department_id,target_department_id,granted_by_user_id,access_level,reason,valid_from,expires_at,status,created_by) VALUES
('cccccccc-1111-2222-3333-444444444444','99999999-9999-9999-9999-999999999998',
'11111111-1111-1111-1111-111111111111','22222222-2222-2222-2222-222222222222',
'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','VIEW','Court review of investigation summary',
CURRENT_TIMESTAMP,CURRENT_TIMESTAMP+INTERVAL '30 days','ACTIVE','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa');

INSERT INTO chain_of_custody_logs (id,case_id,document_id,evidence_id,actor_id,actor_department_id,action,ip_address,user_agent,previous_log_hash,current_log_hash,created_by) VALUES
('dddddddd-1111-2222-3333-444444444444','66666666-6666-6666-6666-666666666666',
'99999999-9999-9999-9999-999999999999','77777777-7777-7777-7777-777777777777',
'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','11111111-1111-1111-1111-111111111111',
'DOCUMENT_CREATED','192.168.1.100','DemoClient/1.0','GENESIS','demo-current-hash-001','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa');

INSERT INTO digital_signatures (id,document_version_id,signer_id,signer_department_id,signature_hash,cert_serial_number,timestamp_seal,signed_at,created_by) VALUES
('eeeeeeee-1111-2222-3333-444444444444','aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb','22222222-2222-2222-2222-222222222222',
'demo-digital-signature-hash-001','CERT-DEMO-001','2026-01-15T10:30:00Z',CURRENT_TIMESTAMP,
'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb');

INSERT INTO court_benches (id,department_id,bench_name,bench_type,presiding_judge_id,is_active,created_by) VALUES
('ffffffff-1111-2222-3333-444444444444','22222222-2222-2222-2222-222222222222','Cyber Crime Bench 1','SPECIAL',
'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',TRUE,'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee');

INSERT INTO court_hearings (id,case_id,bench_id,hearing_date,hearing_purpose,status,next_hearing_date,created_by) VALUES
('12121212-1111-2222-3333-444444444444','66666666-6666-6666-6666-666666666666',
'ffffffff-1111-2222-3333-444444444444',CURRENT_TIMESTAMP+INTERVAL '7 days','Initial hearing','SCHEDULED',
CURRENT_TIMESTAMP+INTERVAL '21 days','bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb');

INSERT INTO order_sheets (id,case_id,hearing_id,order_sheet_number,proceeding_summary,advocates_present,accused_presence_status,document_id,recorded_by_user_id,created_by) VALUES
('13131313-1111-2222-3333-444444444444','66666666-6666-6666-6666-666666666666',
'12121212-1111-2222-3333-444444444444','OS-2026-0001','Initial proceedings recorded.',
'[{"name":"Demo Advocate","role":"DEFENCE"}]'::jsonb,'PRESENT',
'99999999-9999-9999-9999-999999999997','bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb','bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb');

INSERT INTO court_orders (id,case_id,hearing_id,order_number,order_type,order_summary,issuing_judge_id,document_id,effective_date,expiry_date,enforcement_status,created_by) VALUES
('14141414-1111-2222-3333-444444444444','66666666-6666-6666-6666-666666666666',
'12121212-1111-2222-3333-444444444444','ORD-2026-0001','DOCUMENT_PRODUCTION',
'Court directs production and review of relevant digital evidence.',
'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb','99999999-9999-9999-9999-999999999996',
CURRENT_TIMESTAMP,CURRENT_TIMESTAMP+INTERVAL '30 days','ACTIVE','bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb');

INSERT INTO warrants_and_summons (id,court_order_id,case_id,notice_type,target_person_details,assigned_police_station_id,executing_officer_id,execution_status,return_date,created_by) VALUES
('15151515-1111-2222-3333-444444444444','14141414-1111-2222-3333-444444444444',
'66666666-6666-6666-6666-666666666666','SUMMONS',
'{"name":"Demo Witness","identifier":"WIT-001"}'::jsonb,
'33333333-3333-3333-3333-333333333333','cccccccc-cccc-cccc-cccc-cccccccccccc','PENDING',
CURRENT_TIMESTAMP+INTERVAL '20 days','bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb');

INSERT INTO case_stage_history (id,case_id,previous_stage,new_stage,changed_by_order_id,changed_by_user_id,remarks) VALUES
('16161616-1111-2222-3333-444444444444','66666666-6666-6666-6666-666666666666',
'INVESTIGATION','COURT_PROCEEDINGS','14141414-1111-2222-3333-444444444444',
'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb','Case moved to court proceedings following initial order.');

COMMIT;

SELECT 'cases' AS table_name,COUNT(*) AS records FROM cases
UNION ALL SELECT 'evidence_items',COUNT(*) FROM evidence_items
UNION ALL SELECT 'documents',COUNT(*) FROM documents
UNION ALL SELECT 'document_versions',COUNT(*) FROM document_versions
UNION ALL SELECT 'court_hearings',COUNT(*) FROM court_hearings
UNION ALL SELECT 'order_sheets',COUNT(*) FROM order_sheets
UNION ALL SELECT 'court_orders',COUNT(*) FROM court_orders
UNION ALL SELECT 'warrants_and_summons',COUNT(*) FROM warrants_and_summons;

SELECT c.case_number,e.evidence_number,d.document_number,
       d.case_id=c.id AS document_case_match,
       e.case_id=c.id AS evidence_case_match
FROM cases c
LEFT JOIN evidence_items e ON e.case_id=c.id
LEFT JOIN documents d ON d.case_id=c.id
ORDER BY c.case_number,d.document_number;
