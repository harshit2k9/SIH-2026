CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE FUNCTION process_secure_audit_trail()
RETURNS TRIGGER AS $$
DECLARE
    v_prev_hash VARCHAR(64);
    v_current_hash VARCHAR(64);
BEGIN
    -- Get the last current_log_hash from chain_of_custody_logs
    SELECT current_log_hash INTO v_prev_hash 
    FROM chain_of_custody_logs 
    ORDER BY created_at DESC, id DESC 
    LIMIT 1;

    IF v_prev_hash IS NULL THEN
        v_prev_hash := '0000000000000000000000000000000000000000000000000000000000000000';
    END IF;

    -- Compute SHA-256 hash
    v_current_hash := encode(
        digest(
            COALESCE(v_prev_hash, '') || 
            NEW.action || 
            NEW.actor_id::text || 
            NEW.case_id::text || 
            COALESCE(NEW.created_at::text, now()::text), 
            'sha256'
        ), 
        'hex'
    );

    NEW.previous_log_hash := v_prev_hash;
    NEW.current_log_hash := v_current_hash;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_chain_of_custody_hash ON chain_of_custody_logs;

CREATE TRIGGER trg_chain_of_custody_hash
BEFORE INSERT ON chain_of_custody_logs
FOR EACH ROW
EXECUTE FUNCTION process_secure_audit_trail();