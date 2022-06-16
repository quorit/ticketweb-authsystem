--
-- PostgreSQL database dump
--

-- Dumped from database version 13.4
-- Dumped by pg_dump version 13.4

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

--
-- Name: session_storage; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA session_storage;


ALTER SCHEMA session_storage OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: sessions; Type: TABLE; Schema: session_storage; Owner: postgres
--

CREATE TABLE session_storage.sessions (
    session_id character varying(100) NOT NULL,
    user_dn character varying(200) NOT NULL,
    expired timestamp without time zone NOT NULL
);


ALTER TABLE session_storage.sessions OWNER TO postgres;

--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: session_storage; Owner: postgres
--

ALTER TABLE ONLY session_storage.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (session_id);


--
-- Name: expired_idx; Type: INDEX; Schema: session_storage; Owner: postgres
--

CREATE INDEX expired_idx ON session_storage.sessions USING btree (expired);


--
-- Name: SCHEMA session_storage; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA session_storage TO ticketweb_authsystem;


--
-- Name: TABLE sessions; Type: ACL; Schema: session_storage; Owner: postgres
--

GRANT ALL ON TABLE session_storage.sessions TO ticketweb_authsystem;


--
-- PostgreSQL database dump complete
--

