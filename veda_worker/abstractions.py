
import os
import subprocess
import requests
import ast
import json
import uuid

"""Disable insecure warning for requests lib"""
# requests.packages.urllib3.disable_warnings()

"""
Abstractions / A simple way for openVEDA to remember!

AbstractionLayer Object (acts as master abstraction)
    -Video Object
    -[ EncodeObject, EncodeObject ]

"""
from reporting import ErrorObject, Output
import generate_apitoken 
from config import WorkerSetup
from global_vars import *

WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict



class Video():
    """
    This is a simple video class for easy portability between stages in the workflow
    Includes simple tooling for QA checks and a basic API information importer
    """
    def __init__(self, veda_id=None, **kwargs):

        self.veda_id = veda_id

        #-Gathered Data-#
        self.valid = False
        self.vid_pk = None
        self.class_id = None
        self.val_id = None
        self.mezz_extension = None
        self.mezz_bitrate = None
        self.mezz_title = None
        self.mezz_filesize = None
        self.mezz_resolution = None
        self.mezz_duration = None
        self.mezz_filepath = None
        # ** optional
        self.course_url = kwargs.get('course_url', [])


    def activate(self):

        if self.veda_id != None and len(settings['veda_api_url']) == 0:
            ErrorObject().print_error(
                message = 'VEDA API Config Incorrect, run test to debug'
                )
            return None
        """
        test case
        """
        if self.veda_id is None:
            self.mezz_extension = '.mp4'
            self.mezz_title = TEST_VIDEO_FILE
            self.mezz_filepath = os.path.join(TEST_VIDEO_DIR, TEST_VIDEO_FILE)
            self.valid = True
            return None

        """
        Generated Token
        """
        veda_token = generate_apitoken.veda_tokengen()
        if veda_token == None: return None

        data = {
            'edx_id' : self.veda_id,
            }
        headers = {
            'Authorization': 'Token ' + veda_token,
            'content-type': 'application/json'
            }
        x = requests.get(
            '/'.join((settings['veda_api_url'], 'videos', '')),
            params=data, 
            headers=headers
            )

        vid_dict = json.loads(x.text)   
        if len(vid_dict['results']) == 0: return None

        for v in vid_dict['results']:
            """
            Yeah this is horrible, but it's tied to VEDA's model

            """
            self.vid_pk = v['id']
            self.class_id = v['inst_class']
            self.val_id = v['studio_id']
            self.mezz_extension = v['video_orig_extension']
            self.mezz_bitrate = v['video_orig_bitrate']
            self.mezz_title = v['client_title']
            self.mezz_filesize = v['video_orig_filesize']
            '''Do some field cleaning in case of SAR/DAR legacy errors'''
            mezz_resolution = v['video_orig_resolution'].strip().split(' ')[0]
            self.mezz_resolution = mezz_resolution
            '''Clean from unicode (00:00:00.53)'''
            uni_duration = v['video_orig_duration']
            self.mezz_duration = Output._seconds_from_string(uni_duration)
            self.mezz_filepath = '/'.join((
                'https://s3.amazonaws.com', 
                settings['aws_storage_bucket'],
                self.veda_id + '.' + self.mezz_extension
                ))

            if v['video_trans_status'] != 'Corrupt File':
                self.valid = True



class Encode():
    """
    A basic class for easy programatic access to the diff salient variables
    """
    def __init__(self, VideoObject, profile_name):
        self.ffcommand = ''
        self.VideoObject = VideoObject
        self.profile_name = profile_name
        self.encode_suffix = None
        self.filetype = None
        self.resolution = None
        self.rate_factor = None
        self.encode_pk = None
        self.output_file = None
        self.upload_filesize = None
        self.endpoint_url = None


    def pull_data(self):

        encode_dict = {}
        veda_token = generate_apitoken.veda_tokengen()

        if veda_token == None:
            ErrorObject().print_error(
                message="VEDA Token Generate"
                )
            return None

        data = {
            'product_spec' : self.profile_name
            }

        headers = {
            'Authorization': 'Token ' + veda_token,
            'content-type': 'application/json'
            }
        x = requests.get(
            '/'.join((settings['veda_api_url'], 'encodes')), 
            params=data, 
            headers=headers
            )
        enc_dict = json.loads(x.text)   

        if len(enc_dict['results']) == 0:
            ErrorObject().print_error(
                message="VEDA API Encode Mismatch: No Data"
                )
            return None

        for e in enc_dict['results']:
            if e['product_spec'] == self.profile_name and e['profile_active'] is True:
                self.resolution = e['encode_resolution']
                self.rate_factor = e['encode_bitdepth']
                self.filetype = e['encode_filetype']
                self.encode_suffix = e['encode_suffix']
                self.encode_pk = e['id']
        
        if self.encode_suffix == None:
            ErrorObject().print_error(
                message="VEDA API Encode Data Fail: No Suffix"
                )
            return None


def main():
    pass

if __name__ == '__main__':
    sys.exit(main())


