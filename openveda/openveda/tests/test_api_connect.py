
import os
import sys
import requests
import ast
import unittest

"""
This is an API connection test

"""

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
from config import OVConfig

CF = OVConfig()
CF.run()
settings = CF.settings_dict

'''
Import Pipeline
'''
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'pipeline'
        )
    )
from pipeline_val import VALData


class TestVALCredentials(unittest.TestCase):

    def test_api_setup(self):
        salient_variables = [
            'val_token_url', 
            'val_api_url',
            'val_client_id',
            'val_secret_key',
            'val_username',
            'val_password' 
            ]

        for s in salient_variables:
            self.assertTrue(len(settings[s]) > 0)

    def test_api_credentials(self):

        V1 = VALData()
        val_token = V1.val_tokengen()
        self.assertTrue(val_token is not None)

        headers = {
            'Authorization': 'Bearer ' + val_token, 
            'content-type': 'application/json'
            }

        s = requests.get(settings['val_api_url'], headers=headers, timeout=20)
        self.assertTrue(s.status_code < 299)


def main():
    unittest.main()

if __name__ == '__main__':
    sys.exit(main())



