
import os
import sys
import requests
import ast

"""
This is a simple set of token generators for attached APIs

"""

from reporting import ErrorObject

"""Disable insecure warning for requests lib"""
requests.packages.urllib3.disable_warnings()


def veda_tokengen(Settings):
    """
    Gen and authorize a VEDA API token
    """
    if Settings.NODE_VEDA_ATTACH is True:
        ## Generate Token
        payload = { 'grant_type' : 'client_credentials' }
        r = requests.post(
            Settings.VEDA_TOKEN_URL, 
            params=payload, 
            auth=(
                Settings.VEDA_API_CLIENTID, 
                Settings.VEDA_API_CLIENTSECRET
                ), 
            timeout=20
            )
        if r.status_code == 200:
            veda_token = ast.literal_eval(r.text)['access_token']
        else:
            ErrorObject(
                message = 'ERROR : VEDA Token Generate',
                method = 'veda_tokengen',
            )
            return None

        ## Authorize token
        """
        This is based around the VEDA "No Auth Server" hack
        """
        payload = { 'data' : veda_token }
        t = requests.post(Settings.VEDA_AUTH_URL, data=payload)
        if t.status_code == 200 and t.text == 'True':
            return veda_token
        else:
            ErrorObject(
                message = 'ERROR : VEDA Token Auth',
                method = 'veda_tokengen',
            )
            return None

    else:
        ErrorObject(
            message = 'ERROR : CONFIG - veda_attach is False',
            method = 'veda_tokengen',
        )
        return None


def val_tokengen(Settings):

    payload = {
        'grant_type' : 'password',
        'client_id': Settings.VAL_CLIENT_ID,
        'client_secret': Settings.VAL_CLIENT_SECRET, 
        'username' : Settings.VAL_USERNAME,
        'password' : Settings.VAL_USERPASS,
        }

    r = requests.post(Settings.VAL_TOKEN_URL, data=payload, timeout=20)

    if r.status_code != 200:
        ErrorObject(
            method = 'val_tokengen',
            message = 'Token Gen Fail: VAL\nCheck VAL Config'
            )
        return None
        
    val_token = ast.literal_eval(r.text)['access_token']
    return val_token
