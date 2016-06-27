
import os
import sys
import requests
import ast

"""
This is an API connection test

Involves a kwarg sent as val_test, veda_test and 
was tested as an XOR, but can be modded to 
"""

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import generate_apitoken

from reporting import ErrorObject, TestReport



class ConnectionTest():
    
    def __init__(self, Settings, **kwargs):
        self.Settings = Settings
        self.passed = False
        self.val_test = kwargs.get('val_test', False)
        self.veda_test = kwargs.get('veda_test', False)

        '''veda/val test should be sent as XOR'''

        if self.val_test is True:
            test_name = 'VAL API Link Test'
            self.passed = self.val_connection_test()
            TestReport(self.passed, test_name)

        if self.veda_test is True:
            test_name = 'VEDA API Link Test'
            self.passed = self.veda_connection_test()
            TestReport(self.passed, test_name)


    def api_setup_test(self, api):
        if api == 'VAL':
            if self.Settings.VAL_ATTACH is False:
                return False

            salient_variables = [
                'VAL_TOKEN_URL', 
                'VAL_API_URL',
                'VAL_CLIENT_ID',
                'VAL_CLIENT_SECRET', 
                'VAL_USERNAME',
                'VAL_USERPASS',
                ]
            for s in salient_variables:
                if len(eval('self.Settings.' + s)) == 0:
                    raise ErrorObject(
                        method = self,
                        message = s
                        )
                    return False

        elif api == 'VEDA':
            if self.Settings.NODE_VEDA_ATTACH is False:
                return False

            salient_variables = [
                'VEDA_API_CLIENTID',
                'VEDA_API_CLIENTSECRET',
                'VEDA_TOKEN_URL',
                'VEDA_API_URL',
                'VEDA_API_URL',
                ]

            for s in salient_variables:
                if len(eval('self.Settings.' + s)) == 0:
                    raise ErrorObject(
                        method = self,
                        message = s
                        )
                    return False

        return True


    def val_connection_test(self):
        setup = self.api_setup_test(api='VAL')
        if setup is False: return False

        self.val_token = generate_apitoken.val_tokengen(Settings=self.Settings)
        if self.val_token == None:
            raise ErrorObject(
                method=self,
                message='VAL USER/PASS'
                )
            return False

        headers = {
            'Authorization': 'Bearer ' + self.val_token, 
            'content-type': 'application/json'
            }
        try:
            s = requests.get(self.Settings.VAL_API_URL, headers=headers, timeout=20)
        except:
            raise SetupError(
                method=self,
                varbls='VAL URL'
                )
            return False

        if s.status_code > 299:
            raise ErrorObject(
                method=self,
                message='VAL URL'
                )
            return False

        return True


    def veda_connection_test(self):
        setup = self.api_setup_test(api='VEDA')
        if setup is False: return False

        self.veda_token = generate_apitoken.veda_tokengen(Settings=self.Settings)
        if self.veda_token == None:
            return False        
        ## Generate Token

        headers = {
            'Authorization': 'Bearer ' + self.veda_token, 
            'content-type': 'application/json'
            }
        try:
            s = requests.get(self.Settings.VEDA_API_URL, headers=headers, timeout=20)
        except:
            raise ErrorObject(
                method=self,
                message='VEDA API URL'
                )
            return False

        if s.status_code > 299:
            raise ErrorObject(
                method=self,
                message='VEDA API CONNECTION'
                )
            return False

        return True


"""
Just for writing and testing
"""
def main():
    NCE1 = ConnectionTest(val_test = True, veda_test = True)


if __name__ == '__main__':
    sys.exit(main())



