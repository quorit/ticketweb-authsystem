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
-- Name: token_server; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA token_server;


ALTER SCHEMA token_server OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: sessions; Type: TABLE; Schema: token_server; Owner: postgres
--

CREATE TABLE token_server.sessions (
    session_id character varying(100) NOT NULL,
    user_dn character varying(200) NOT NULL,
    expired timestamp without time zone NOT NULL
);


ALTER TABLE token_server.sessions OWNER TO postgres;

--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: token_server; Owner: postgres
--

ALTER TABLE ONLY token_server.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (session_id);


--
-- Name: expired_idx; Type: INDEX; Schema: token_server; Owner: postgres
--

CREATE INDEX expired_idx ON token_server.sessions USING btree (expired);


--
-- Name: SCHEMA token_server; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA token_server TO tokenserver;


--
-- Name: TABLE sessions; Type: ACL; Schema: token_server; Owner: postgres
--

GRANT ALL ON TABLE token_server.sessions TO tokenserver;


--
-- PostgreSQL database dump complete
--

