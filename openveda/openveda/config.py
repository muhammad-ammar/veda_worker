
import os
import sys
import json
import yaml
import getpass
import boto

"""
Configure VDC instance, or read config'd settings into class

This will read a default yaml file and output to a instance-specific file, 
to be read by processes as needed

"""
from reporting import ErrorObject
from global_vars import *

class OVConfig():

    def __init__(self, configure=False, **kwargs):

        """
        Attempt to open and read yaml file

        """
        self.configure = configure

        self.settings_yaml = kwargs.get(
            'settings_yaml', 
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                'instance_config.yaml'
                )
            )

        self.settings_dict = {}
        self.encode_library = None

        '''for nose'''
        self.test = kwargs.get('test', False)
        self.testvar = kwargs.get('testvar', None)

        """
        Run
        """

    def run(self):
        if self.configure is True and self.test is False:
            self._CONFIGURE()
        if self.test is True:
            self._MONKEYPATCH()
        if self.configure is False and self.test is False:
            self._READ_SETTINGS()
            self._PREP_ENVIRON()


    def _PREP_ENVIRON(self):
        """
        Do the necessaries
        """
        try:
            self.settings_dict['workdir']
        except:
            return None

        if not os.path.exists(self.settings_dict['workdir']):
            os.mkdir(self.settings_dict['workdir'])

        """
        BOTO Config
        """
        try:
            boto.config.add_section('Boto') 
        except:
            pass
        boto.config.set(
            'Boto','http_socket_timeout',
            str(BOTO_TIMEOUT)
            ) 


    def _READ_SETTINGS(self):
        """
        Read Extant Settings or Generate New Ones
        """

        if not os.path.exists(self.settings_yaml) and self.test is True:
            self.settings_yaml = DEFAULT_YAML

        if not os.path.exists(self.settings_yaml):
            return None

        with open(self.settings_yaml, 'r') as stream:
            try:
                self.settings_dict = yaml.load(stream)
            except yaml.YAMLError as exc:
                raise ErrorObject().print_error(
                    message='Invalid Config YAML'
                    )

        if self.settings_dict['workdir'] is None or \
        len(self.settings_dict['workdir']) == 0:
            self.settings_dict['workdir'] = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                'VEDA_WORKING'
                )
        self.settings_dict['encode_library'] = self._READ_ENCODES()

        if not os.path.exists(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'ffmpeg_binary.yaml'
            )):
            self.settings_dict['ffmpeg'] = 'ffmpeg'
            self.settings_dict['ffprobe'] = 'ffprobe'

        else:
            with open(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'ffmpeg_binary.yaml'
            ), 'r') as stream:
                ffdict = yaml.load(stream)
            self.settings_dict['ffmpeg'] = ffdict['ffmpeg']
            self.settings_dict['ffprobe'] = ffdict['ffprobe']


    def _MONKEYPATCH(self):
        config_list = ['testvar']
        for c in config_list:
            self.settings_dict[c] = self.testvar

        '''Protection'''
        self.settings_dict['workdir'] = ''
        with open(self.settings_yaml, 'w') as outfile:
            outfile.write(
                yaml.dump(
                    self.settings_dict, 
                    default_flow_style=False
                    )
                )
        self._READ_SETTINGS()


    def _CONFIGURE(self):

        config_list = [
            'workdir',
            'aws_storage_bucket',
            'aws_deliver_bucket',
            'aws_ingest_bucket',
            'aws_access_key',
            'aws_secret_key',
            'val_token_url',
            'val_api_url',
            'val_username',
            'val_password',
            'val_client_id',
            'val_secret_key',
        ]

        ov_setup_walkthrough = {
            'workdir' : 'VEDA Working Directory [defaults to repo dir]',
            'aws_storage_bucket': 'AWS S3 Storage Bucket Name: ',
            'aws_deliver_bucket': 'AWS S3 Deliver Bucket Name: ',
            'aws_access_key': 'AWS S3 Access key: ',
            'aws_secret_key': 'P AWS S3 Secret key: ',
            'aws_ingest_bucket': 'Studio Ingest Bucket Name [optional]: ',
            'val_token_url' : 'VAL Token URL [optional]: ',
            'val_api_url' : 'VAL API URL: ',
            'val_username' : 'VAL Username: ',
            'val_password' : 'P VAL Password: ',
            'val_client_id' : 'VAL Client ID: ',
            'val_secret_key' : 'P VAL Secret Key: ',
            }


        def _input_pretty(parameter):
            """
            Just to make this more polite
            """
            if 'P ' in ov_setup_walkthrough[c]:
                print '--Input Hidden--'
                new_value = getpass.getpass(
                    ov_setup_walkthrough[c].replace('P ', '')
                    )
            else:
                new_value = raw_input(ov_setup_walkthrough[c])
            return new_value


        val = None
        for c in config_list:
            if 'val' not in c:
                param = _input_pretty(parameter=c)

            elif c == 'val_token_url':
                param = _input_pretty(parameter=c)
                if param is None or len(param) == 0:
                    val = False
                    param = None
            else:
                if val is not False:
                    param = _input_pretty(parameter=c)
                else:
                    param = None

            self.settings_dict[c] = param

        with open(self.settings_yaml, 'w') as outfile:
            outfile.write(
                yaml.dump(
                    self.settings_dict, 
                    default_flow_style=False
                    )
                )
        self._READ_SETTINGS()
        self.ENCODE_PROFILES = self._READ_ENCODES()


    def _READ_ENCODES(self):
        if self.encode_library == None:
            self.encode_library = os.path.join(
                os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__))
                ), 
                'default_encode_profiles.json'
                )

        with open(self.encode_library) as data_file:
            data = json.load(data_file)
            return data["ENCODE_PROFILES"]


def main():
    """
    For example
    """
    V = OVConfig(settings_yaml=DEFAULT_YAML)
    V.run()


if __name__ == '__main__':
    sys.exit(main())











