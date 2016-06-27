
import os
import sys
import requests
import ast
import json
import datetime

"""
Transmit endpoint URL data to VEDA via VEDA API

"""
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from node_config import *
from node_secrets import *

from reporting import ErrorObject
import generate_apitoken


class VEDAData():

    def __init__(self, Settings, VideoObject, EncodeObject=None, **kwargs):
        self.Settings = Settings
        self.VideoObject = VideoObject
        self.EncodeObject = EncodeObject
        """
        Test Connection
        """
        self.testconn = kwargs.get('testconn', False)
        """
        Generate Status Change?
        """
        self.video_status = kwargs.get('video_status', False)
        """
        Generated Vars
        """
        self.api_token = None
        self.headers = None
        self.video_dict = None


    def activate(self):
        if self.VideoObject.video_id == None:
            ErrorObject(
                method = self,
                message = 'VEDA API Fail:\nInvalid Method\nNo Video ID in payload'
                )
            return False

        self.api_token = generate_apitoken.veda_tokengen(Settings=self.Settings)
        if self.api_token == None:
            ErrorObject(
                method = self,
                message = 'VEDA API Conn Fail:\nInvalid Setup/Method'
                )
            return False
        self.headers = {
            'Authorization': 'Bearer ' + self.api_token, 
            'content-type': 'application/json'
            }

        if self.testconn is True:
            passed = self.connect_test()
            if passed is False:
                ErrorObject(
                    method = self,
                    message = 'VEDA API Conn Fail:\nAPI Connection Test'
                    )
                return False

        self.video_dict = self.determine_video_id()
        if self.video_dict == None or self.video_dict['count'] < 1:
            ErrorObject(
                method = self,
                message = 'VEDA API Fail:\nFile \'GET\' Failure, no objects\n\
                    Check VEDA API config, video ID'
                )
            return False

        if self.video_status is True:
            return self.send_video_status()
        
        """
        If sending URL
        """
        if self.EncodeObject == None:
            ErrorObject(
                method = self,
                message = 'VEDA API Fail:\nInvalid Encode Object'
                    )
            return False

        return self.send_url()


    def connect_test(self):
        s = requests.get(self.Settings.VEDA_API_URL, headers=self.headers, timeout=20)
        if s.status_code > 299:
            ErrorObject(
                method = self,
                message = 'Connection Test Fail:VEDA\nCheck VEDA Config'
                )
            return False
        return True


    def determine_video_id(self):
        """
        To keep things manageable, we're going to presuppose an extant VEDA video ID
        --if we want to generate new VEDA objects, we'll do that in a completely separate
            method/script, and quite frankly that belongs in "big VEDA" anyway
        ## Get video information (?)
        """
        data = {
            'edx_id' : self.VideoObject.video_id,
            }
        y = requests.get(
            self.Settings.VEDA_API_URL + 'videos', 
            params=data, 
            headers=self.headers, 
            timeout=20
            )
        if y.status_code != 200:
            ErrorObject(
                method = self,
                message = 'VEDA API Fail:\nAPI Url, 404\nCheck VEDA API config'
                )
            return None

        return json.loads(y.text)


    def send_video_status(self):
        """
        VEDA Stati (as of 05-2016) [salient only to NODE]
        ----
        'Transcode Queue'
        'Active Transcode'
        'Transcode Retry'
        'Transcode Complete'
        'Deliverable Upload'
        'File Complete'
        'Corrupt File'
        ----

        * This will update a video's status
        """
        for u in self.video_dict['results']:
            """
            This should just send transcode_active, as the other queue
            phases are controlled by other big veda pipeline steps
            """
            if self.VideoObject.valid is True:
                video_data = {
                    'video_trans_status' : 'Active Transcode', ## get course pk?
                    }
            else:
                video_data = {
                    'video_trans_status' : 'Corrupt File', ## get course pk?
                    }

            w = requests.patch(
                self.Settings.VEDA_API_URL + 'videos/' + str(u['id']) + '/', 
                headers=self.headers, 
                data=json.dumps(video_data)
                )
            if w.status_code != 200:
                ErrorObject(
                    method = self,
                    message = 'VEDA API Fail:\nFile \'GET\' Failure, no objects\n\
                        Check VEDA API config, video ID'
                    )
                return False
        return True


    def send_url(self):
        if len(self.video_dict['results']) > 1:
            """
            get latest
            """
            latest = None
            for u in self.video_dict['results']:
                if latest == None or u['video_trans_start'] > latest:
                    latest = u['video_trans_start']
                    video_fk = u['id']
        else:
            video_fk = self.video_dict['results'][0]['id']

        url_data = {
            'encode_profile' : self.EncodeObject.encode_pk, 
            'videoID' : video_fk,
            'encode_url' : self.EncodeObject.endpoint_url,
            'url_date' : str(datetime.datetime.utcnow()),
            'encode_duration' : self.VideoObject.mezz_duration,
            'encode_bitdepth' : self.EncodeObject.rate_factor,
            'encode_size' : self.EncodeObject.upload_filesize,
            'md5_sum' : self.EncodeObject.hash_sum
            }
        w = requests.post(
            self.Settings.VEDA_API_URL + 'urls/', 
            headers=self.headers, 
            data=json.dumps(url_data)
            )

        if w.status_code > 299:
            ErrorObject(
                method = self,
                message = 'VEDA API Fail:\nURL \'POST\' Failure\n\
                    Check VEDA API config, video ID, Encode ID'
                )
            return False

        return True



def main():
    pass

if __name__ == '__main__':
    sys.exit(main())

































