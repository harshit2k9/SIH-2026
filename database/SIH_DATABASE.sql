\restrict GJYfOpc0BrHzEke1BOQj1zYgMg2poFMqLHRvNLHd9mRuobZYUuCM5W4LWFgwsbC
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;
SET default_tablespace = '';
SET default_table_access_method = heap;
CREATE TABLE public.case_stage_history (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_id uuid NOT NULL,
    previous_stage character varying,
    new_stage character varying NOT NULL,
    changed_by_order_id uuid,
    changed_by_user_id uuid NOT NULL,
    remarks text,
    changed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.cases (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_number character varying NOT NULL,
    title character varying NOT NULL,
    description text,
    classification_level integer,
    status character varying NOT NULL,
    primary_department_id uuid NOT NULL,
    lead_investigator_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.chain_of_custody_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_id uuid NOT NULL,
    document_id uuid,
    evidence_id uuid,
    actor_id uuid NOT NULL,
    actor_department_id uuid NOT NULL,
    action character varying NOT NULL,
    ip_address character varying,
    user_agent text,
    previous_log_hash character varying,
    current_log_hash character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.court_benches (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    department_id uuid NOT NULL,
    bench_name character varying NOT NULL,
    bench_type character varying NOT NULL,
    presiding_judge_id uuid NOT NULL,
    is_active boolean DEFAULT true
);
CREATE TABLE public.court_hearings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_id uuid NOT NULL,
    bench_id uuid NOT NULL,
    hearing_date timestamp with time zone NOT NULL,
    hearing_purpose character varying NOT NULL,
    status character varying NOT NULL,
    adjournment_reason text,
    next_hearing_date timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.court_orders (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_id uuid NOT NULL,
    hearing_id uuid,
    order_number character varying NOT NULL,
    order_type character varying NOT NULL,
    order_summary text,
    issuing_judge_id uuid NOT NULL,
    document_id uuid,
    effective_date timestamp with time zone,
    expiry_date timestamp with time zone,
    enforcement_status character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.departments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying NOT NULL,
    code character varying NOT NULL,
    parent_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.digital_signatures (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_version_id uuid NOT NULL,
    signer_id uuid NOT NULL,
    signer_department_id uuid NOT NULL,
    signature_hash text NOT NULL,
    cert_serial_number character varying,
    timestamp_seal text,
    signed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.document_ai_metadata (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    version_id uuid NOT NULL,
    ocr_extracted_text text,
    ai_summary text,
    extracted_entities jsonb,
    vector_embedding_id character varying,
    processed_at timestamp with time zone
);
CREATE TABLE public.document_versions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_id uuid NOT NULL,
    version_number integer NOT NULL,
    storage_uri character varying NOT NULL,
    file_size_bytes bigint,
    file_mime_type character varying,
    sha256_checksum character varying,
    kms_key_id character varying,
    uploaded_by uuid,
    uploaded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_id uuid NOT NULL,
    evidence_item_id uuid,
    document_number character varying NOT NULL,
    title character varying NOT NULL,
    document_type character varying NOT NULL,
    confidentiality_level integer,
    current_version integer,
    created_by uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    is_locked boolean DEFAULT false
);
CREATE TABLE public.evidence_custody_transfers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    evidence_item_id uuid NOT NULL,
    released_by_user_id uuid,
    received_by_user_id uuid,
    purpose text,
    transfer_timestamp timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    physical_condition_notes text
);
CREATE TABLE public.evidence_items (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_id uuid NOT NULL,
    evidence_number character varying NOT NULL,
    provider_id uuid,
    title character varying NOT NULL,
    evidence_type character varying NOT NULL,
    storage_location character varying,
    current_status character varying NOT NULL,
    seized_at timestamp with time zone,
    seized_by_user_id uuid
);
CREATE TABLE public.evidence_providers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    provider_type character varying NOT NULL,
    full_name_or_org character varying NOT NULL,
    contact_info jsonb,
    identification_number character varying,
    clearance_verified boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.inter_department_shares (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_id uuid NOT NULL,
    source_department_id uuid NOT NULL,
    target_department_id uuid NOT NULL,
    granted_by_user_id uuid NOT NULL,
    access_level character varying NOT NULL,
    reason text,
    valid_from timestamp with time zone,
    expires_at timestamp with time zone,
    status character varying NOT NULL
);
CREATE TABLE public.order_sheets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_id uuid NOT NULL,
    hearing_id uuid NOT NULL,
    order_sheet_number character varying NOT NULL,
    proceeding_summary text,
    advocates_present jsonb,
    accused_presence_status character varying,
    document_id uuid,
    recorded_by_user_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.roles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying NOT NULL,
    permissions jsonb
);
CREATE TABLE public.user_departments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    department_id uuid NOT NULL,
    role_id uuid NOT NULL,
    is_primary boolean DEFAULT false,
    assigned_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    full_name character varying NOT NULL,
    email character varying NOT NULL,
    badge_number character varying,
    security_clearance_level integer,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE public.warrants_and_summons (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    court_order_id uuid NOT NULL,
    case_id uuid NOT NULL,
    notice_type character varying NOT NULL,
    target_person_details jsonb,
    assigned_police_station_id uuid,
    executing_officer_id uuid,
    execution_status character varying NOT NULL,
    return_date timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
COPY public.case_stage_history (id, case_id, previous_stage, new_stage, changed_by_order_id, changed_by_user_id, remarks, changed_at) FROM stdin;
\.
COPY public.cases (id, case_number, title, description, classification_level, status, primary_department_id, lead_investigator_id, created_at) FROM stdin;
\.
COPY public.chain_of_custody_logs (id, case_id, document_id, evidence_id, actor_id, actor_department_id, action, ip_address, user_agent, previous_log_hash, current_log_hash, created_at) FROM stdin;
\.
COPY public.court_benches (id, department_id, bench_name, bench_type, presiding_judge_id, is_active) FROM stdin;
\.
COPY public.court_hearings (id, case_id, bench_id, hearing_date, hearing_purpose, status, adjournment_reason, next_hearing_date, created_at) FROM stdin;
\.
COPY public.court_orders (id, case_id, hearing_id, order_number, order_type, order_summary, issuing_judge_id, document_id, effective_date, expiry_date, enforcement_status, created_at) FROM stdin;
\.
COPY public.departments (id, name, code, parent_id, created_at) FROM stdin;
\.
COPY public.digital_signatures (id, document_version_id, signer_id, signer_department_id, signature_hash, cert_serial_number, timestamp_seal, signed_at) FROM stdin;
\.
COPY public.document_ai_metadata (id, version_id, ocr_extracted_text, ai_summary, extracted_entities, vector_embedding_id, processed_at) FROM stdin;
\.
COPY public.document_versions (id, document_id, version_number, storage_uri, file_size_bytes, file_mime_type, sha256_checksum, kms_key_id, uploaded_by, uploaded_at) FROM stdin;
\.
COPY public.documents (id, case_id, evidence_item_id, document_number, title, document_type, confidentiality_level, current_version, created_by, created_at, is_locked) FROM stdin;
\.
COPY public.evidence_custody_transfers (id, evidence_item_id, released_by_user_id, received_by_user_id, purpose, transfer_timestamp, physical_condition_notes) FROM stdin;
\.
COPY public.evidence_items (id, case_id, evidence_number, provider_id, title, evidence_type, storage_location, current_status, seized_at, seized_by_user_id) FROM stdin;
\.
COPY public.evidence_providers (id, provider_type, full_name_or_org, contact_info, identification_number, clearance_verified, created_at) FROM stdin;
\.
COPY public.inter_department_shares (id, document_id, source_department_id, target_department_id, granted_by_user_id, access_level, reason, valid_from, expires_at, status) FROM stdin;
\.
COPY public.order_sheets (id, case_id, hearing_id, order_sheet_number, proceeding_summary, advocates_present, accused_presence_status, document_id, recorded_by_user_id, created_at) FROM stdin;
\.
COPY public.roles (id, name, permissions) FROM stdin;
\.
COPY public.user_departments (id, user_id, department_id, role_id, is_primary, assigned_at) FROM stdin;
\.
COPY public.users (id, full_name, email, badge_number, security_clearance_level, is_active, created_at) FROM stdin;
\.
COPY public.warrants_and_summons (id, court_order_id, case_id, notice_type, target_person_details, assigned_police_station_id, executing_officer_id, execution_status, return_date, created_at) FROM stdin;
\.
ALTER TABLE ONLY public.case_stage_history
    ADD CONSTRAINT case_stage_history_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.cases
    ADD CONSTRAINT cases_case_number_key UNIQUE (case_number);
ALTER TABLE ONLY public.cases
    ADD CONSTRAINT cases_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT chain_of_custody_logs_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.court_benches
    ADD CONSTRAINT court_benches_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.court_hearings
    ADD CONSTRAINT court_hearings_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_document_id_key UNIQUE (document_id);
ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_order_number_key UNIQUE (order_number);
ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_code_key UNIQUE (code);
ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.digital_signatures
    ADD CONSTRAINT digital_signatures_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.document_ai_metadata
    ADD CONSTRAINT document_ai_metadata_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.document_ai_metadata
    ADD CONSTRAINT document_ai_metadata_version_id_key UNIQUE (version_id);
ALTER TABLE ONLY public.document_versions
    ADD CONSTRAINT document_versions_document_id_version_number_key UNIQUE (document_id, version_number);
ALTER TABLE ONLY public.document_versions
    ADD CONSTRAINT document_versions_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_document_number_key UNIQUE (document_number);
ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.evidence_custody_transfers
    ADD CONSTRAINT evidence_custody_transfers_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.evidence_items
    ADD CONSTRAINT evidence_items_evidence_number_key UNIQUE (evidence_number);
ALTER TABLE ONLY public.evidence_items
    ADD CONSTRAINT evidence_items_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.evidence_providers
    ADD CONSTRAINT evidence_providers_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.inter_department_shares
    ADD CONSTRAINT inter_department_shares_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_hearing_id_key UNIQUE (hearing_id);
ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_order_sheet_number_key UNIQUE (order_sheet_number);
ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);
ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.user_departments
    ADD CONSTRAINT user_departments_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.user_departments
    ADD CONSTRAINT user_departments_user_id_department_id_role_id_key UNIQUE (user_id, department_id, role_id);
ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_badge_number_key UNIQUE (badge_number);
ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);
ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.warrants_and_summons
    ADD CONSTRAINT warrants_and_summons_pkey PRIMARY KEY (id);
CREATE INDEX idx_case_stage_history_case ON public.case_stage_history USING btree (case_id, changed_at DESC);
CREATE INDEX idx_case_stage_history_order ON public.case_stage_history USING btree (changed_by_order_id);
CREATE INDEX idx_case_stage_history_stage ON public.case_stage_history USING btree (new_stage);
CREATE INDEX idx_case_stage_history_user ON public.case_stage_history USING btree (changed_by_user_id);
CREATE INDEX idx_cases_classification ON public.cases USING btree (classification_level);
CREATE INDEX idx_cases_department ON public.cases USING btree (primary_department_id);
CREATE INDEX idx_cases_lead_investigator ON public.cases USING btree (lead_investigator_id);
CREATE INDEX idx_cases_status ON public.cases USING btree (status);
CREATE INDEX idx_court_benches_active ON public.court_benches USING btree (is_active);
CREATE INDEX idx_court_benches_department ON public.court_benches USING btree (department_id);
CREATE INDEX idx_court_benches_judge ON public.court_benches USING btree (presiding_judge_id);
CREATE INDEX idx_court_hearings_bench ON public.court_hearings USING btree (bench_id, hearing_date);
CREATE INDEX idx_court_hearings_case ON public.court_hearings USING btree (case_id, hearing_date DESC);
CREATE INDEX idx_court_hearings_next_date ON public.court_hearings USING btree (next_hearing_date);
CREATE INDEX idx_court_hearings_status ON public.court_hearings USING btree (status);
CREATE INDEX idx_court_orders_case ON public.court_orders USING btree (case_id, created_at DESC);
CREATE INDEX idx_court_orders_enforcement ON public.court_orders USING btree (enforcement_status);
CREATE INDEX idx_court_orders_hearing ON public.court_orders USING btree (hearing_id);
CREATE INDEX idx_court_orders_judge ON public.court_orders USING btree (issuing_judge_id);
CREATE INDEX idx_custody_logs_actor ON public.chain_of_custody_logs USING btree (actor_id, created_at DESC);
CREATE INDEX idx_custody_logs_case ON public.chain_of_custody_logs USING btree (case_id, created_at DESC);
CREATE INDEX idx_custody_logs_document ON public.chain_of_custody_logs USING btree (document_id, created_at DESC);
CREATE INDEX idx_custody_logs_evidence ON public.chain_of_custody_logs USING btree (evidence_id, created_at DESC);
CREATE INDEX idx_custody_transfers_evidence ON public.evidence_custody_transfers USING btree (evidence_item_id, transfer_timestamp DESC);
CREATE INDEX idx_departments_parent_id ON public.departments USING btree (parent_id);
CREATE INDEX idx_document_ai_metadata_embedding ON public.document_ai_metadata USING btree (vector_embedding_id);
CREATE INDEX idx_document_versions_checksum ON public.document_versions USING btree (sha256_checksum);
CREATE INDEX idx_document_versions_document ON public.document_versions USING btree (document_id, version_number DESC);
CREATE INDEX idx_document_versions_uploaded_by ON public.document_versions USING btree (uploaded_by);
CREATE INDEX idx_documents_case ON public.documents USING btree (case_id);
CREATE INDEX idx_documents_created_by ON public.documents USING btree (created_by);
CREATE INDEX idx_documents_evidence ON public.documents USING btree (evidence_item_id);
CREATE INDEX idx_documents_locked ON public.documents USING btree (is_locked);
CREATE INDEX idx_documents_type ON public.documents USING btree (document_type);
CREATE INDEX idx_evidence_items_case ON public.evidence_items USING btree (case_id);
CREATE INDEX idx_evidence_items_provider ON public.evidence_items USING btree (provider_id);
CREATE INDEX idx_evidence_items_seized_by ON public.evidence_items USING btree (seized_by_user_id);
CREATE INDEX idx_evidence_items_status ON public.evidence_items USING btree (current_status);
CREATE INDEX idx_order_sheets_case ON public.order_sheets USING btree (case_id);
CREATE INDEX idx_order_sheets_document ON public.order_sheets USING btree (document_id);
CREATE INDEX idx_order_sheets_recorded_by ON public.order_sheets USING btree (recorded_by_user_id);
CREATE INDEX idx_shares_document ON public.inter_department_shares USING btree (document_id);
CREATE INDEX idx_shares_expiry ON public.inter_department_shares USING btree (expires_at);
CREATE INDEX idx_shares_source_department ON public.inter_department_shares USING btree (source_department_id);
CREATE INDEX idx_shares_target_department ON public.inter_department_shares USING btree (target_department_id, status);
CREATE INDEX idx_signatures_document_version ON public.digital_signatures USING btree (document_version_id);
CREATE INDEX idx_signatures_signed_at ON public.digital_signatures USING btree (signed_at DESC);
CREATE INDEX idx_signatures_signer ON public.digital_signatures USING btree (signer_id);
CREATE INDEX idx_user_departments_department_id ON public.user_departments USING btree (department_id);
CREATE INDEX idx_user_departments_role_id ON public.user_departments USING btree (role_id);
CREATE INDEX idx_user_departments_user_id ON public.user_departments USING btree (user_id);
CREATE INDEX idx_warrants_case ON public.warrants_and_summons USING btree (case_id);
CREATE INDEX idx_warrants_officer ON public.warrants_and_summons USING btree (executing_officer_id);
CREATE INDEX idx_warrants_order ON public.warrants_and_summons USING btree (court_order_id);
CREATE INDEX idx_warrants_police_station ON public.warrants_and_summons USING btree (assigned_police_station_id);
CREATE INDEX idx_warrants_return_date ON public.warrants_and_summons USING btree (return_date);
CREATE INDEX idx_warrants_status ON public.warrants_and_summons USING btree (execution_status);
ALTER TABLE ONLY public.case_stage_history
    ADD CONSTRAINT case_stage_history_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);
ALTER TABLE ONLY public.case_stage_history
    ADD CONSTRAINT case_stage_history_changed_by_order_id_fkey FOREIGN KEY (changed_by_order_id) REFERENCES public.court_orders(id);
ALTER TABLE ONLY public.case_stage_history
    ADD CONSTRAINT case_stage_history_changed_by_user_id_fkey FOREIGN KEY (changed_by_user_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.cases
    ADD CONSTRAINT cases_lead_investigator_id_fkey FOREIGN KEY (lead_investigator_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.cases
    ADD CONSTRAINT cases_primary_department_id_fkey FOREIGN KEY (primary_department_id) REFERENCES public.departments(id);
ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT chain_of_custody_logs_actor_department_id_fkey FOREIGN KEY (actor_department_id) REFERENCES public.departments(id);
ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT chain_of_custody_logs_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT chain_of_custody_logs_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);
ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT chain_of_custody_logs_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id);
ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT chain_of_custody_logs_evidence_id_fkey FOREIGN KEY (evidence_id) REFERENCES public.evidence_items(id);
ALTER TABLE ONLY public.court_benches
    ADD CONSTRAINT court_benches_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);
ALTER TABLE ONLY public.court_benches
    ADD CONSTRAINT court_benches_presiding_judge_id_fkey FOREIGN KEY (presiding_judge_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.court_hearings
    ADD CONSTRAINT court_hearings_bench_id_fkey FOREIGN KEY (bench_id) REFERENCES public.court_benches(id);
ALTER TABLE ONLY public.court_hearings
    ADD CONSTRAINT court_hearings_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);
ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);
ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id);
ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_hearing_id_fkey FOREIGN KEY (hearing_id) REFERENCES public.court_hearings(id);
ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_issuing_judge_id_fkey FOREIGN KEY (issuing_judge_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.departments(id);
ALTER TABLE ONLY public.digital_signatures
    ADD CONSTRAINT digital_signatures_document_version_id_fkey FOREIGN KEY (document_version_id) REFERENCES public.document_versions(id);
ALTER TABLE ONLY public.digital_signatures
    ADD CONSTRAINT digital_signatures_signer_department_id_fkey FOREIGN KEY (signer_department_id) REFERENCES public.departments(id);
ALTER TABLE ONLY public.digital_signatures
    ADD CONSTRAINT digital_signatures_signer_id_fkey FOREIGN KEY (signer_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.document_ai_metadata
    ADD CONSTRAINT document_ai_metadata_version_id_fkey FOREIGN KEY (version_id) REFERENCES public.document_versions(id);
ALTER TABLE ONLY public.document_versions
    ADD CONSTRAINT document_versions_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id);
ALTER TABLE ONLY public.document_versions
    ADD CONSTRAINT document_versions_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);
ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);
ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);
ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_evidence_item_id_fkey FOREIGN KEY (evidence_item_id) REFERENCES public.evidence_items(id);
ALTER TABLE ONLY public.evidence_custody_transfers
    ADD CONSTRAINT evidence_custody_transfers_evidence_item_id_fkey FOREIGN KEY (evidence_item_id) REFERENCES public.evidence_items(id);
ALTER TABLE ONLY public.evidence_custody_transfers
    ADD CONSTRAINT evidence_custody_transfers_received_by_user_id_fkey FOREIGN KEY (received_by_user_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.evidence_custody_transfers
    ADD CONSTRAINT evidence_custody_transfers_released_by_user_id_fkey FOREIGN KEY (released_by_user_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.evidence_items
    ADD CONSTRAINT evidence_items_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);
ALTER TABLE ONLY public.evidence_items
    ADD CONSTRAINT evidence_items_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.evidence_providers(id);
ALTER TABLE ONLY public.evidence_items
    ADD CONSTRAINT evidence_items_seized_by_user_id_fkey FOREIGN KEY (seized_by_user_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.inter_department_shares
    ADD CONSTRAINT inter_department_shares_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id);
ALTER TABLE ONLY public.inter_department_shares
    ADD CONSTRAINT inter_department_shares_granted_by_user_id_fkey FOREIGN KEY (granted_by_user_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.inter_department_shares
    ADD CONSTRAINT inter_department_shares_source_department_id_fkey FOREIGN KEY (source_department_id) REFERENCES public.departments(id);
ALTER TABLE ONLY public.inter_department_shares
    ADD CONSTRAINT inter_department_shares_target_department_id_fkey FOREIGN KEY (target_department_id) REFERENCES public.departments(id);
ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);
ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id);
ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_hearing_id_fkey FOREIGN KEY (hearing_id) REFERENCES public.court_hearings(id);
ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_recorded_by_user_id_fkey FOREIGN KEY (recorded_by_user_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.user_departments
    ADD CONSTRAINT user_departments_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);
ALTER TABLE ONLY public.user_departments
    ADD CONSTRAINT user_departments_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);
ALTER TABLE ONLY public.user_departments
    ADD CONSTRAINT user_departments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.warrants_and_summons
    ADD CONSTRAINT warrants_and_summons_assigned_police_station_id_fkey FOREIGN KEY (assigned_police_station_id) REFERENCES public.departments(id);
ALTER TABLE ONLY public.warrants_and_summons
    ADD CONSTRAINT warrants_and_summons_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);
ALTER TABLE ONLY public.warrants_and_summons
    ADD CONSTRAINT warrants_and_summons_court_order_id_fkey FOREIGN KEY (court_order_id) REFERENCES public.court_orders(id);
ALTER TABLE ONLY public.warrants_and_summons
    ADD CONSTRAINT warrants_and_summons_executing_officer_id_fkey FOREIGN KEY (executing_officer_id) REFERENCES public.users(id);
CREATE TABLE IF NOT EXISTS public.revoked_tokens (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    token_jti character varying NOT NULL UNIQUE,
    revoked_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp with time zone NOT NULL
);
CREATE INDEX idx_revoked_tokens_jti ON public.revoked_tokens(token_jti);
CREATE INDEX idx_revoked_tokens_expires ON public.revoked_tokens(expires_at);
CREATE TABLE public.user_mapping (
    registration_user_id INTEGER NOT NULL,
    operational_user_id UUID NOT NULL REFERENCES public.users(id),
    mapped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (registration_user_id)
);

\unrestrict GJYfOpc0BrHzEke1BOQj1zYgMg2poFMqLHRvNLHd9mRuobZYUuCM5W4LWFgwsbC