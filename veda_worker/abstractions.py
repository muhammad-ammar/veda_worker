
import os
import subprocess
import requests
import ast
import json
import uuid

"""Disable insecure warning for requests lib"""
requests.packages.urllib3.disable_warnings()

"""
Abstractions / A simple way for openVEDA to remember!

AbstractionLayer Object (acts as master abstraction)
    -Video Object
    -[ EncodeObject, EncodeObject ]

"""
from reporting import ErrorObject, Output
import generate_apitoken 
from config import WorkerSetup

WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict



# class AbstractionLayer():
#     """
#     A simple object to hold states in openVEDA
#     for basic reporting/logging and tracking of long running
#     processes
#     """
#     def __init__(self):
#         self.VideoObject = None
#         self.Encodes = []
#         self.valid = False
#         self.complete = False
#         self.delivered = False


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
        Generated Token
        """
        veda_token = generate_apitoken.veda_tokengen()
        if veda_token == None: return None

        data = {
            'edx_id' : self.veda_id,
            }
        headers = {
            'Authorization': 'Bearer ' + veda_token, 
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


        # return self




        # self.Settings = Settings
        # self.mezz_title = mezz_title
        # self.mezz_filepath = mezz_filepath
        # self.mezz_bitrate = None
        # self.mezz_resolution = None
        # self.mezz_extension = None
        # self.mezz_filesize = None 
        # self.mezz_duration = None
        # self.mezz_active = True
        # self.class_id = None
        #
        # self.val_id = kwargs.get('val_id', None)
        # self.course_url = kwargs.get('course_url', [])

        # self.valid = True

    # def _seconds_from_string(self, duration):
        # hours = float(duration.split(':')[0])
        # minutes = float(duration.split(':')[1])
        # seconds = float(duration.split(':')[2])
        # duration_seconds = (((hours * 60) + minutes) * 60) + seconds
        # return duration_seconds

    # def activate(self):
        # if self.video_id == None and self.mezz_filepath != None:
            # self = self.file_determiner()
            # 
        # elif self.video_id != None and self.Settings.NODE_VEDA_ATTACH is True:
            # self = self.api_determiner()

        # self = self.id_determiner()
        # return self

    # def id_determiner(self):
        # """
        # This is done quickly to pass tests, but does not cover studio upload ingest
        # """
        # if self.val_id == None or len(self.val_id) == 0:
            # if self.video_id == None:
                # """
                # Local File, no ingest, gen uuid
                # """
                # self.mezz_title = self.mezz_filepath.split('/')[-1]
                ## Generate random hash
                # self.val_id =  uuid.uuid1().hex[0:10]
            # else:
                # """
                # VEDA File
                # """
                # self.val_id =  self.video_id
                

    # def file_determiner(self):
    #     """
    #     This is to intake a file sitting in the watch folder, with no metadata
    #     """
    #     file = self.mezz_filepath.split('/')[-1]
    #     if '.' in file:
    #         self.mezz_extension = file.split('.')[-1]
    #     else:
    #         self.mezz_extension = None

    #     ## Get filesize for nodal assignment if clustered
    #     if self.mezz_filesize is None:
    #         if 'http' not in self.mezz_filepath:
    #             self.mezz_filesize = os.stat(self.mezz_filepath).st_size
    #         else:
    #             f = requests.head(self.mezz_filepath)
    
    #             if f.status_code > 399: return None
    #             header_dict = ast.literal_eval(str(f.headers))
    #             try:
    #                 self.mezz_filesize = header_dict['content-length']
    #             except:
    #                 ## protect for AWS headers
    #                 try:
    #                     self.mezz_filesize = header_dict['Content-Length']
    #                 except:
    #                     self.mezz_filesize = None

    #     """
    #     This is a little bit ugly, and for that I am sorry
    #     HOWEVER, it is functional with ffprobe 2.3.3
    #     """
    #     ffcommand = 'ffprobe -hide_banner '
    #     if 'http' in self.mezz_filepath:  
    #         ffcommand += '-print_format json '

    #     seek_path = self.mezz_filepath.replace('https://', 'http://')
    #     ffcommand += '\"' + seek_path + '\"'

    #     p = subprocess.Popen(ffcommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    #     for line in iter(p.stdout.readline, b''):
    #         if "Duration: " in line:
    #             ## Duration
    #             vid_duration = line.split('Duration: ')[1].split(',')[0].strip()
    #             self.mezz_duration = self._seconds_from_string(duration=vid_duration)
    #             ## Bitrate
    #             try:
    #                 self.mezz_bitrate = line.split('bitrate: ')[1].strip()
    #             except:
    #                 pass
    #         elif "Stream #" in line and 'Video: ' in line:
    #             codec_array = line.strip().split(',') 
    #             for c in codec_array:
    #                 ## Resolution
    #                 if len(c.split('x')) == 2:
    #                     if '[' not in c:
    #                         self.mezz_resolution = c.strip()
    #                     else:
    #                         self.mezz_resolution = c.strip().split(' ')[0]
    #     return self

    # def api_determiner(self):



class Encode():
    """
    A basic class for easy programatic access to the diff salient variables
    """
    def __init__(self, Settings, VideoObject, profile_name):
        self.Settings = Settings
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

        self.complete = False
        self.delivered = False

    def activate(self):
        if self.Settings.NODE_VEDA_ATTACH is False:
            self.resolution = self.Settings.NODE_ENCODE_PROFILES[self.profile_name]['resolution']
            self.rate_factor = self.Settings.NODE_ENCODE_PROFILES[self.profile_name]['rate_factor']
            self.filetype = self.Settings.NODE_ENCODE_PROFILES[self.profile_name]['filetype']
            self.encode_suffix = self.Settings.NODE_ENCODE_PROFILES[self.profile_name]['encode_suffix']

        else:
            encode_dict = {}
            import generate_apitoken
            veda_token = generate_apitoken.veda_tokengen(Settings=self.Settings)

            if veda_token == None: return None

            data = {}
            headers = {'Authorization': 'Bearer ' + veda_token, 'content-type': 'application/json'}
            x = requests.get(self.Settings.VEDA_API_URL + 'encodes', params=data, headers=headers) 
            enc_dict = json.loads(x.text)   

            if len(enc_dict['results']) == 0: return None

            for e in enc_dict['results']:
                if e['product_spec'] == self.profile_name and e['profile_active'] is True:
                    self.resolution = e['encode_resolution']
                    self.rate_factor = e['encode_bitdepth']
                    self.filetype = e['encode_filetype']
                    self.encode_suffix = e['encode_suffix']
                    self.encode_pk = e['id']
        
        if self.encode_suffix == None: return None
        return self


def main():
    pass

if __name__ == '__main__':
    sys.exit(main())


