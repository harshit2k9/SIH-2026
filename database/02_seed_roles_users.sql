-- 02_seed_roles_users.sql
BEGIN;

INSERT INTO departments (id,name,code,parent_id) VALUES
('11111111-1111-1111-1111-111111111111','Crime Investigation Unit','CIU',NULL),
('22222222-2222-2222-2222-222222222222','Court Department','COURT',NULL),
('33333333-3333-3333-3333-333333333333','Central Police Station','CPS',NULL);

INSERT INTO users (id,full_name,email,badge_number,security_clearance_level,is_active) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','Akash Sharma','akash.sharma@example.com','CIU-001',4,TRUE),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb','Riya Mehta','riya.mehta@example.com','CRT-001',5,TRUE),
('cccccccc-cccc-cccc-cccc-cccccccccccc','Rahul Verma','rahul.verma@example.com','POL-001',3,TRUE),
('dddddddd-dddd-dddd-dddd-dddddddddddd','Neha Kapoor','neha.kapoor@example.com','CIU-002',3,TRUE),
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee','System Administrator','admin@example.com','ADM-001',5,TRUE);

INSERT INTO roles (id,name,permissions) VALUES
('aaaa1111-1111-1111-1111-111111111111','INVESTIGATOR',
'{"case":{"view":true,"edit":true,"share":true,"delete":false},"document":{"view":true,"edit":true,"share":true,"delete":false},"evidence":{"view":true,"edit":true,"share":false,"delete":false}}'::jsonb),
('bbbb2222-2222-2222-2222-222222222222','JUDGE',
'{"case":{"view":true,"edit":false,"share":false,"delete":false},"document":{"view":true,"edit":false,"share":false,"delete":false},"court_order":{"view":true,"edit":true,"share":true,"delete":false}}'::jsonb),
('cccc3333-3333-3333-3333-333333333333','OFFICER',
'{"case":{"view":true,"edit":false,"share":false,"delete":false},"document":{"view":true,"edit":false,"share":false,"delete":false},"evidence":{"view":true,"edit":false,"share":false,"delete":false}}'::jsonb),
('dddd4444-4444-4444-4444-444444444444','ADMIN',
'{"case":{"view":true,"edit":true,"share":true,"delete":true},"document":{"view":true,"edit":true,"share":true,"delete":true},"evidence":{"view":true,"edit":true,"share":true,"delete":true},"user":{"view":true,"edit":true,"delete":true}}'::jsonb);

INSERT INTO user_departments (id,user_id,department_id,role_id,is_primary) VALUES
('10000000-0000-0000-0000-000000000001','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','11111111-1111-1111-1111-111111111111','aaaa1111-1111-1111-1111-111111111111',TRUE),
('10000000-0000-0000-0000-000000000002','bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb','22222222-2222-2222-2222-222222222222','bbbb2222-2222-2222-2222-222222222222',TRUE),
('10000000-0000-0000-0000-000000000003','cccccccc-cccc-cccc-cccc-cccccccccccc','33333333-3333-3333-3333-333333333333','cccc3333-3333-3333-3333-333333333333',TRUE),
('10000000-0000-0000-0000-000000000004','dddddddd-dddd-dddd-dddd-dddddddddddd','11111111-1111-1111-1111-111111111111','aaaa1111-1111-1111-1111-111111111111',TRUE),
('10000000-0000-0000-0000-000000000005','eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee','11111111-1111-1111-1111-111111111111','dddd4444-4444-4444-4444-444444444444',TRUE);

COMMIT;
