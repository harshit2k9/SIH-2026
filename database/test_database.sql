--
-- PostgreSQL database dump
--

\restrict rFka8SUshuBffh8YAsbVcNDBkQiWu705yVamb4dBHEjgfZsIH89dnJtjYVtLTsI

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

-- Started on 2026-09-10 21:27:45

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

--
-- TOC entry 238 (class 1259 OID 33575)
-- Name: case_stage_history; Type: TABLE; Schema: public; Owner: postgres
--

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


ALTER TABLE public.case_stage_history OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 33157)
-- Name: cases; Type: TABLE; Schema: public; Owner: postgres
--

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


ALTER TABLE public.cases OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 33349)
-- Name: chain_of_custody_logs; Type: TABLE; Schema: public; Owner: postgres
--

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


ALTER TABLE public.chain_of_custody_logs OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 33417)
-- Name: court_benches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.court_benches (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    department_id uuid NOT NULL,
    bench_name character varying NOT NULL,
    bench_type character varying NOT NULL,
    presiding_judge_id uuid NOT NULL,
    is_active boolean DEFAULT true
);


ALTER TABLE public.court_benches OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 33441)
-- Name: court_hearings; Type: TABLE; Schema: public; Owner: postgres
--

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


ALTER TABLE public.court_hearings OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 33503)
-- Name: court_orders; Type: TABLE; Schema: public; Owner: postgres
--

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


ALTER TABLE public.court_orders OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 33067)
-- Name: departments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.departments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying NOT NULL,
    code character varying NOT NULL,
    parent_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.departments OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 33388)
-- Name: digital_signatures; Type: TABLE; Schema: public; Owner: postgres
--

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


ALTER TABLE public.digital_signatures OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 33297)
-- Name: document_ai_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.document_ai_metadata (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    version_id uuid NOT NULL,
    ocr_extracted_text text,
    ai_summary text,
    extracted_entities jsonb,
    vector_embedding_id character varying,
    processed_at timestamp with time zone
);


ALTER TABLE public.document_ai_metadata OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 33272)
-- Name: document_versions; Type: TABLE; Schema: public; Owner: postgres
--

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


ALTER TABLE public.document_versions OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 33240)
-- Name: documents; Type: TABLE; Schema: public; Owner: postgres
--

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


ALTER TABLE public.documents OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 33214)
-- Name: evidence_custody_transfers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.evidence_custody_transfers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    evidence_item_id uuid NOT NULL,
    released_by_user_id uuid,
    received_by_user_id uuid,
    purpose text,
    transfer_timestamp timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    physical_condition_notes text
);


ALTER TABLE public.evidence_custody_transfers OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 33183)
-- Name: evidence_items; Type: TABLE; Schema: public; Owner: postgres
--

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


ALTER TABLE public.evidence_items OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 33144)
-- Name: evidence_providers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.evidence_providers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    provider_type character varying NOT NULL,
    full_name_or_org character varying NOT NULL,
    contact_info jsonb,
    identification_number character varying,
    clearance_verified boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.evidence_providers OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 33314)
-- Name: inter_department_shares; Type: TABLE; Schema: public; Owner: postgres
--

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


ALTER TABLE public.inter_department_shares OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 33466)
-- Name: order_sheets; Type: TABLE; Schema: public; Owner: postgres
--

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


ALTER TABLE public.order_sheets OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 33103)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying NOT NULL,
    permissions jsonb
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 33115)
-- Name: user_departments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_departments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    department_id uuid NOT NULL,
    role_id uuid NOT NULL,
    is_primary boolean DEFAULT false,
    assigned_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_departments OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 33086)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    full_name character varying NOT NULL,
    email character varying NOT NULL,
    badge_number character varying,
    security_clearance_level integer,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 33541)
-- Name: warrants_and_summons; Type: TABLE; Schema: public; Owner: postgres
--

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


ALTER TABLE public.warrants_and_summons OWNER TO postgres;

--
-- TOC entry 5210 (class 0 OID 33575)
-- Dependencies: 238
-- Data for Name: case_stage_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.case_stage_history (id, case_id, previous_stage, new_stage, changed_by_order_id, changed_by_user_id, remarks, changed_at) FROM stdin;
9982993f-bd33-4880-8e3f-260d3205755e	ac4fbec5-f9b5-4280-9994-a55619ca10e2	INVESTIGATION	COURT_PROCEEDINGS	80344309-06b8-484f-bd17-0d844221c05f	526f939d-6703-4aa5-a8be-e3c23dfe2012	Case moved to court proceedings for prototype testing.	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5196 (class 0 OID 33157)
-- Dependencies: 224
-- Data for Name: cases; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cases (id, case_number, title, description, classification_level, status, primary_department_id, lead_investigator_id, created_at) FROM stdin;
ac4fbec5-f9b5-4280-9994-a55619ca10e2	FIR-2026-0001	Cyber Fraud Investigation	Dummy development case for testing the document management workflow.	3	ACTIVE	22f22eef-a32d-4c50-9a21-43d8087aeaa7	f470d6be-4067-4ed0-862f-51c1eda2054f	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5203 (class 0 OID 33349)
-- Dependencies: 231
-- Data for Name: chain_of_custody_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chain_of_custody_logs (id, case_id, document_id, evidence_id, actor_id, actor_department_id, action, ip_address, user_agent, previous_log_hash, current_log_hash, created_at) FROM stdin;
2f60863e-17ba-49a6-8bef-1aa08c31350c	ac4fbec5-f9b5-4280-9994-a55619ca10e2	e2eb040e-5aae-4446-be27-e858583ec719	6d223e75-42ac-48f5-8e0f-1cfa15d32be9	f470d6be-4067-4ed0-862f-51c1eda2054f	22f22eef-a32d-4c50-9a21-43d8087aeaa7	DOCUMENT_UPLOADED	127.0.0.1	Prototype Browser	\N	demo-current-log-hash-001	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5205 (class 0 OID 33417)
-- Dependencies: 233
-- Data for Name: court_benches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.court_benches (id, department_id, bench_name, bench_type, presiding_judge_id, is_active) FROM stdin;
ab9c31b4-c640-4a84-bba2-747408fc31ad	021d1e9c-56eb-4c26-8ab9-9d6180a14fa6	Cyber Crime Bench	DISTRICT_COURT	526f939d-6703-4aa5-a8be-e3c23dfe2012	t
\.


--
-- TOC entry 5206 (class 0 OID 33441)
-- Dependencies: 234
-- Data for Name: court_hearings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.court_hearings (id, case_id, bench_id, hearing_date, hearing_purpose, status, adjournment_reason, next_hearing_date, created_at) FROM stdin;
8d3d7988-59cd-4a54-af2f-b6256a7ede5c	ac4fbec5-f9b5-4280-9994-a55619ca10e2	ab9c31b4-c640-4a84-bba2-747408fc31ad	2026-09-15 22:42:45.205986+05:30	Initial hearing	SCHEDULED	\N	2026-10-08 22:42:45.205986+05:30	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5208 (class 0 OID 33503)
-- Dependencies: 236
-- Data for Name: court_orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.court_orders (id, case_id, hearing_id, order_number, order_type, order_summary, issuing_judge_id, document_id, effective_date, expiry_date, enforcement_status, created_at) FROM stdin;
80344309-06b8-484f-bd17-0d844221c05f	ac4fbec5-f9b5-4280-9994-a55619ca10e2	8d3d7988-59cd-4a54-af2f-b6256a7ede5c	ORDER-2026-0001	DIRECTION	Dummy court order for prototype testing.	526f939d-6703-4aa5-a8be-e3c23dfe2012	4343595b-54a3-4745-bcff-ba5289a326f1	2026-09-08 22:42:45.205986+05:30	\N	PENDING	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5191 (class 0 OID 33067)
-- Dependencies: 219
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.departments (id, name, code, parent_id, created_at) FROM stdin;
22f22eef-a32d-4c50-9a21-43d8087aeaa7	Cyber Crime Investigation Unit	CCIU	\N	2026-09-08 22:42:45.205986+05:30
021d1e9c-56eb-4c26-8ab9-9d6180a14fa6	District Court	COURT	\N	2026-09-08 22:42:45.205986+05:30
8ae16499-1d83-4b08-b16c-f0156e31a435	Central Police Station	CPS	\N	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5204 (class 0 OID 33388)
-- Dependencies: 232
-- Data for Name: digital_signatures; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.digital_signatures (id, document_version_id, signer_id, signer_department_id, signature_hash, cert_serial_number, timestamp_seal, signed_at) FROM stdin;
dbf6d660-740d-45ab-9834-2a16da4fd37e	b057e28d-5e61-43a8-9735-eec7eb9ff045	526f939d-6703-4aa5-a8be-e3c23dfe2012	021d1e9c-56eb-4c26-8ab9-9d6180a14fa6	demo-signature-hash-001	CERT-DEMO-001	DEMO-TIMESTAMP-SEAL	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5201 (class 0 OID 33297)
-- Dependencies: 229
-- Data for Name: document_ai_metadata; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.document_ai_metadata (id, version_id, ocr_extracted_text, ai_summary, extracted_entities, vector_embedding_id, processed_at) FROM stdin;
a6283c0e-3963-4f14-8f1b-2e2b4fdb3ed1	af611d22-7be5-4fb1-bcf1-4c2fbbc58d64	Dummy OCR extracted text for development testing.	Dummy AI summary of the investigation document.	{"case_number": "FIR-2026-0001", "document_type": "INVESTIGATION_REPORT"}	embedding-demo-001	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5200 (class 0 OID 33272)
-- Dependencies: 228
-- Data for Name: document_versions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.document_versions (id, document_id, version_number, storage_uri, file_size_bytes, file_mime_type, sha256_checksum, kms_key_id, uploaded_by, uploaded_at) FROM stdin;
af611d22-7be5-4fb1-bcf1-4c2fbbc58d64	e2eb040e-5aae-4446-be27-e858583ec719	1	minio://legal-documents/DOC-2026-0001/v1.pdf	245760	application/pdf	dummy-sha256-checksum-document-0001	kms-key-demo-001	f470d6be-4067-4ed0-862f-51c1eda2054f	2026-09-08 22:42:45.205986+05:30
b057e28d-5e61-43a8-9735-eec7eb9ff045	4343595b-54a3-4745-bcff-ba5289a326f1	1	minio://legal-documents/DOC-2026-0002/v1.pdf	128000	application/pdf	dummy-sha256-checksum-document-0002	kms-key-demo-002	526f939d-6703-4aa5-a8be-e3c23dfe2012	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5199 (class 0 OID 33240)
-- Dependencies: 227
-- Data for Name: documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.documents (id, case_id, evidence_item_id, document_number, title, document_type, confidentiality_level, current_version, created_by, created_at, is_locked) FROM stdin;
e2eb040e-5aae-4446-be27-e858583ec719	ac4fbec5-f9b5-4280-9994-a55619ca10e2	6d223e75-42ac-48f5-8e0f-1cfa15d32be9	DOC-2026-0001	Investigation Report	INVESTIGATION_REPORT	4	1	f470d6be-4067-4ed0-862f-51c1eda2054f	2026-09-08 22:42:45.205986+05:30	f
4343595b-54a3-4745-bcff-ba5289a326f1	ac4fbec5-f9b5-4280-9994-a55619ca10e2	\N	DOC-2026-0002	Court Order Document	COURT_ORDER	5	1	526f939d-6703-4aa5-a8be-e3c23dfe2012	2026-09-08 22:42:45.205986+05:30	f
\.


--
-- TOC entry 5198 (class 0 OID 33214)
-- Dependencies: 226
-- Data for Name: evidence_custody_transfers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.evidence_custody_transfers (id, evidence_item_id, released_by_user_id, received_by_user_id, purpose, transfer_timestamp, physical_condition_notes) FROM stdin;
f63e8e26-d48e-4e08-927e-d2363c3ab838	6d223e75-42ac-48f5-8e0f-1cfa15d32be9	a9e89d4d-ac46-4833-a5af-7efa278feda1	f470d6be-4067-4ed0-862f-51c1eda2054f	Transfer for forensic examination	2026-09-08 22:42:45.205986+05:30	Device received in sealed condition.
\.


--
-- TOC entry 5197 (class 0 OID 33183)
-- Dependencies: 225
-- Data for Name: evidence_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.evidence_items (id, case_id, evidence_number, provider_id, title, evidence_type, storage_location, current_status, seized_at, seized_by_user_id) FROM stdin;
6d223e75-42ac-48f5-8e0f-1cfa15d32be9	ac4fbec5-f9b5-4280-9994-a55619ca10e2	EVD-2026-0001	3f0d1c24-2e81-4d26-9cd3-04aa8d981f2c	Laptop used in investigation	DIGITAL_DEVICE	Secure Evidence Locker A-01	IN_CUSTODY	2026-09-08 22:42:45.205986+05:30	a9e89d4d-ac46-4833-a5af-7efa278feda1
\.


--
-- TOC entry 5195 (class 0 OID 33144)
-- Dependencies: 223
-- Data for Name: evidence_providers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.evidence_providers (id, provider_type, full_name_or_org, contact_info, identification_number, clearance_verified, created_at) FROM stdin;
3f0d1c24-2e81-4d26-9cd3-04aa8d981f2c	POLICE	Central Police Station	{"phone": "+91-9000000000"}	CPS-001	t	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5202 (class 0 OID 33314)
-- Dependencies: 230
-- Data for Name: inter_department_shares; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inter_department_shares (id, document_id, source_department_id, target_department_id, granted_by_user_id, access_level, reason, valid_from, expires_at, status) FROM stdin;
c92e0899-1df9-4c86-98ee-92d82695a70c	e2eb040e-5aae-4446-be27-e858583ec719	22f22eef-a32d-4c50-9a21-43d8087aeaa7	021d1e9c-56eb-4c26-8ab9-9d6180a14fa6	f470d6be-4067-4ed0-862f-51c1eda2054f	view	Required for court review.	2026-09-08 22:42:45.205986+05:30	2026-10-08 22:42:45.205986+05:30	active
\.


--
-- TOC entry 5207 (class 0 OID 33466)
-- Dependencies: 235
-- Data for Name: order_sheets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_sheets (id, case_id, hearing_id, order_sheet_number, proceeding_summary, advocates_present, accused_presence_status, document_id, recorded_by_user_id, created_at) FROM stdin;
c60aa8df-7ee5-454f-85d0-1709aa162514	ac4fbec5-f9b5-4280-9994-a55619ca10e2	8d3d7988-59cd-4a54-af2f-b6256a7ede5c	OS-2026-0001	Initial hearing proceedings recorded for development testing.	{"defence": "Present", "prosecution": "Present"}	PRESENT	4343595b-54a3-4745-bcff-ba5289a326f1	526f939d-6703-4aa5-a8be-e3c23dfe2012	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5193 (class 0 OID 33103)
-- Dependencies: 221
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name, permissions) FROM stdin;
8b9f33a8-31f7-40e1-a62c-4784326f201f	INVESTIGATOR	{"case": {"edit": true, "view": true, "share": true, "delete": true}, "document": {"edit": true, "view": true, "share": true, "upload": true}}
a412945c-eead-4329-8903-66c6043f4551	JUDGE	{"case": {"edit": false, "view": true, "share": false, "delete": false}, "document": {"edit": false, "view": true, "share": false, "upload": false}}
a9f95862-4959-408a-8562-c61085022bde	OFFICER	{"case": {"edit": true, "view": true, "share": false, "delete": false}, "document": {"edit": true, "view": true, "share": false, "upload": true}}
\.


--
-- TOC entry 5194 (class 0 OID 33115)
-- Dependencies: 222
-- Data for Name: user_departments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_departments (id, user_id, department_id, role_id, is_primary, assigned_at) FROM stdin;
14c25538-7f2b-4a82-867d-aac48a11888a	f470d6be-4067-4ed0-862f-51c1eda2054f	22f22eef-a32d-4c50-9a21-43d8087aeaa7	8b9f33a8-31f7-40e1-a62c-4784326f201f	t	2026-09-08 22:42:45.205986+05:30
caff2fea-137b-42e1-b109-6904de556d7e	526f939d-6703-4aa5-a8be-e3c23dfe2012	021d1e9c-56eb-4c26-8ab9-9d6180a14fa6	a412945c-eead-4329-8903-66c6043f4551	t	2026-09-08 22:42:45.205986+05:30
9bc2376b-913d-4bb7-8747-0c28685ce78d	a9e89d4d-ac46-4833-a5af-7efa278feda1	8ae16499-1d83-4b08-b16c-f0156e31a435	a9f95862-4959-408a-8562-c61085022bde	t	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5192 (class 0 OID 33086)
-- Dependencies: 220
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, full_name, email, badge_number, security_clearance_level, is_active, created_at) FROM stdin;
f470d6be-4067-4ed0-862f-51c1eda2054f	Aarav Sharma	aarav.investigator@example.com	BADGE-1001	4	t	2026-09-08 22:42:45.205986+05:30
526f939d-6703-4aa5-a8be-e3c23dfe2012	Priya Mehta	priya.judge@example.com	BADGE-2001	5	t	2026-09-08 22:42:45.205986+05:30
a9e89d4d-ac46-4833-a5af-7efa278feda1	Rohan Verma	rohan.officer@example.com	BADGE-3001	3	t	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 5209 (class 0 OID 33541)
-- Dependencies: 237
-- Data for Name: warrants_and_summons; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warrants_and_summons (id, court_order_id, case_id, notice_type, target_person_details, assigned_police_station_id, executing_officer_id, execution_status, return_date, created_at) FROM stdin;
c4e120a0-fb25-4a0e-8c3d-52de466700eb	80344309-06b8-484f-bd17-0d844221c05f	ac4fbec5-f9b5-4280-9994-a55619ca10e2	SUMMONS	{"name": "Demo Respondent", "address": "Demo Address"}	8ae16499-1d83-4b08-b16c-f0156e31a435	a9e89d4d-ac46-4833-a5af-7efa278feda1	PENDING	2026-09-23 22:42:45.205986+05:30	2026-09-08 22:42:45.205986+05:30
\.


--
-- TOC entry 4990 (class 2606 OID 33587)
-- Name: case_stage_history case_stage_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_stage_history
    ADD CONSTRAINT case_stage_history_pkey PRIMARY KEY (id);


--
-- TOC entry 4895 (class 2606 OID 33172)
-- Name: cases cases_case_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cases
    ADD CONSTRAINT cases_case_number_key UNIQUE (case_number);


--
-- TOC entry 4897 (class 2606 OID 33170)
-- Name: cases cases_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cases
    ADD CONSTRAINT cases_pkey PRIMARY KEY (id);


--
-- TOC entry 4941 (class 2606 OID 33362)
-- Name: chain_of_custody_logs chain_of_custody_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT chain_of_custody_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4952 (class 2606 OID 33430)
-- Name: court_benches court_benches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_benches
    ADD CONSTRAINT court_benches_pkey PRIMARY KEY (id);


--
-- TOC entry 4957 (class 2606 OID 33455)
-- Name: court_hearings court_hearings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_hearings
    ADD CONSTRAINT court_hearings_pkey PRIMARY KEY (id);


--
-- TOC entry 4972 (class 2606 OID 33520)
-- Name: court_orders court_orders_document_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_document_id_key UNIQUE (document_id);


--
-- TOC entry 4974 (class 2606 OID 33518)
-- Name: court_orders court_orders_order_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_order_number_key UNIQUE (order_number);


--
-- TOC entry 4976 (class 2606 OID 33516)
-- Name: court_orders court_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_pkey PRIMARY KEY (id);


--
-- TOC entry 4871 (class 2606 OID 33080)
-- Name: departments departments_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_code_key UNIQUE (code);


--
-- TOC entry 4873 (class 2606 OID 33078)
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- TOC entry 4947 (class 2606 OID 33401)
-- Name: digital_signatures digital_signatures_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_signatures
    ADD CONSTRAINT digital_signatures_pkey PRIMARY KEY (id);


--
-- TOC entry 4930 (class 2606 OID 33306)
-- Name: document_ai_metadata document_ai_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_ai_metadata
    ADD CONSTRAINT document_ai_metadata_pkey PRIMARY KEY (id);


--
-- TOC entry 4932 (class 2606 OID 33308)
-- Name: document_ai_metadata document_ai_metadata_version_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_ai_metadata
    ADD CONSTRAINT document_ai_metadata_version_id_key UNIQUE (version_id);


--
-- TOC entry 4923 (class 2606 OID 33286)
-- Name: document_versions document_versions_document_id_version_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_versions
    ADD CONSTRAINT document_versions_document_id_version_number_key UNIQUE (document_id, version_number);


--
-- TOC entry 4925 (class 2606 OID 33284)
-- Name: document_versions document_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_versions
    ADD CONSTRAINT document_versions_pkey PRIMARY KEY (id);


--
-- TOC entry 4914 (class 2606 OID 33256)
-- Name: documents documents_document_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_document_number_key UNIQUE (document_number);


--
-- TOC entry 4916 (class 2606 OID 33254)
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- TOC entry 4911 (class 2606 OID 33224)
-- Name: evidence_custody_transfers evidence_custody_transfers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_custody_transfers
    ADD CONSTRAINT evidence_custody_transfers_pkey PRIMARY KEY (id);


--
-- TOC entry 4903 (class 2606 OID 33198)
-- Name: evidence_items evidence_items_evidence_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_items
    ADD CONSTRAINT evidence_items_evidence_number_key UNIQUE (evidence_number);


--
-- TOC entry 4905 (class 2606 OID 33196)
-- Name: evidence_items evidence_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_items
    ADD CONSTRAINT evidence_items_pkey PRIMARY KEY (id);


--
-- TOC entry 4893 (class 2606 OID 33156)
-- Name: evidence_providers evidence_providers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_providers
    ADD CONSTRAINT evidence_providers_pkey PRIMARY KEY (id);


--
-- TOC entry 4939 (class 2606 OID 33328)
-- Name: inter_department_shares inter_department_shares_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inter_department_shares
    ADD CONSTRAINT inter_department_shares_pkey PRIMARY KEY (id);


--
-- TOC entry 4966 (class 2606 OID 33480)
-- Name: order_sheets order_sheets_hearing_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_hearing_id_key UNIQUE (hearing_id);


--
-- TOC entry 4968 (class 2606 OID 33482)
-- Name: order_sheets order_sheets_order_sheet_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_order_sheet_number_key UNIQUE (order_sheet_number);


--
-- TOC entry 4970 (class 2606 OID 33478)
-- Name: order_sheets order_sheets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_pkey PRIMARY KEY (id);


--
-- TOC entry 4882 (class 2606 OID 33114)
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- TOC entry 4884 (class 2606 OID 33112)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- TOC entry 4889 (class 2606 OID 33126)
-- Name: user_departments user_departments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_departments
    ADD CONSTRAINT user_departments_pkey PRIMARY KEY (id);


--
-- TOC entry 4891 (class 2606 OID 33128)
-- Name: user_departments user_departments_user_id_department_id_role_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_departments
    ADD CONSTRAINT user_departments_user_id_department_id_role_id_key UNIQUE (user_id, department_id, role_id);


--
-- TOC entry 4876 (class 2606 OID 33102)
-- Name: users users_badge_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_badge_number_key UNIQUE (badge_number);


--
-- TOC entry 4878 (class 2606 OID 33100)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4880 (class 2606 OID 33098)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4988 (class 2606 OID 33554)
-- Name: warrants_and_summons warrants_and_summons_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warrants_and_summons
    ADD CONSTRAINT warrants_and_summons_pkey PRIMARY KEY (id);


--
-- TOC entry 4991 (class 1259 OID 33657)
-- Name: idx_case_stage_history_case; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_case_stage_history_case ON public.case_stage_history USING btree (case_id, changed_at DESC);


--
-- TOC entry 4992 (class 1259 OID 33658)
-- Name: idx_case_stage_history_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_case_stage_history_order ON public.case_stage_history USING btree (changed_by_order_id);


--
-- TOC entry 4993 (class 1259 OID 33660)
-- Name: idx_case_stage_history_stage; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_case_stage_history_stage ON public.case_stage_history USING btree (new_stage);


--
-- TOC entry 4994 (class 1259 OID 33659)
-- Name: idx_case_stage_history_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_case_stage_history_user ON public.case_stage_history USING btree (changed_by_user_id);


--
-- TOC entry 4898 (class 1259 OID 33611)
-- Name: idx_cases_classification; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cases_classification ON public.cases USING btree (classification_level);


--
-- TOC entry 4899 (class 1259 OID 33608)
-- Name: idx_cases_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cases_department ON public.cases USING btree (primary_department_id);


--
-- TOC entry 4900 (class 1259 OID 33609)
-- Name: idx_cases_lead_investigator; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cases_lead_investigator ON public.cases USING btree (lead_investigator_id);


--
-- TOC entry 4901 (class 1259 OID 33610)
-- Name: idx_cases_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cases_status ON public.cases USING btree (status);


--
-- TOC entry 4953 (class 1259 OID 33639)
-- Name: idx_court_benches_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_court_benches_active ON public.court_benches USING btree (is_active);


--
-- TOC entry 4954 (class 1259 OID 33637)
-- Name: idx_court_benches_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_court_benches_department ON public.court_benches USING btree (department_id);


--
-- TOC entry 4955 (class 1259 OID 33638)
-- Name: idx_court_benches_judge; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_court_benches_judge ON public.court_benches USING btree (presiding_judge_id);


--
-- TOC entry 4958 (class 1259 OID 33641)
-- Name: idx_court_hearings_bench; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_court_hearings_bench ON public.court_hearings USING btree (bench_id, hearing_date);


--
-- TOC entry 4959 (class 1259 OID 33640)
-- Name: idx_court_hearings_case; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_court_hearings_case ON public.court_hearings USING btree (case_id, hearing_date DESC);


--
-- TOC entry 4960 (class 1259 OID 33643)
-- Name: idx_court_hearings_next_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_court_hearings_next_date ON public.court_hearings USING btree (next_hearing_date);


--
-- TOC entry 4961 (class 1259 OID 33642)
-- Name: idx_court_hearings_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_court_hearings_status ON public.court_hearings USING btree (status);


--
-- TOC entry 4977 (class 1259 OID 33647)
-- Name: idx_court_orders_case; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_court_orders_case ON public.court_orders USING btree (case_id, created_at DESC);


--
-- TOC entry 4978 (class 1259 OID 33650)
-- Name: idx_court_orders_enforcement; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_court_orders_enforcement ON public.court_orders USING btree (enforcement_status);


--
-- TOC entry 4979 (class 1259 OID 33648)
-- Name: idx_court_orders_hearing; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_court_orders_hearing ON public.court_orders USING btree (hearing_id);


--
-- TOC entry 4980 (class 1259 OID 33649)
-- Name: idx_court_orders_judge; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_court_orders_judge ON public.court_orders USING btree (issuing_judge_id);


--
-- TOC entry 4942 (class 1259 OID 33633)
-- Name: idx_custody_logs_actor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_custody_logs_actor ON public.chain_of_custody_logs USING btree (actor_id, created_at DESC);


--
-- TOC entry 4943 (class 1259 OID 33630)
-- Name: idx_custody_logs_case; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_custody_logs_case ON public.chain_of_custody_logs USING btree (case_id, created_at DESC);


--
-- TOC entry 4944 (class 1259 OID 33631)
-- Name: idx_custody_logs_document; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_custody_logs_document ON public.chain_of_custody_logs USING btree (document_id, created_at DESC);


--
-- TOC entry 4945 (class 1259 OID 33632)
-- Name: idx_custody_logs_evidence; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_custody_logs_evidence ON public.chain_of_custody_logs USING btree (evidence_id, created_at DESC);


--
-- TOC entry 4912 (class 1259 OID 33616)
-- Name: idx_custody_transfers_evidence; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_custody_transfers_evidence ON public.evidence_custody_transfers USING btree (evidence_item_id, transfer_timestamp DESC);


--
-- TOC entry 4874 (class 1259 OID 33604)
-- Name: idx_departments_parent_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_departments_parent_id ON public.departments USING btree (parent_id);


--
-- TOC entry 4933 (class 1259 OID 33625)
-- Name: idx_document_ai_metadata_embedding; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_document_ai_metadata_embedding ON public.document_ai_metadata USING btree (vector_embedding_id);


--
-- TOC entry 4926 (class 1259 OID 33624)
-- Name: idx_document_versions_checksum; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_document_versions_checksum ON public.document_versions USING btree (sha256_checksum);


--
-- TOC entry 4927 (class 1259 OID 33622)
-- Name: idx_document_versions_document; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_document_versions_document ON public.document_versions USING btree (document_id, version_number DESC);


--
-- TOC entry 4928 (class 1259 OID 33623)
-- Name: idx_document_versions_uploaded_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_document_versions_uploaded_by ON public.document_versions USING btree (uploaded_by);


--
-- TOC entry 4917 (class 1259 OID 33617)
-- Name: idx_documents_case; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_documents_case ON public.documents USING btree (case_id);


--
-- TOC entry 4918 (class 1259 OID 33620)
-- Name: idx_documents_created_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_documents_created_by ON public.documents USING btree (created_by);


--
-- TOC entry 4919 (class 1259 OID 33618)
-- Name: idx_documents_evidence; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_documents_evidence ON public.documents USING btree (evidence_item_id);


--
-- TOC entry 4920 (class 1259 OID 33621)
-- Name: idx_documents_locked; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_documents_locked ON public.documents USING btree (is_locked);


--
-- TOC entry 4921 (class 1259 OID 33619)
-- Name: idx_documents_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_documents_type ON public.documents USING btree (document_type);


--
-- TOC entry 4906 (class 1259 OID 33612)
-- Name: idx_evidence_items_case; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_evidence_items_case ON public.evidence_items USING btree (case_id);


--
-- TOC entry 4907 (class 1259 OID 33613)
-- Name: idx_evidence_items_provider; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_evidence_items_provider ON public.evidence_items USING btree (provider_id);


--
-- TOC entry 4908 (class 1259 OID 33615)
-- Name: idx_evidence_items_seized_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_evidence_items_seized_by ON public.evidence_items USING btree (seized_by_user_id);


--
-- TOC entry 4909 (class 1259 OID 33614)
-- Name: idx_evidence_items_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_evidence_items_status ON public.evidence_items USING btree (current_status);


--
-- TOC entry 4962 (class 1259 OID 33644)
-- Name: idx_order_sheets_case; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_order_sheets_case ON public.order_sheets USING btree (case_id);


--
-- TOC entry 4963 (class 1259 OID 33645)
-- Name: idx_order_sheets_document; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_order_sheets_document ON public.order_sheets USING btree (document_id);


--
-- TOC entry 4964 (class 1259 OID 33646)
-- Name: idx_order_sheets_recorded_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_order_sheets_recorded_by ON public.order_sheets USING btree (recorded_by_user_id);


--
-- TOC entry 4934 (class 1259 OID 33626)
-- Name: idx_shares_document; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_shares_document ON public.inter_department_shares USING btree (document_id);


--
-- TOC entry 4935 (class 1259 OID 33629)
-- Name: idx_shares_expiry; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_shares_expiry ON public.inter_department_shares USING btree (expires_at);


--
-- TOC entry 4936 (class 1259 OID 33628)
-- Name: idx_shares_source_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_shares_source_department ON public.inter_department_shares USING btree (source_department_id);


--
-- TOC entry 4937 (class 1259 OID 33627)
-- Name: idx_shares_target_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_shares_target_department ON public.inter_department_shares USING btree (target_department_id, status);


--
-- TOC entry 4948 (class 1259 OID 33634)
-- Name: idx_signatures_document_version; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_signatures_document_version ON public.digital_signatures USING btree (document_version_id);


--
-- TOC entry 4949 (class 1259 OID 33636)
-- Name: idx_signatures_signed_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_signatures_signed_at ON public.digital_signatures USING btree (signed_at DESC);


--
-- TOC entry 4950 (class 1259 OID 33635)
-- Name: idx_signatures_signer; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_signatures_signer ON public.digital_signatures USING btree (signer_id);


--
-- TOC entry 4885 (class 1259 OID 33606)
-- Name: idx_user_departments_department_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_departments_department_id ON public.user_departments USING btree (department_id);


--
-- TOC entry 4886 (class 1259 OID 33607)
-- Name: idx_user_departments_role_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_departments_role_id ON public.user_departments USING btree (role_id);


--
-- TOC entry 4887 (class 1259 OID 33605)
-- Name: idx_user_departments_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_departments_user_id ON public.user_departments USING btree (user_id);


--
-- TOC entry 4981 (class 1259 OID 33652)
-- Name: idx_warrants_case; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_warrants_case ON public.warrants_and_summons USING btree (case_id);


--
-- TOC entry 4982 (class 1259 OID 33654)
-- Name: idx_warrants_officer; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_warrants_officer ON public.warrants_and_summons USING btree (executing_officer_id);


--
-- TOC entry 4983 (class 1259 OID 33651)
-- Name: idx_warrants_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_warrants_order ON public.warrants_and_summons USING btree (court_order_id);


--
-- TOC entry 4984 (class 1259 OID 33653)
-- Name: idx_warrants_police_station; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_warrants_police_station ON public.warrants_and_summons USING btree (assigned_police_station_id);


--
-- TOC entry 4985 (class 1259 OID 33656)
-- Name: idx_warrants_return_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_warrants_return_date ON public.warrants_and_summons USING btree (return_date);


--
-- TOC entry 4986 (class 1259 OID 33655)
-- Name: idx_warrants_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_warrants_status ON public.warrants_and_summons USING btree (execution_status);


--
-- TOC entry 5041 (class 2606 OID 33588)
-- Name: case_stage_history case_stage_history_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_stage_history
    ADD CONSTRAINT case_stage_history_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);


--
-- TOC entry 5042 (class 2606 OID 33593)
-- Name: case_stage_history case_stage_history_changed_by_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_stage_history
    ADD CONSTRAINT case_stage_history_changed_by_order_id_fkey FOREIGN KEY (changed_by_order_id) REFERENCES public.court_orders(id);


--
-- TOC entry 5043 (class 2606 OID 33598)
-- Name: case_stage_history case_stage_history_changed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_stage_history
    ADD CONSTRAINT case_stage_history_changed_by_user_id_fkey FOREIGN KEY (changed_by_user_id) REFERENCES public.users(id);


--
-- TOC entry 4999 (class 2606 OID 33178)
-- Name: cases cases_lead_investigator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cases
    ADD CONSTRAINT cases_lead_investigator_id_fkey FOREIGN KEY (lead_investigator_id) REFERENCES public.users(id);


--
-- TOC entry 5000 (class 2606 OID 33173)
-- Name: cases cases_primary_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cases
    ADD CONSTRAINT cases_primary_department_id_fkey FOREIGN KEY (primary_department_id) REFERENCES public.departments(id);


--
-- TOC entry 5017 (class 2606 OID 33383)
-- Name: chain_of_custody_logs chain_of_custody_logs_actor_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT chain_of_custody_logs_actor_department_id_fkey FOREIGN KEY (actor_department_id) REFERENCES public.departments(id);


--
-- TOC entry 5018 (class 2606 OID 33378)
-- Name: chain_of_custody_logs chain_of_custody_logs_actor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT chain_of_custody_logs_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.users(id);


--
-- TOC entry 5019 (class 2606 OID 33363)
-- Name: chain_of_custody_logs chain_of_custody_logs_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT chain_of_custody_logs_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);


--
-- TOC entry 5020 (class 2606 OID 33368)
-- Name: chain_of_custody_logs chain_of_custody_logs_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT chain_of_custody_logs_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id);


--
-- TOC entry 5021 (class 2606 OID 33373)
-- Name: chain_of_custody_logs chain_of_custody_logs_evidence_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT chain_of_custody_logs_evidence_id_fkey FOREIGN KEY (evidence_id) REFERENCES public.evidence_items(id);


--
-- TOC entry 5025 (class 2606 OID 33431)
-- Name: court_benches court_benches_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_benches
    ADD CONSTRAINT court_benches_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- TOC entry 5026 (class 2606 OID 33436)
-- Name: court_benches court_benches_presiding_judge_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_benches
    ADD CONSTRAINT court_benches_presiding_judge_id_fkey FOREIGN KEY (presiding_judge_id) REFERENCES public.users(id);


--
-- TOC entry 5027 (class 2606 OID 33461)
-- Name: court_hearings court_hearings_bench_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_hearings
    ADD CONSTRAINT court_hearings_bench_id_fkey FOREIGN KEY (bench_id) REFERENCES public.court_benches(id);


--
-- TOC entry 5028 (class 2606 OID 33456)
-- Name: court_hearings court_hearings_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_hearings
    ADD CONSTRAINT court_hearings_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);


--
-- TOC entry 5033 (class 2606 OID 33521)
-- Name: court_orders court_orders_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);


--
-- TOC entry 5034 (class 2606 OID 33536)
-- Name: court_orders court_orders_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id);


--
-- TOC entry 5035 (class 2606 OID 33526)
-- Name: court_orders court_orders_hearing_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_hearing_id_fkey FOREIGN KEY (hearing_id) REFERENCES public.court_hearings(id);


--
-- TOC entry 5036 (class 2606 OID 33531)
-- Name: court_orders court_orders_issuing_judge_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.court_orders
    ADD CONSTRAINT court_orders_issuing_judge_id_fkey FOREIGN KEY (issuing_judge_id) REFERENCES public.users(id);


--
-- TOC entry 4995 (class 2606 OID 33081)
-- Name: departments departments_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.departments(id);


--
-- TOC entry 5022 (class 2606 OID 33402)
-- Name: digital_signatures digital_signatures_document_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_signatures
    ADD CONSTRAINT digital_signatures_document_version_id_fkey FOREIGN KEY (document_version_id) REFERENCES public.document_versions(id);


--
-- TOC entry 5023 (class 2606 OID 33412)
-- Name: digital_signatures digital_signatures_signer_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_signatures
    ADD CONSTRAINT digital_signatures_signer_department_id_fkey FOREIGN KEY (signer_department_id) REFERENCES public.departments(id);


--
-- TOC entry 5024 (class 2606 OID 33407)
-- Name: digital_signatures digital_signatures_signer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_signatures
    ADD CONSTRAINT digital_signatures_signer_id_fkey FOREIGN KEY (signer_id) REFERENCES public.users(id);


--
-- TOC entry 5012 (class 2606 OID 33309)
-- Name: document_ai_metadata document_ai_metadata_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_ai_metadata
    ADD CONSTRAINT document_ai_metadata_version_id_fkey FOREIGN KEY (version_id) REFERENCES public.document_versions(id);


--
-- TOC entry 5010 (class 2606 OID 33287)
-- Name: document_versions document_versions_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_versions
    ADD CONSTRAINT document_versions_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id);


--
-- TOC entry 5011 (class 2606 OID 33292)
-- Name: document_versions document_versions_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_versions
    ADD CONSTRAINT document_versions_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- TOC entry 5007 (class 2606 OID 33257)
-- Name: documents documents_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);


--
-- TOC entry 5008 (class 2606 OID 33267)
-- Name: documents documents_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 5009 (class 2606 OID 33262)
-- Name: documents documents_evidence_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_evidence_item_id_fkey FOREIGN KEY (evidence_item_id) REFERENCES public.evidence_items(id);


--
-- TOC entry 5004 (class 2606 OID 33225)
-- Name: evidence_custody_transfers evidence_custody_transfers_evidence_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_custody_transfers
    ADD CONSTRAINT evidence_custody_transfers_evidence_item_id_fkey FOREIGN KEY (evidence_item_id) REFERENCES public.evidence_items(id);


--
-- TOC entry 5005 (class 2606 OID 33235)
-- Name: evidence_custody_transfers evidence_custody_transfers_received_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_custody_transfers
    ADD CONSTRAINT evidence_custody_transfers_received_by_user_id_fkey FOREIGN KEY (received_by_user_id) REFERENCES public.users(id);


--
-- TOC entry 5006 (class 2606 OID 33230)
-- Name: evidence_custody_transfers evidence_custody_transfers_released_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_custody_transfers
    ADD CONSTRAINT evidence_custody_transfers_released_by_user_id_fkey FOREIGN KEY (released_by_user_id) REFERENCES public.users(id);


--
-- TOC entry 5001 (class 2606 OID 33199)
-- Name: evidence_items evidence_items_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_items
    ADD CONSTRAINT evidence_items_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);


--
-- TOC entry 5002 (class 2606 OID 33204)
-- Name: evidence_items evidence_items_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_items
    ADD CONSTRAINT evidence_items_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.evidence_providers(id);


--
-- TOC entry 5003 (class 2606 OID 33209)
-- Name: evidence_items evidence_items_seized_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_items
    ADD CONSTRAINT evidence_items_seized_by_user_id_fkey FOREIGN KEY (seized_by_user_id) REFERENCES public.users(id);


--
-- TOC entry 5013 (class 2606 OID 33329)
-- Name: inter_department_shares inter_department_shares_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inter_department_shares
    ADD CONSTRAINT inter_department_shares_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id);


--
-- TOC entry 5014 (class 2606 OID 33344)
-- Name: inter_department_shares inter_department_shares_granted_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inter_department_shares
    ADD CONSTRAINT inter_department_shares_granted_by_user_id_fkey FOREIGN KEY (granted_by_user_id) REFERENCES public.users(id);


--
-- TOC entry 5015 (class 2606 OID 33334)
-- Name: inter_department_shares inter_department_shares_source_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inter_department_shares
    ADD CONSTRAINT inter_department_shares_source_department_id_fkey FOREIGN KEY (source_department_id) REFERENCES public.departments(id);


--
-- TOC entry 5016 (class 2606 OID 33339)
-- Name: inter_department_shares inter_department_shares_target_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inter_department_shares
    ADD CONSTRAINT inter_department_shares_target_department_id_fkey FOREIGN KEY (target_department_id) REFERENCES public.departments(id);


--
-- TOC entry 5029 (class 2606 OID 33483)
-- Name: order_sheets order_sheets_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);


--
-- TOC entry 5030 (class 2606 OID 33493)
-- Name: order_sheets order_sheets_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id);


--
-- TOC entry 5031 (class 2606 OID 33488)
-- Name: order_sheets order_sheets_hearing_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_hearing_id_fkey FOREIGN KEY (hearing_id) REFERENCES public.court_hearings(id);


--
-- TOC entry 5032 (class 2606 OID 33498)
-- Name: order_sheets order_sheets_recorded_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_sheets
    ADD CONSTRAINT order_sheets_recorded_by_user_id_fkey FOREIGN KEY (recorded_by_user_id) REFERENCES public.users(id);


--
-- TOC entry 4996 (class 2606 OID 33134)
-- Name: user_departments user_departments_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_departments
    ADD CONSTRAINT user_departments_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- TOC entry 4997 (class 2606 OID 33139)
-- Name: user_departments user_departments_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_departments
    ADD CONSTRAINT user_departments_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- TOC entry 4998 (class 2606 OID 33129)
-- Name: user_departments user_departments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_departments
    ADD CONSTRAINT user_departments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 5037 (class 2606 OID 33565)
-- Name: warrants_and_summons warrants_and_summons_assigned_police_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warrants_and_summons
    ADD CONSTRAINT warrants_and_summons_assigned_police_station_id_fkey FOREIGN KEY (assigned_police_station_id) REFERENCES public.departments(id);


--
-- TOC entry 5038 (class 2606 OID 33560)
-- Name: warrants_and_summons warrants_and_summons_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warrants_and_summons
    ADD CONSTRAINT warrants_and_summons_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);


--
-- TOC entry 5039 (class 2606 OID 33555)
-- Name: warrants_and_summons warrants_and_summons_court_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warrants_and_summons
    ADD CONSTRAINT warrants_and_summons_court_order_id_fkey FOREIGN KEY (court_order_id) REFERENCES public.court_orders(id);


--
-- TOC entry 5040 (class 2606 OID 33570)
-- Name: warrants_and_summons warrants_and_summons_executing_officer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warrants_and_summons
    ADD CONSTRAINT warrants_and_summons_executing_officer_id_fkey FOREIGN KEY (executing_officer_id) REFERENCES public.users(id);


-- Completed on 2026-09-10 21:27:46

--
-- PostgreSQL database dump complete
--

\unrestrict rFka8SUshuBffh8YAsbVcNDBkQiWu705yVamb4dBHEjgfZsIH89dnJtjYVtLTsI

