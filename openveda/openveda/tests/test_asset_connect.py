
import os
import sys
import requests
# import boto
from boto.s3.connection import S3Connection
import unittest

"""
Test AWS credentials

"""

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
from config import OVConfig
CF = OVConfig()
CF.run()
settings = CF.settings_dict



class TestAWSCredentials(unittest.TestCase):
    
    def test_storage_config(self):

        salient_variables = [
            'aws_access_key',
            'aws_deliver_bucket',
            'aws_secret_key',
            'aws_storage_bucket'
            ]

        for s in salient_variables:
            self.assertTrue(len(settings[s]) > 0)

    def test_storage_creds(self):
        print settings
        conn = S3Connection(settings['aws_access_key'], settings['aws_secret_key'])
        deliver_bucket = settings['aws_deliver_bucket'].split('/')[0]
        storage_bucket = settings['aws_storage_bucket'].split('/')[0]
        try:
            bucket = conn.get_bucket(deliver_bucket)
            self.assertTrue(True)
        except:
            self.assertTrue(False)
        try:
            bucket = conn.get_bucket(storage_bucket)
            self.assertTrue(True)
        except:
            self.assertTrue(False)

        if settings['aws_ingest_bucket'] is not None and len(settings['aws_ingest_bucket']) > 0:
            ingest_bucket = settings['aws_ingest_bucket'].split('/')[0]
            try:
                bucket = conn.get_bucket(ingest_bucket)
                self.assertTrue(True)
            except:
                self.assertTrue(False)



def main():
    unittest.main()

if __name__ == '__main__':
    sys.exit(main())

