import os
import psycopg2
from psycopg2 import sql
from psycopg2 import extras
import binascii
from .config_data import db_conn_string
from .config_data import session_length
from . import bad_request as br
import time
import falcon



_sql_bank = {}
_sql_files = [
    "put_session_data",
    "get_session_expiry",
    "get_session_data",
    "update_session_expiry",
    "get_session_expiry",
    "delete_session",
    "prune_old_sessions"
]


def _init_sql_bank():
    thisdir = os.path.dirname(__file__)
    for filename in _sql_files:
        newpath = os.path.join(thisdir,"sql",filename + ".sql")
        sql_file=open(newpath)
        try:
            sql_code = sql_file.read()
            _sql_bank[filename] = sql_code
        finally:
            sql_file.close()

_init_sql_bank()

class SessionNotFound(br.BadRequest):
    def __init__(self, session_id):
         message = "Session '{0}' does not exist.".format(session_id)
         status = falcon.HTTP_UNAUTHORIZED # really means "unathenticated" in HTTP-speak
         super().__init__(message,status)



class ExpiredSession(br.BadRequest):
    def __init__(self, session_id):
         message = "Session '{0}' has expired.".format(session_id)
         status = falcon.HTTP_UNAUTHORIZED # really means "unathenticated" in HTTP-speak
         super().__init__(message,status)



def _generate_session_key():
    return binascii.b2a_base64(os.urandom(24)).decode().rstrip()


def _run_transaction(transaction):
    conn = psycopg2.connect(db_conn_string)
    try:
        cur = conn.cursor(cursor_factory=extras.DictCursor)
        cur.execute("SET SEARCH_PATH TO session_storage")
        result=transaction(cur)
        conn.commit()
    finally:
        conn.close()
    return result


def _post_session_data_lambda(session_key,user_id,user_data,cur):
    sql_code = _sql_bank['put_session_data']
    cur.execute(sql_code,[session_key,session_length,user_id,user_data["displayName"],user_data["mail"]])
    sql_code = _sql_bank['get_session_expiry']
    cur.execute(sql_code,[session_key])
    thisrow=cur.fetchone()
    return thisrow['expired'] # the expiry



def post_session_data(user_id,user_data):
    session_key = _generate_session_key()
    print("FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUCK")
    print(session_key)
    print(user_id)
    print(user_data)
    expiry = _run_transaction(lambda cur: _post_session_data_lambda(session_key,user_id,user_data,cur))
    return {
        "session_id": session_key,
        "expiry": expiry
    }


def _renew_session_lambda(session_id,cur):
    sql_code = _sql_bank['get_session_data']
    cur.execute(sql_code,[session_id])
    thisrow = cur.fetchone()
    if not thisrow:
        raise SessionNotFound(session_id)
    expiry = thisrow['expired']
    net_id = thisrow["net_id"]
    real_name = thisrow["real_name"]
    email = thisrow["email"]

    if expiry.timestamp() < time.time():
    # expiry is a "datetime" object and we want a standard unic epoch time
        raise falcon.HTTPUnauthorized(description="Session has expired")
    sql_code = _sql_bank['update_session_expiry']
    cur.execute(sql_code,[session_length,session_id])
    sql_code = _sql_bank['get_session_expiry']
    cur.execute(sql_code,[session_id])
    thisrow = cur.fetchone()
    expiry = thisrow["expired"]
    return {
        "net_id": net_id,
        "expiry": expiry,
        "real_name": real_name,
        "email": email

    }


def renew_session(session_id):
    return _run_transaction(lambda cur: _renew_session_lambda(session_id,cur))


def _delete_session_lambda(session_id,cur):
    sql_code = _sql_bank['delete_session']
    cur.execute(sql_code,[session_id])


def delete_session(session_id):
    _run_transaction(lambda cur:_delete_session_lambda(session_id,cur))

def _prune_old_sessions_lambda(cur):
    sql_code = _sql_bank['prune_old_sessions']
    cur.execute(sql_code)

def prune_old_sessions():
    _run_transaction(_prune_old_sessions_lambda)