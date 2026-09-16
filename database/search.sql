-- Enable trigram extension for fast text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create GIN index on event_type and other text fields for fast full-text/fuzzy search
CREATE INDEX IF NOT EXISTS idx_chain_logs_event_type_gin 
ON chain_of_custody_logs USING gin (event_type gin_trgm_ops);