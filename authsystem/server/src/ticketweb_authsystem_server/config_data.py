import os
import json
import sys
from cryptography.hazmat.primitives import serialization




if sys.base_prefix != sys.prefix:
    _etc_path = sys.prefix + "/etc"
else:
    _etc_path = "/etc"




def _get_config_data():
    config_file = os.path.join(_etc_path,"ticketweb","authsystem","config.json")
    f = open(config_file,"r")
    config_data = json.load(f)
    f.close()
    return config_data

_config_data = _get_config_data()




def _get_applications():
    apps_file = os.path.join(_etc_path,"ticketweb","authsystem","applications.json")
    f = open(apps_file,"r")
    apps_data = json.load(f)
    f.close()
    return apps_data["application_set"]

applications = _get_applications()


def _init_rsa_key_data():
    rsa_path = os.path.join(_etc_path,"ticketweb","authsystem","rsa")
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


session_length = _config_data["session_length_mins"]

loginportal_pub_key_url = _config_data["loginportal_pub_key_url"]



def _get_db_conn_string():
    db_conn_string_exec = _config_data["db_conn_string_exec"]
    db_conn_string = os.popen(db_conn_string_exec).read()
    return db_conn_string


db_conn_string = _get_db_conn_string()