CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE FUNCTION process_secure_audit_trail()
RETURNS TRIGGER AS $$
DECLARE
    v_prev_hash CHAR(64);
    v_current_hash CHAR(64);
BEGIN
    SELECT current_hash INTO v_prev_hash 
    FROM chain_of_custody_logs 
    ORDER BY id DESC 
    LIMIT 1;

    IF v_prev_hash IS NULL THEN
        v_prev_hash := '0000000000000000000000000000000000000000000000000000000000000000';
    END IF;

    v_current_hash := encode(
        digest(
            v_prev_hash || 
            NEW.event_type || 
            COALESCE(NEW.user_id::text, '') || 
            COALESCE(NEW.event_timestamp::text, now()::text), 
            'sha256'
        ), 
        'hex'
    );

    NEW.previous_hash := v_prev_hash;
    NEW.current_hash := v_current_hash;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_chain_of_custody_hash ON chain_of_custody_logs;

CREATE TRIGGER trg_chain_of_custody_hash
BEFORE INSERT ON chain_of_custody_logs
FOR EACH ROW
EXECUTE FUNCTION process_secure_audit_trail();