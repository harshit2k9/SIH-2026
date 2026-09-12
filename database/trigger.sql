CREATE OR REPLACE FUNCTION process_secure_audit_trail()
RETURNS TRIGGER AS $$
DECLARE
    v_prev_hash CHAR(64);
    v_current_hash CHAR(64);
BEGIN
    SELECT current_hash INTO v_prev_hash FROM audit_check ORDER BY id DESC LIMIT 1;
    IF v_prev_hash IS NULL THEN
        v_prev_hash := '0000000000000000000000000000000000000000000000000000000000000000';
    END IF;

    v_current_hash := encode(digest(v_prev_hash || TG_OP || NEW.id::text || now()::text, 'sha256'), 'hex');

    INSERT INTO audit_check (
        event_type, user_id, case_id, document_id, event_timestamp, previous_hash, current_hash
    ) VALUES (
        TG_OP, NEW.user_id, NEW.case_id, NEW.id, now(), v_prev_hash, v_current_hash
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;