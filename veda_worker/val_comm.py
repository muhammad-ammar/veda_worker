
import os
import sys
import requests
import ast
import json
import datetime

"""
Send data to VAL, Video ID data

"""
from global_vars import *
from reporting import ErrorObject
import generate_apitoken
from config import WorkerSetup
WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict


class VALData():

    def __init__(self, VideoObject, **kwargs):
        self.VideoObject = VideoObject
        self.video_status = kwargs.get('video_status', None)
        # generated values
        self.api_token = None
        self.headers = None
        self.encode_data = {}


    def run(self):
        """
        Errors covered in other methods
        """
        self.api_token = generate_apitoken.val_tokengen()
        if self.api_token is None:
            return None

        self.headers = {
            'Authorization': 'Bearer ' + self.api_token, 
            'content-type': 'application/json'
            }

        self.send_val_data()


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
        if self.api_token == None: return None

        # in case non-studio side upload
        if self.VideoObject.val_id is None or len(self.VideoObject.val_id) == 0:
            self.VideoObject.val_id = self.VideoObject.veda_id

        val_data = { 
            'client_video_id' : self.VideoObject.val_id, 
            'duration' : self.VideoObject.mezz_duration, 
            'edx_video_id' : self.VideoObject.val_id,
            }

        if not isinstance(self.VideoObject.course_url, list):
            self.VideoObject.course_url = [ self.VideoObject.course_url ]

        r1 = requests.get(
            '/'.join((settings['val_api_url'], self.VideoObject.val_id, '')),
                headers=self.headers,
                timeout=20
            )

        if r1.status_code != 200 and r1.status_code != 404:
            """
            Total API Failure
            """
            ErrorObject().print_error(
                message = 'VAL Communication Fail'
                )
            return None

        if r1.status_code == 404:
            """
            Generate new VAL ID (shouldn't happen, but whatever)
            """
            val_data['encoded_videos'] = []
            val_data['courses'] = self.VideoObject.course_url
            val_data['status'] = self.video_status

            ## FINAL CONNECTION
            r2 = requests.post(
                settings['val_api_url'],
                data=json.dumps(val_data),
                headers=self.headers,
                timeout=20
                )
            
            if r2.status_code > 299:
                ErrorObject().print_error(
                    method = self,
                    message = 'VAL POST/PUT Fail: VAL'
                    )
                return None

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
            # add back in the encodes
            for e in val_api_return['encoded_videos']:
                val_data['encoded_videos'].append(e)

            """
            Determine Status
            """
            val_data['status'] = self.video_status

            """
            Make Request, finally
            """
            r2 = requests.put(
                '/'.join((settings['val_api_url'], self.VideoObject.val_id)),
                data=json.dumps(val_data), 
                headers=self.headers,
                timeout=20
                )

            if r2.status_code > 299:
                ErrorObject().print_error(
                    message = 'VAL POST/PUT Fail'
                    )
                return None


def main():
    pass

if __name__ == '__main__':
    sys.exit(main())










