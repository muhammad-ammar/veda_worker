
import os
import sys
import requests
import ast
"""Disable insecure warning for requests lib"""
requests.packages.urllib3.disable_warnings()

"""
This is a simple set of token generators for attached APIs

"""
from config import WorkerSetup
from reporting import ErrorObject
WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict



def veda_tokengen():
    """
    Gen and authorize a VEDA API token
    """
    '''Generate Token'''
    payload = { 'grant_type' : 'client_credentials' }
    r = requests.post(
        settings['veda_token_url'],
        params=payload, 
        auth=(
            settings['veda_client_id'], 
            settings['veda_secret_key']
            ), 
        timeout=20
        )
    if r.status_code == 200:
        veda_token = ast.literal_eval(r.text)['access_token']
    else:
        ErrorObject().print_error(
            message = 'VEDA Token Generate',
            )
        return None

    '''Authorize token'''
    """
    This is based around the VEDA "No Auth Server" hack
    """
    payload = { 'data' : veda_token }
    t = requests.post(settings['veda_auth_url'], data=payload)

    if t.status_code == 200 and t.text == 'True':
        return veda_token
    else:
        ErrorObject().print_error(
            message = 'VEDA Token Authorization',
            )
        return None



def val_tokengen():
    """
    Gen and authorize a VAL API token
    """
    payload = {
        'grant_type' : 'password',
        'client_id': settings['val_client_id'],
        'client_secret':  settings['val_secret_key'], 
        'username' : settings['val_username'],
        'password' : settings['val_password']
        }

    r = requests.post(settings['val_token_url'], data=payload, timeout=20)

    if r.status_code != 200:
        ErrorObject().print_error(
            message = 'Token Gen Fail: VAL\nCheck VAL Config'
            )
        return None

    val_token = ast.literal_eval(r.text)['access_token']
    return val_token














