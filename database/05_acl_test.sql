-- ============================================================
-- 05_acl_test.sql
-- Secure Digital Document Management System
-- ACL / Access Control Verification
-- ============================================================

-- ============================================================
-- TEST 1: ROLE PERMISSIONS
-- Shows permissions assigned to each role
-- ============================================================

SELECT
    name AS role,
    permissions
FROM roles
ORDER BY name;


-- ============================================================
-- TEST 2: USER -> DEPARTMENT -> ROLE
-- Shows which role and department each user belongs to
-- ============================================================

SELECT
    u.full_name,
    u.email,
    d.name AS department,
    r.name AS role
FROM users u
JOIN user_departments ud
    ON ud.user_id = u.id
JOIN departments d
    ON d.id = ud.department_id
JOIN roles r
    ON r.id = ud.role_id
ORDER BY u.full_name;


-- ============================================================
-- TEST 3: DOCUMENT PERMISSIONS
-- Checks VIEW / EDIT / SHARE / DELETE permissions
-- based on the user's role
-- ============================================================

SELECT
    u.full_name,
    r.name AS role,
    d.document_number,
    d.title,

    CASE
        WHEN COALESCE((r.permissions->'document'->>'view')::boolean, false)
        THEN 'ALLOW'
        ELSE 'DENY'
    END AS view_decision,

    CASE
        WHEN COALESCE((r.permissions->'document'->>'edit')::boolean, false)
        THEN 'ALLOW'
        ELSE 'DENY'
    END AS edit_decision,

    CASE
        WHEN COALESCE((r.permissions->'document'->>'share')::boolean, false)
        THEN 'ALLOW'
        ELSE 'DENY'
    END AS share_decision,

    CASE
        WHEN COALESCE((r.permissions->'document'->>'delete')::boolean, false)
        THEN 'ALLOW'
        ELSE 'DENY'
    END AS delete_decision

FROM users u
JOIN user_departments ud
    ON ud.user_id = u.id
JOIN roles r
    ON r.id = ud.role_id
CROSS JOIN documents d
ORDER BY u.full_name, d.document_number;


-- ============================================================
-- TEST 4: ACTIVE DEPARTMENT SHARES
-- Shows documents shared between departments
-- ============================================================

SELECT
    d.document_number,
    d.title,
    source_dept.name AS source_department,
    target_dept.name AS target_department,
    s.access_level,
    s.status,
    s.valid_from,
    s.expires_at,

    CASE
        WHEN s.status = 'ACTIVE'
        THEN 'ACTIVE'
        ELSE 'INACTIVE'
    END AS share_status,

    CASE
        WHEN s.valid_from <= CURRENT_TIMESTAMP
         AND (s.expires_at IS NULL
              OR s.expires_at > CURRENT_TIMESTAMP)
        THEN 'CURRENT'
        ELSE 'EXPIRED / NOT_STARTED'
    END AS time_status

FROM inter_department_shares s
JOIN documents d
    ON d.id = s.document_id
JOIN departments source_dept
    ON source_dept.id = s.source_department_id
JOIN departments target_dept
    ON target_dept.id = s.target_department_id
ORDER BY d.document_number;


-- ============================================================
-- TEST 5: FINAL VIEW ACL DECISION
--
-- Logic:
-- 1. User must have VIEW permission.
-- 2. User's department can directly access documents
--    belonging to its own case department.
-- 3. Otherwise, an ACTIVE and currently valid
--    inter-department share is required.
-- ============================================================

SELECT
    u.full_name,
    r.name AS role,
    user_dept.name AS user_department,
    d.document_number,
    d.title,

    CASE
        WHEN COALESCE(
            (r.permissions->'document'->>'view')::boolean,
            false
        ) = false
        THEN 'DENY - ROLE HAS NO VIEW PERMISSION'

        WHEN ud.department_id = c.primary_department_id
        THEN 'ALLOW - SAME DEPARTMENT'

        WHEN EXISTS (
            SELECT 1
            FROM inter_department_shares s
            WHERE s.document_id = d.id
              AND s.target_department_id = ud.department_id
              AND s.status = 'ACTIVE'
              AND s.valid_from <= CURRENT_TIMESTAMP
              AND (
                  s.expires_at IS NULL
                  OR s.expires_at > CURRENT_TIMESTAMP
              )
        )
        THEN 'ALLOW - ACTIVE DOCUMENT SHARE'

        ELSE 'DENY - NO VALID ACCESS'
    END AS final_view_decision

FROM users u
JOIN user_departments ud
    ON ud.user_id = u.id
JOIN departments user_dept
    ON user_dept.id = ud.department_id
JOIN roles r
    ON r.id = ud.role_id
CROSS JOIN documents d
JOIN cases c
    ON c.id = d.case_id

ORDER BY u.full_name, d.document_number;


-- ============================================================
-- TEST 6: ACL SUMMARY
-- Gives a simple count of ALLOW / DENY decisions
-- ============================================================

WITH acl_result AS (
    SELECT
        u.full_name,
        r.name AS role,
        d.document_number,

        CASE
            WHEN COALESCE(
                (r.permissions->'document'->>'view')::boolean,
                false
            ) = false
            THEN 'DENY'

            WHEN ud.department_id = c.primary_department_id
            THEN 'ALLOW'

            WHEN EXISTS (
                SELECT 1
                FROM inter_department_shares s
                WHERE s.document_id = d.id
                  AND s.target_department_id = ud.department_id
                  AND s.status = 'ACTIVE'
                  AND s.valid_from <= CURRENT_TIMESTAMP
                  AND (
                      s.expires_at IS NULL
                      OR s.expires_at > CURRENT_TIMESTAMP
                  )
            )
            THEN 'ALLOW'

            ELSE 'DENY'
        END AS decision

    FROM users u
    JOIN user_departments ud
        ON ud.user_id = u.id
    JOIN roles r
        ON r.id = ud.role_id
    CROSS JOIN documents d
    JOIN cases c
        ON c.id = d.case_id
)

SELECT
    decision,
    COUNT(*) AS total
FROM acl_result
GROUP BY decision
ORDER BY decision;


-- ============================================================
-- END OF ACL TESTS
-- ============================================================