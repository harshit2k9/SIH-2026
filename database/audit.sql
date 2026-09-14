CREATE TABLE chain_of_custody_logs (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(80) NOT NULL,
    user_id INT NOT NULL,
    case_id INT,
    document_id INT,
    document_version_id INT,
    event_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB,
    previous_hash  CHAR(64) NOT NULL,
    current_hash  CHAR(64) NOT NULL);
    REVOKE UPDATE, DELETE ON chain_of_custody_logs FROM PUBLIC;