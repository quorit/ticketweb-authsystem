import os
import json
import sys
from cryptography.hazmat.primitives import serialization




if sys.base_prefix != sys.prefix:
    _etc_path = sys.prefix + "/etc"
else:
    _etc_path = "/etc"



def _get_db_conn_string():
    secret_file = os.path.join(_etc_path,"ticketweb","token-server","db-conn-string")
    f = open(secret_file,"r")
    secret_data = f.read()
    f.close()
    return secret_data.strip()


db_conn_string = _get_db_conn_string()


def _get_config_data():
    config_file = os.path.join(_etc_path,"ticketweb","token-server","config-data.json")
    f = open(config_file,"r")
    config_data = json.load(f)
    f.close()
    return config_data

_config_data = _get_config_data()

applications = _config_data["applications"]

def _init_rsa_key_data():
    rsa_path = os.path.join(_etc_path,"ticketweb","token-server","rsa")
    # I need to generate a table of of pairs.
    # first member of each pair is priv key, that i can use to encode with
    # second member is a serilisation of a public key that I can export through the web api
    # to an application server.
    # note that with these keys, pub keys are fully determinable from priv keys.
    # the files we are reading in are serializations of priv keys.
    result = {}
    for application in applications:
        # read in the priv-key serialisation (pem) file for that application
        key_file = os.path.join(rsa_path,application+".pem")
        f = open(key_file,"rb")
        private_key = serialization.load_pem_private_key(
                                                            f.read(),
                                                            password=None,
                                                        )
        f.close()
        pub_key = private_key.public_key()
        pub_key_bytes = pub_key.public_bytes(
                                              encoding=serialization.Encoding.PEM,
                                              format=serialization.PublicFormat.SubjectPublicKeyInfo
                                             )
        pub_key_pem = pub_key_bytes.decode()
        result[application]= {
                                        "private_key": private_key,
                                        "public_key_pem": pub_key_pem
                                    }
    return result




rsa_key_data = _init_rsa_key_data()



ldap_data = _config_data["ldap"]

session_length = _config_data["session_length_mins"]


def _get_pw():

    secret_file = os.path.join(_etc_path,"service_creds.json")
    f = open(secret_file,"r")
    secret_data = json.load(f)
    f.close()
    return secret_data[ldap_data["service_account"]]

service_account_pw = _get_pw()

print ("this really happened No!")