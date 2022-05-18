import falcon
import jwt
import json
import re
import time
import ldap
import time
from .config_data import rsa_key_data
from .config_data import ldap_data
from .config_data import service_account_pw
from .sessions import post_session_data
from .sessions import renew_session
from .sessions import delete_session
from . import bad_request as br
import datetime








def create_token(secret,user_id, duration):

     exp_time = int(time.time()) + 60 * duration
     exp_time_english = time.ctime(exp_time)
     print (exp_time_english)
     jwt_payload = {
         'user_id': user_id,
         'exp': exp_time
     }
     headers = {
        'alg': "HS256",
        'typ': "JWT"
     }
     jwt_token = jwt.encode(jwt_payload, secret, algorithm='RS256')
     return jwt_token





def _canonicalise_userid(userid):
    userid_local = userid.lower()
    re_pattern = r"^[0-9a-z]+$"
    if re.search(re_pattern,userid_local):
        return userid_local
    re_pattern = r"^ad(\.queensu.ca){0,1}\\[0-9a-z]+$"
    if re.search(re_pattern,userid_local):
        return userid_local.split("\\")[1]
    re_pattern = r"^[0-9a-z]+@ad\.queensu\.ca$"
    if re.search(re_pattern,userid_local):
        return userid_local.split("@")[0]
     






def _get_json_string(obj,item_key,max_len):
    if item_key not in obj:
        raise br.MissingJSONItem(item_key)
    item = obj.get(item_key)
    if not isinstance(item,str):
        raise br.JSON_ItemNotString(item_key)
    if len(item) > max_len:
        raise br.StringTooBig(item_key)
    if len(item)==0:
        raise br.StringCannotBeEmpty(item_key)
    return item



class NoSessionCookie(br.BadRequest):
    def __init__(self,cookie_name):
        message = "Request did not provide the session cookie, '{0}'.".format(cookie_name)
        status = falcon.HTTP_UNAUTHORIZED # really means "unathenticated" in HTTP-speak
        super().__init__(message,status)


class AuthHandlerSession ():
    def __init__(self,application):
        self.application = application



    def on_post(self,req,resp):


        content_len = req.content_length
        if content_len==0:
            raise br.NoContentReceived()
        if content_len > 1000:
            raise br.ContentTooLarge()
        try:
            req_content = json.load(req.stream)
        except json.decoder.JSONDecodeError as e:
            raise br.JSON_ParseFail() from e
        user_id = _get_json_string(req_content,"user_id",255)
        re_pattern = r"^[0-9a-z]+$|^ad(\.queensu.ca){0,1}\\[0-9a-z]+$|^[0-9a-z]+@ad\.queensu\.ca$"
        if not re.search(re_pattern,user_id,flags=re.IGNORECASE):
             raise br.JSONBadFormatUserId()
        userid = _canonicalise_userid(user_id)
        password = _get_json_string(req_content,"password",255)
        url = ldap_data["url"]
        ldap_handle  = ldap.initialize(url)
        service_account_dn = ldap_data["dn"]
        search_base=ldap_data["search_base"]
        ldap_handle.simple_bind_s(service_account_dn,service_account_pw)
        ldap_handle.set_option(ldap.OPT_REFERRALS, 0)
        ldap_search_result = ldap_handle.search_s(search_base,ldap.SCOPE_SUBTREE,"(sAMAccountName={0})".format(userid),["dn"])
        user_dn = ldap_search_result[0][0]
        if not user_dn:
            raise br.UserNotFound(userid)

        try:
             ldap_handle.simple_bind_s(user_dn,password)
             # The success of this tests the user's password
        except ldap.INVALID_CREDENTIALS:
             raise br.LDAPAuthFail()

        session_data = post_session_data(user_dn)
        print(session_data)
        resp.set_cookie(self.application,session_data["session_id"],expires=session_data["expiry"])
        resp.status = falcon.HTTP_CREATED


   


    def on_get(self,req,resp):
        app_priv_key = rsa_key_data[self.application]["private_key"]
        cookie_vals = req.get_cookie_values(self.application)
        if not cookie_vals:
            raise NoSessionCookie(self.application)
        session_id = cookie_vals[0]
        session_data = renew_session(session_id)
        user_dn = session_data["user_dn"]
        resp.text = create_token(app_priv_key,user_dn,15)
        resp.set_cookie(self.application,session_id,expires=session_data["expiry"])
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_OK

    def on_delete(self,req,resp):
        cookie_vals = req.get_cookie_values(self.application)
        if cookie_vals:
            session_id = cookie_vals[0]
            delete_session(session_id)
            resp.set_cookie(self.application,"",expires=datetime.datetime.min)
            resp.status = falcon.HTTP_NO_CONTENT
        

class PubKeyHandler():
    def __init__(self,application):
        self.application = application

    def on_get(self,req,resp):
        application = self.application
        resp.text = rsa_key_data[application]["public_key_pem"]
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_OK

