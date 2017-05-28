
import ast
import json
import os
import requests

from global_vars import *
from reporting import ErrorObject
import generate_apitoken
from config import WorkerSetup

"""
Transmit endpoint URL data to VEDA via VEDA API

"""

WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict
# Disable warning
requests.packages.urllib3.disable_warnings()


class UpdateAPIStatus:

    def __init__(self, VideoObject=None, **kwargs):
        self.VideoObject = VideoObject
        self.veda_video_status = kwargs.get('veda_video_status', None)
        self.val_video_status = kwargs.get('val_video_status', None)
        self.send_veda = kwargs.get('send_veda', True)
        self.send_val = kwargs.get('send_val', True)
        # generated values (VEDA)
        self.veda_token = None
        self.veda_headers = None
        self.veda_video_dict = None
        # generated values (VAL)
        self.val_token = None
        self.val_headers = None
        self.encode_data = {}

    def run(self):
        if self.send_veda is True:
            self.run_veda()
        if self.send_val is True:
            self.run_val()

    def run_veda(self):
        if len(settings) == 0:
            return None

        self.veda_token = generate_apitoken.veda_tokengen()
        if self.veda_token is None:
            ErrorObject().print_error(
                message='VEDA API Conn Fail:\nInvalid Setup/Method'
            )
            return None

        self.veda_headers = {
            'Authorization': 'Token ' + self.veda_token,
            'content-type': 'application/json'
        }

        self.veda_video_dict = self.determine_veda_pk()

        """
        Status Update Only
        """
        if self.veda_video_status is not None:
            return self.send_veda_status()

    def run_val(self):
        """
        Errors covered in other methods
        """
        self.val_token = generate_apitoken.val_tokengen()
        if self.val_token is None:
            return None

        self.val_headers = {
            'Authorization': 'Bearer ' + self.val_token,
            'content-type': 'application/json'
        }
        self.send_val_data()

    def determine_veda_pk(self):
        """
        To keep things manageable, we're going to presuppose an extant VEDA video ID
        --if we want to generate new VEDA objects, we'll do that in a completely separate
        method/script, and quite frankly that belongs in "big VEDA" anyway
        ## Get video information (?)
        """
        if self.VideoObject is None:
            return None

        data = {'edx_id': self.VideoObject.veda_id}

        y = requests.get(
            '/'.join((settings['veda_api_url'], 'videos', '')),
            params=data,
            headers=self.veda_headers,
            timeout=20
        )

        if y.status_code != 200:
            ErrorObject().print_error(
                message='VEDA API Fail: Check VEDA API config'
            )
            return None

        return json.loads(y.text)

    def send_veda_status(self):
        """
        VEDA Stati (as of 05-2016) [salient only to NODE],
        kept in 'globals'
        ----
        'Active Transcode'
        ----
        * This will update a video's status
        """
        for u in self.veda_video_dict['results']:
            """
            This should just send transcode_active, as the other queue
            phases are controlled by other big veda pipeline steps
            """
            if self.VideoObject.valid is not True:
                return None
            video_data = {'video_trans_status': self.veda_video_status}

            w = requests.patch(
                '/'.join((settings['veda_api_url'], 'videos', str(u['id']), '')),
                headers=self.veda_headers,
                data=json.dumps(video_data)
            )
            if w.status_code != 200:

                ErrorObject().print_error(
                    message='VEDA API Fail: File \'GET\' Failure, no objects'
                )

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
        if self.val_token is None:
            return None

        # in case non-studio side upload
        if self.VideoObject.val_id is None or len(self.VideoObject.val_id) == 0:
            self.VideoObject.val_id = self.VideoObject.veda_id

        val_data = {
            'client_video_id': self.VideoObject.val_id,
            'duration': self.VideoObject.mezz_duration,
            'edx_video_id': self.VideoObject.val_id,
        }

        if not isinstance(self.VideoObject.course_url, list):
            self.VideoObject.course_url = [self.VideoObject.course_url]

        r1 = requests.get(
            '/'.join((settings['val_api_url'], self.VideoObject.val_id, '')),
            headers=self.val_headers,
            timeout=20
        )

        if r1.status_code != 200 and r1.status_code != 404:
            """
            Total API Failure
            """
            ErrorObject().print_error(
                message='VAL Communication Fail'
            )
            return None

        if r1.status_code == 404:
            """
            Generate new VAL ID (shouldn't happen, but whatever)
            """
            val_data['encoded_videos'] = []
            val_data['courses'] = self.VideoObject.course_url
            val_data['status'] = self.val_video_status

            # Final Connection
            r2 = requests.post(
                settings['val_api_url'],
                data=json.dumps(val_data),
                headers=self.val_headers,
                timeout=20
            )

            if r2.status_code > 299:
                ErrorObject().print_error(
                    method=self,
                    message='VAL POST/PUT Fail: VAL'
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
            val_data['status'] = self.val_video_status

            """
            Make Request, finally
            """
            r2 = requests.put(
                '/'.join((settings['val_api_url'], self.VideoObject.val_id)),
                data=json.dumps(val_data),
                headers=self.val_headers,
                timeout=20
            )

            if r2.status_code > 299:
                ErrorObject().print_error(
                    message='VAL POST/PUT Fail'
                )
                return None


def main():
    pass

if __name__ == '__main__':
    sys.exit(main())
