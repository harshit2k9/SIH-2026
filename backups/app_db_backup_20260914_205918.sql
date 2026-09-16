--
-- PostgreSQL database dump
--

\restrict WPmljHuj1FG4cdQiyT1SsxZdYGPoJO4ChwlDeg3HEZYN2e42tsfN73h5ub0Uba5

-- Dumped from database version 15.19
-- Dumped by pg_dump version 15.19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP TRIGGER IF EXISTS trg_chain_of_custody_hash ON public.chain_of_custody_logs;
DROP RULE IF EXISTS block_updates ON public.chain_of_custody_logs;
DROP RULE IF EXISTS block_deletes ON public.chain_of_custody_logs;
DROP INDEX IF EXISTS public.idx_chain_logs_event_type_gin;
ALTER TABLE IF EXISTS ONLY public.chain_of_custody_logs DROP CONSTRAINT IF EXISTS audit_check_pkey;
ALTER TABLE IF EXISTS public.chain_of_custody_logs ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.audit_check_id_seq;
DROP TABLE IF EXISTS public.chain_of_custody_logs;
DROP FUNCTION IF EXISTS public.process_secure_audit_trail();
DROP EXTENSION IF EXISTS pgcrypto;
DROP EXTENSION IF EXISTS pg_trgm;
--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: process_secure_audit_trail(); Type: FUNCTION; Schema: public; Owner: admin
--

CREATE FUNCTION public.process_secure_audit_trail() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.process_secure_audit_trail() OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: chain_of_custody_logs; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.chain_of_custody_logs (
    id bigint NOT NULL,
    event_type character varying(80) NOT NULL,
    user_id integer NOT NULL,
    case_id integer,
    document_id integer,
    document_version_id integer,
    event_timestamp timestamp with time zone DEFAULT now() NOT NULL,
    metadata jsonb,
    previous_hash character(64) NOT NULL,
    current_hash character(64) NOT NULL
);


ALTER TABLE public.chain_of_custody_logs OWNER TO admin;

--
-- Name: audit_check_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.audit_check_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_check_id_seq OWNER TO admin;

--
-- Name: audit_check_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.audit_check_id_seq OWNED BY public.chain_of_custody_logs.id;


--
-- Name: chain_of_custody_logs id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.chain_of_custody_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_check_id_seq'::regclass);


--
-- Data for Name: chain_of_custody_logs; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.chain_of_custody_logs (id, event_type, user_id, case_id, document_id, document_version_id, event_timestamp, metadata, previous_hash, current_hash) FROM stdin;
1	TEST_EVENT	1	\N	\N	\N	2026-09-14 19:54:36.527206+00	\N	0000000000000000000000000000000000000000000000000000000000000000	f48bc8b0c72e8cd679e83cae0a74430c55b86b4ff186394cae2bd6edbb416a50
\.


--
-- Name: audit_check_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.audit_check_id_seq', 1, true);


--
-- Name: chain_of_custody_logs audit_check_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.chain_of_custody_logs
    ADD CONSTRAINT audit_check_pkey PRIMARY KEY (id);


--
-- Name: idx_chain_logs_event_type_gin; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_chain_logs_event_type_gin ON public.chain_of_custody_logs USING gin (event_type public.gin_trgm_ops);


--
-- Name: chain_of_custody_logs block_deletes; Type: RULE; Schema: public; Owner: admin
--

CREATE RULE block_deletes AS
    ON DELETE TO public.chain_of_custody_logs DO INSTEAD NOTHING;


--
-- Name: chain_of_custody_logs block_updates; Type: RULE; Schema: public; Owner: admin
--

CREATE RULE block_updates AS
    ON UPDATE TO public.chain_of_custody_logs DO INSTEAD NOTHING;


--
-- Name: chain_of_custody_logs trg_chain_of_custody_hash; Type: TRIGGER; Schema: public; Owner: admin
--

CREATE TRIGGER trg_chain_of_custody_hash BEFORE INSERT ON public.chain_of_custody_logs FOR EACH ROW EXECUTE FUNCTION public.process_secure_audit_trail();


--
-- PostgreSQL database dump complete
--

\unrestrict WPmljHuj1FG4cdQiyT1SsxZdYGPoJO4ChwlDeg3HEZYN2e42tsfN73h5ub0Uba5

