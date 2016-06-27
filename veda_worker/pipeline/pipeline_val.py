
import os
import sys
import requests
import ast
import json
import datetime

"""
Send data to VAL, either Video ID data or endpoint URLs

"""
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from reporting import ErrorObject
import generate_apitoken


class VALData():

    def __init__(self, Settings, VideoObject, EncodeObject=None, **kwargs):
        self.Settings = Settings
        self.VideoObject = VideoObject
        self.EncodeObject = EncodeObject
        self.test_conn = kwargs.get('test_conn', False)
        # self.val_status = kwargs.get('val_status', None)

        self.api_token = None
        self.headers = None
        self.encode_data = {}


    def activate(self):
        """
        Errors covered in other methods
        """
        self.api_token = generate_apitoken.val_tokengen(Settings=self.Settings)
        if self.api_token is False:
            return False
        self.headers = {
            'Authorization': 'Bearer ' + self.api_token, 
            'content-type': 'application/json'
            }

        if self.test_conn is True:
            conn = self.connection_test()
            if conn is False: return False

        complete = self.send_val_data()
        return True


    def connection_test(self):
        """
        Test the connection
        """
        s = requests.get(self.Settings.VAL_API_URL, headers=self.headers, timeout=20)
        if s.status_code > 299:
            ErrorObject(
                method = self,
                message = 'Connection Fail: VAL\nCheck VAL Config'
                )
            return False
        return True


    def determine_status(self, status_code, complete_urls=0):
        '''
        Val Stati : (as of 06.01.16)

        upload (Uploading)
        ingest (In Progress)
        transcode_queue (In Progress)
        transcode_active (In Progress)
        file_delivered (Complete)
        file_complete (Complete)
        file_corrupt (Failed)
        pipeline_error (Failed)
        invalid_token (Invalid Token)
        '''
        if self.VideoObject.valid is False:
            return 'file_corrupt'

        if self.Settings.NODE_VEDA_ATTACH is False and \
        status_code == 200 and \
        complete_urls == len(self.Settings.NODE_ENCODE_PROFILES):
            return 'file_complete'
        else:
            """
            the thinking here is that one is running this singly, 
            so it will return this object unless it's all the encodes
            """
            return 'transcode_active'


    def send_val_data(self):
        """
        VAL is very tetchy -- it needs a great deal of specific info or it will fail
        """
        '''
        sending_data = { 
            encoded_videos = [{
                url="https://testurl.mp4",
                file_size=8499040,
                bitrate=131,
                profile="override",
                }, {...},],
            client_video_id = "This is a VEDA-VAL Test", 
            courses = [ "TEST", "..." ], 
            duration = 517.82,
            edx_video_id = "TESTID",
            status = "transcode_active"
            }
        ## "POST" for new objects to 'video' root url
        ## "PUT" for extant objects to video/id -- 
            cannot send duplicate course records
        '''
        if self.api_token == None: return False

        val_data = { 
            'client_video_id' : self.VideoObject.val_id, 
            'duration' : self.VideoObject.mezz_duration, 
            'edx_video_id' : self.VideoObject.val_id,
            }

        if self.EncodeObject != None:
            self.encode_data = {
                'url' : self.EncodeObject.endpoint_url,
                'file_size' : self.EncodeObject.upload_filesize,
                'bitrate' : self.EncodeObject.rate_factor,
                'profile' : self.EncodeObject.profile_name,
                }

        if not isinstance(self.VideoObject.course_url, list):
            self.VideoObject.course_url = [ self.VideoObject.course_url ]

        r1 = requests.get(
            self.Settings.VAL_API_URL + self.VideoObject.val_id,
                headers=self.headers,
                timeout=20
            )

        if r1.status_code != 200 and r1.status_code != 404:
            ErrorObject(
                method = self,
                message = 'VAL Communication Fail: VAL\nCheck VAL Config'
                )
            return False

        if r1.status_code == 404:
            """
            Generate new VAL ID
            """
            if self.EncodeObject != None:
                val_data['encoded_videos'] = [ self.encode_data ]
            else:
                val_data['encoded_videos'] = []

            val_data['courses'] = self.VideoObject.course_url
            val_data['status'] = self.determine_status(status_code=404)

            ## FINAL CONNECTION
            r2 = requests.post(
                self.Settings.VAL_API_URL,
                data=json.dumps(val_data),
                headers=self.headers,
                timeout=20
                )
            
            if r2.status_code > 299:
                ErrorObject(
                    method = self,
                    message = '%s\n %s\n %s\n' % \
                        ('VAL POST/PUT Fail: VAL', 'Check VAL Config', r2.text)
                    )
                return False

        elif r1.status_code == 200:
            """
            ID is previously extant
            """

            val_api_return = ast.literal_eval(r1.text)

            """
            VAL will not allow duped studio urls to be sent, so 
            we must scrub the data
            """
            for c in self.VideoObject.course_url:
                if c in [o for o in val_api_return['courses']]:
                    self.VideoObject.course_url.remove(c)

            val_data['courses'] = self.VideoObject.course_url

            """
            Double check for profiles in case of overwrite
            """
            val_data['encoded_videos'] = []

            if self.EncodeObject != None:
                for e in val_api_return['encoded_videos']:
                    if e['profile'] != self.EncodeObject.profile_name:
                        val_data['encoded_videos'].append(e)

                val_data['encoded_videos'].append(self.encode_data)

            """
            Determine Status
            """
            val_data['status'] = self.determine_status(
                status_code=200,
                complete_urls=len(val_data['encoded_videos'])
                )

            """
            Make Request, finally
            """
            r2 = requests.put(
                self.Settings.VAL_API_URL + self.VideoObject.val_id,
                data=json.dumps(val_data), 
                headers=self.headers,
                timeout=20
                )

            if r2.status_code > 299:
                ErrorObject(
                    method = self,
                    message = '%s\n %s\n %s\n' % \
                        ('VAL POST/PUT Fail: VAL', 'Check VAL Config', r2.status_code)
                    )
                return False

        return True


def main():
    pass

if __name__ == '__main__':
    sys.exit(main())










