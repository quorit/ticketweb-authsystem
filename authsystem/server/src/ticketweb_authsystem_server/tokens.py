import falcon
import jwt
import json
import re
import time
import time
from .config_data import rsa_key_data
from .config_data import login_portal_data
from .sessions import post_session_data
from .sessions import renew_session
from .sessions import delete_session
import requests
from jwt import PyJWKClient








def create_token(secret,net_id,real_name,email,duration):

     exp_time = int(time.time()) + 60 * duration
     exp_time_english = time.ctime(exp_time)
     print (exp_time_english)
     jwt_payload = {
         'sub': net_id,
         'name': real_name,
         'email': email,
         'exp': exp_time
     }
     headers = {
        'alg': "HS256",
        'typ': "JWT"
     }
     jwt_token = jwt.encode(jwt_payload, secret, algorithm='RS256')
     return jwt_token


def get_ms_signing_key(token, tenant_id):
    # 1. The URL where Microsoft publishes their current public keys
    jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
    
    # 2. Initialize the JWK Client
    jwks_client = PyJWKClient(jwks_url)
    
    # 3. This function:
    #    - Extracts the 'kid' from your token's header
    #    - Fetches the keys from the URL
    #    - Finds the matching key and returns a 'signing_key' object
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    
    return signing_key



def _get_signing_key(req_token,issuer_portal):
    login_portal_instance_data = login_portal_data[issuer_portal] 
    if issuer_portal == "ticketweb":
        loginportal_pub_key_url = login_portal_instance_data["signing_key_url"]
        receive = requests.get(loginportal_pub_key_url)
        signing_key = receive.text
        if receive.status_code != 200:
            raise Exception("Failed commmunication with login portal")
        return signing_key
    else: # microsoft
        tenant_id = login_portal_instance_data["tenant_id"]
        signing_key = get_ms_signing_key(req_token,tenant_id)
        return signing_key






def _get_user_data(req):
   
    
    req_auth_hdr = req.get_header('Authorization')
    if not req_auth_hdr:
        raise falcon.HTTPUnauthorized(
            description="Missing authorization header"
        )
    print(req_auth_hdr)
    if len(req_auth_hdr) > 2048:
        raise falcon.HTTPUnauthorized(
            description="'Authorization' header is too long."
        )
    re_pattern = r"^Bearer [-a-zA-Z0-9._]+$"
    if not re.search(re_pattern,req_auth_hdr):
        raise falcon.HTTPUnauthorized(
            description="'Authorization' header does not have format, 'Bearer <jwt token>'"
        )
    req_token = req_auth_hdr[len("Bearer "):]

    req_token_fields = jwt.decode(req_token, options={"verify_signature": False})
    print (req_token_fields)
    if req_token_fields["iss"] != "ticketweb_portal":
        issuer_portal = "microsoft"
    else:
        issuer_portal = "ticketweb"
    signing_key = _get_signing_key(req_token,issuer_portal)
    if issuer_portal == "ticketweb":
        jwt_audience = "ticketweb_auth_server"
    else: # microsoft portal
        jwt_audience = login_portal_data["microsoft"]["client_id"]

    try:
        req_decoded = jwt.decode(
                req_token,signing_key,
                algorithms=['RS256'],
                options={"require": ["upn","name","email","exp","uti"]},
                audience=jwt_audience)
        print(req_decoded)
    except jwt.exceptions.ExpiredSignatureError as e:
        raise falcon.HTTPUnauthorized(
            description="JWT token has expired"
        )
    except jwt.exceptions.InvalidTokenError as e:
        raise falcon.HTTPUnauthorized(
            description="Invalid Token Error: " + str(e)
        )
    if not isinstance(req_decoded["upn"],str):
        raise falcon.HTTPBadRequest(
            description="sub field in jwt data does not have string type"
        )
    if not isinstance(req_decoded["name"],str):
        raise falcon.HTTPBadRequest(
            description="name field in jwt data does not have string type"
        )
    if not isinstance(req_decoded["email"],str):
        raise falcon.HTTPBadRequest(
            description="email field in jwt data does not have string type"
        )
    if not isinstance(req_decoded["uti"],str):
        raise falcon.HTTPBadRequest(
            description="uti field in jwt data does not have string type"
        )
    req_decoded.pop("exp")
    return req_decoded



class AuthHandlerSession ():
    def __init__(self,application):
        self.application = application

   


    def on_get(self,req,resp):
        app_priv_key = rsa_key_data[self.application]["private_key"]
        cookie_vals = req.get_cookie_values(self.application)
        if not cookie_vals or not cookie_vals[0]:
            # the first thing to do is to see if there is a jwt token from the login portal
            #
            user_data = _get_user_data(req)
            session_id=user_data["uti"]
            expiry = post_session_data(user_data)
            net_id = user_data["upn"].partition('@')[0]
            real_name = user_data["name"]
            email = user_data["email"]
        else:
            session_id = cookie_vals[0]
            print("Cookie"+session_id)
            session_data = renew_session(self.application,session_id)  
            # if the session is not found
            # or if the session has expired, appropriate errors get thrown
            # The error handler will unset the cookie in the response
            net_id = session_data["net_id"]
            real_name = session_data["real_name"]
            email = session_data["email"]
            expiry = session_data["expiry"]
        token = create_token(app_priv_key,net_id,real_name,email,15)
        resp.set_cookie(self.application,session_id,expires=expiry)
        response_body = {
            "jwt_token": token,
            "user_data": {
                    "net_id": net_id,
                    "real_name": real_name,
                    "email": email
                }
            }
        resp.text = json.dumps(response_body)
        resp.content_type = falcon.MEDIA_JSON
        resp.status = falcon.HTTP_OK

    def on_delete(self,req,resp):
        cookie_vals = req.get_cookie_values(self.application)
        if cookie_vals:
            session_id = cookie_vals[0]
            delete_session(session_id)
            resp.unset_cookie(self.application)
            # resp.set_cookie(self.application,"",expires=datetime.datetime.min)
            resp.status = falcon.HTTP_NO_CONTENT
        

class PubKeyHandler():
    def __init__(self,application):
        self.application = application

    def on_get(self,req,resp):
        application = self.application
        resp.text = rsa_key_data[application]["public_key_pem"]
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_OK

