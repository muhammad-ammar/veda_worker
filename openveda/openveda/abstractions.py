
import os
import subprocess
import ast
import json
import uuid

"""
Abstractions / A simple way for openVEDA to remember!

AbstractionLayer Object (acts as master abstraction)
    -Video Object
    -[ EncodeObject, EncodeObject ]


"""
from config import OVConfig
CF = OVConfig()
CF.run()
settings = CF.settings_dict

from reporting import ErrorObject


class AbstractionLayer():
    """
    A simple object to hold states in openVEDA
    for basic reporting/logging and tracking of long running
    processes
    """
    def __init__(self, **kwargs):
        self.VideoObject = kwargs.get('VideoObject', None)
        self.Encodes = []
        self.complete = False
        self.delivered = False



class Video():
    """
    This is a simple video class for easy portability between stages in the workflow
    Includes simple tooling for QA checks and a basic API information importer
    """
    def __init__(self, mezz_video, **kwargs):

        self.mezz_video = mezz_video

        self.val_id = kwargs.get('val_id', None)
        self.course_url = kwargs.get('course_url', [])
        self.client_title = kwargs.get('client_title', None)
        """
        General Video Data
        """
        self.mezz_filepath = None
        self.mezz_bitrate = None
        self.mezz_resolution = None
        self.mezz_filesize = None 
        self.mezz_duration = None
        # ##
        self.valid = False

    def _seconds_from_string(self, duration):
        hours = float(duration.split(':')[0])
        minutes = float(duration.split(':')[1])
        seconds = float(duration.split(':')[2])
        duration_seconds = (((hours * 60) + minutes) * 60) + seconds
        return duration_seconds


    def validate(self):
        """
        Presumes a video object tied to an actual file in the workdir

        """
        self.mezz_filepath = os.path.join(
            settings['workdir'], 
            self.mezz_video
            )

        '''Generate missing metadata'''
        if self.client_title is None:
            self.client_title = self.mezz_video.split('.')[0]
        if self.val_id is None:
            self.val_id = uuid.uuid1().hex[0:10]

        """

        ## Video Validation ##

        """
        if not os.path.exists(self.mezz_filepath):
            ErrorObject().print_error(message='Mezz. File Not Found')
            self.valid = False
            return None

        self.mezz_filesize = os.stat(self.mezz_filepath).st_size
        if self.mezz_filesize == 0:
            ErrorObject().print_error(message='Video size: 0')
            self.valid = False
            return None

        """
        This is a little bit ugly, and for that I am sorry
        HOWEVER, it is functional with ffprobe 2.3.3
        """
        ffcommand = settings['ffprobe'] + ' -hide_banner '
        ffcommand += '\"' + self.mezz_filepath + '\"'
        p = subprocess.Popen(
            ffcommand, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            shell=True
            )

        for line in iter(p.stdout.readline, b''):

            if 'No such file or directory' in line:
                ErrorObject().print_error(message='Validation fail: ffprobe: File not found')
                self.valid = False
                return None

            if 'Invalid data found when processing input' in line:
                ErrorObject().print_error(message='Validation fail: DATA: File is not video or is corrupt')
                self.valid = False
                return None

            if "multiple edit list entries, a/v desync might occur, patch welcome" in line:
                ErrorObject().print_error(message='Validation fail: METADATA: desync')
                self.valid = False
                return None

            if "Duration: " in line:
                """Get and Test Duration"""
                if "Duration: 00:00:00.0" in line:
                    ErrorObject().print_error(message='Validation fail: DURATION: Duration is zero')
                    self.valid = False
                    return None

                elif "Duration: N/A, " in line:
                    ErrorObject().print_error(message='Validation fail: DURATION: File is non-playable')
                    self.valid = False
                    return None

                vid_duration = line.split('Duration: ')[1].split(',')[0].strip()
                self.mezz_duration = self._seconds_from_string(duration=vid_duration)

                if self.mezz_duration < 1.05:
                    ErrorObject().print_error(message='Validation fail: DURATION: Duration is zero')
                    self.valid = False
                    return None

                ## Bitrate
                try:
                    self.mezz_bitrate = line.split('bitrate: ')[1].strip()
                except:
                    pass

            elif "Stream #" in line and 'Video: ' in line:
                codec_array = line.strip().split(',') 
                for c in codec_array:
                    ## Resolution
                    if len(c.split('x')) == 2:
                        if '[' not in c:
                            self.mezz_resolution = c.strip()
                        else:
                            self.mezz_resolution = c.strip().split(' ')[0]

        self.valid = True


class Encode():

    def __init__(self, VideoObject, profile_name):

        self.ffcommand = ''
        self.VideoObject = VideoObject
        self.profile_name = profile_name
        self.output_file = None
        self.endpoint_url = None

        ## Encode Particulars
        self.resolution = settings['encode_library'][self.profile_name]['resolution']
        self.rate_factor = settings['encode_library'][self.profile_name]['rate_factor']
        self.filetype = settings['encode_library'][self.profile_name]['filetype']
        self.encode_suffix = settings['encode_library'][self.profile_name]['encode_suffix']

        ## Pipeline Steps
        self.encoded = False
        self.valid = False
        self.delivered = False
        self.complete = False

        ## Endpoint information
        self.upload_filesize = None
        self.hash_sum = None
        self.endpoint_url = None


def main():
    pass

if __name__ == '__main__':
    sys.exit(main())


