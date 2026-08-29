-- Minimal seed data so a test upload has a valid user/case/permission to work with.
-- Run AFTER schema.sql. Matches user_id=1 used by generate_test_token.py by default.

INSERT INTO users (id, username, role, is_active)
VALUES (1, 'test_investigator', 'investigator', TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO cases (id, case_number, title, status)
VALUES (1, 'CASE-2026-001', 'Test Case File', 'open')
ON CONFLICT (id) DO NOTHING;

INSERT INTO case_assignments (case_id, user_id, can_upload, can_view)
VALUES (1, 1, TRUE, TRUE)
ON CONFLICT (case_id, user_id) DO NOTHING;

-- Reset sequences so subsequent inserts don't collide with these hardcoded IDs.
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('cases_id_seq', (SELECT MAX(id) FROM cases));
