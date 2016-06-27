
import os
import sys
import json
import yaml

"""
This will read a default yaml file and output to a instance-specific file, 
to be read by processes as needed

"""

"""
Get Default encodes from master dir
"""

"""
set up environment

"""

"""
Configure VDC instance, or read config'd settings into class

"""
setup_list = {
    # Storage
    'STORAGE: bucket name' : 'aws_storage_bucket',
    'STORAGE: Access key' : 'aws_access_key',
    'STORAGE: Secret key' : 'aws_secret_key',
    # Ingest
    'INGEST: bucket name' : 'aws_ingest_bucket',
    # Delivery
    'DELIVERY: Bucket Name' : 'aws_deliver_bucket',
    'DELIVERY: Access Key' : 'aws_deliver_access_key',
    'DELIVERY: Secret Key' : 'aws_deliver_secret_key',
    # VAL
    'VAL: Token URL' : 'val_token_url',
    'VAL: API URL' : 'val_api_url',
    'VAL: Username' : 'val_username',
    'VAL: Pass' : 'val_password',
    'VAL: Client ID' : 'val_client_id',
    'VAL: Secret Key' : 'val_secret_key',
    # VEDA
    'VEDA: Auth URL' : 'veda_auth_url',
    'VEDA: Token URL' : 'veda_token_url',
    'VEDA: API URL' : 'veda_api_url',
    'VEDA: Client ID' : 'veda_client_id',
    'VEDA: Secret Key' : 'veda_secret_key'
}



class OVConfig():

    def __init__(self, configure=False): #, **kwargs):
        """
        Attempt to open and read yaml file

        """
        self.configure = configure

        ## Defaults
        self.default_yaml = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'default_config.yaml'
            )
        self.settings_yaml = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'instance_config.yaml'
            )
        self.settings_dict = {}
        self.encode_library = None

        """
        Run
        """
        if self.configure is True:
            self._CONFIGURE()
        else:
            self._READ_SETTINGS()


    def _READ_SETTINGS(self):
        """
        Read Extant Settings or Generate New Ones
        """
        if not os.path.exists(self.settings_yaml):
            # ## TODO: ERROR MESSAGES
            # print '[ ERROR ] : Not Configured'
            return None

        with open(self.settings_yaml, 'r') as stream:
            try:
                self.settings_dict = yaml.load(stream)
                if len(self.settings_dict['workdir']) == 0:
                    self.settings_dict['workdir'] = os.path.join(
                        os.getcwd(), 
                        'VEDA_WORKING'
                        )

            except yaml.YAMLError as exc:
                ## TODO: ERROR MESSAGES
                print '[ ERROR ] : YAML config'
                return None


    def _CONFIGURE(self):
        """
        Prompt user for settings as needed for yaml
        """
        with open(self.default_yaml, 'r') as stream:
            try:
                config_dict = yaml.load(stream)
            except yaml.YAMLError as exc:
                ## TODO: ERROR MESSAGES
                print '[ ERROR ] : YAML defaults'
                return None

        self.settings_dict = config_dict

        for j, k in setup_list.iteritems():
            sys.stdout.write('\r')
            sys.stdout.write('%s : \n' % (j))
            new_value = raw_input('%s :' % (k))
            if new_value == None:
                new_value = ''
            self.settings_dict[k] = new_value
            sys.stdout.flush()

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
                os.path.dirname(os.path.dirname(__file__)), 
                'default_encode_profiles.json'
                )
        with open(self.encode_library) as data_file:
            data = json.load(data_file)
            return data["ENCODE_PROFILES"]



    # # def __init__(self, node_config=None, **kwargs):
    #     """
    #     A Master setup, which will override all defaults set here
    #     """
    #     # self.node_config = node_config
    #     # self.encode_library = kwargs.get('encode_library', None)

    #     """
    #     If we want this to be prettier
    #     though, this seems dangerous
    #     """
    #     # for key, value in kwargs.items():
    #     #     setattr(self, key, value)

    #     """
    #     kwargs
    #     """
    #     self.VAL_ATTACH = kwargs.get('VAL_ATTACH', False)
    #     self.VAL_TOKEN_URL = kwargs.get('VAL_TOKEN_URL', '')
    #     self.VAL_API_URL = kwargs.get('VAL_API_URL', '')
    #     self.NODE_LOGGING = kwargs.get('NODE_LOGGING', False)
    #     self.NODE_STDIO = kwargs.get('NODE_STDIO', True)
    #     self.EDX_STUDIO_UPLOAD = kwargs.get('EDX_STUDIO_UPLOAD', False)
    #     # self.VEDA_WORK_DIR = kwargs.get(
    #     #     'VEDA_WORK_DIR',
    #     #     os.path.join(os.getcwd(), 'VEDA_WORKING')
    #     #     )
        # """
        # VEDA INFORMATION
        # """
        # self.NODE_VEDA_ATTACH = kwargs.get('NODE_VEDA_ATTACH', False)
        # self.VEDA_TOKEN_URL = kwargs.get('VEDA_TOKEN_URL', '')
        # self.VEDA_AUTH_URL = kwargs.get('VEDA_AUTH_URL', '')
        # self.VEDA_API_URL = kwargs.get('VEDA_API_URL', '')
        # self.CELERY_APP_NAME = kwargs.get('CELERY_APP_NAME', '')
        # self.CELERY_QUEUE = kwargs.get('CELERY_QUEUE', [])
        # """
        # STORAGE INFORMATION
        # """
        # self.S3_ASSET_STORE = kwargs.get('S3_ASSET_STORE', False)
        # self.MEZZ_HOTSTORE_LOCATION = kwargs.get('MEZZ_HOTSTORE_LOCATION', '')
        # self.MEZZ_INGEST_LOCATION = kwargs.get('MEZZ_INGEST_LOCATION', '')
        # self.S3_DELIVER = kwargs.get('S3_DELIVER', False)
        # self.DELIVERY_ENDPOINT = kwargs.get('DELIVERY_ENDPOINT', '')
        # self.SSL_ENDPOINT = kwargs.get('SSL_ENDPOINT', False)
        # """
        # DEFAULTS 
        # """
        # self.FFMPEG_COMPILED = kwargs.get('FFMPEG_COMPILED', 'ffmpeg')
        # self.FFPROBE_COMPILED = kwargs.get('FFMPEG_COMPILED', 'ffprobe')

        # self.TARGET_ASPECT_RATIO = float(1920) / float(1080)
        # self.ENFORCE_TARGET_ASPECT = True
        # self.MULTI_UPLOAD_BARRIER = 2000000000

        # self.TEST_VIDEO_DIR = os.path.join(os.path.dirname(__file__), 'VEDA_TESTFILES')
        # self.TEST_VIDEO_FILE = 'OVTESTFILE_01.mp4'
        # self.TEST_VIDEO_ID = 'XXXXXXXX2016-V00TEST'
        # self.TEST_ENCODE_PROFILE = 'desktop_mp4'
        # self.TEST_VAL_ID = '760ba4421d'

        # self.NODE_COLORS_BLUE = '\033[94m'
        # self.NODE_COLORS_GREEN = '\033[92m'
        # self.NODE_COLORS_RED = '\033[91m'
        # self.NODE_COLORS_END = '\033[0m'

        # """
        # Connection Secrets 
        # """
        # """
        # VAL 
        # """
        # self.VAL_CLIENT_ID = kwargs.get('VAL_CLIENT_ID', '')
        # self.VAL_CLIENT_SECRET = kwargs.get('VAL_CLIENT_SECRET', '')
        # self.VAL_USERNAME = kwargs.get('VAL_USERNAME', '')
        # self.VAL_USERPASS = kwargs.get('VAL_USERPASS', '')
        # """
        # s3 Access info
        # """
        # self.S3_ACCESS_KEY_ID = kwargs.get('S3_ACCESS_KEY_ID', '')
        # self.S3_SECRET_ACCESS_KEY = kwargs.get('S3_SECRET_ACCESS_KEY', '')
        # """
        # Delivery Information
        # """
        # self.DELIVERY_ID = kwargs.get('DELIVERY_ID', '')
        # self.DELIVERY_PASS = kwargs.get('DELIVERY_PASS', '')
        # """
        # NODE INFORMATION
        # """
        # self.VEDA_API_CLIENTID = kwargs.get('VEDA_API_CLIENTID', '')
        # self.VEDA_API_CLIENTSECRET = kwargs.get('VEDA_API_CLIENTSECRET', '')
        # """
        # Cluster information
        # """
        # self.RABBIT_USER = kwargs.get('RABBIT_USER', '')
        # self.RABBIT_PASS = kwargs.get('RABBIT_PASS', '')
        # self.RABBIT_BROKER = kwargs.get('RABBIT_BROKER', '')

        # if len(self.DELIVERY_ID) == 0:
        #     self.DELIVERY_ID = self.S3_ACCESS_KEY_ID
        #     self.DELIVERY_PASS = self.S3_SECRET_ACCESS_KEY




    # def activate(self):
    #     """
    #     Iterate through defined classes and redo if config file specified
    #     """
    #     if self.node_config != None:
    #         sys.path.append(os.path.dirname(self.node_config))
    #         config_file = os.path.basename(self.node_config).split('.')[0]
    #         for d in self.__dict__.keys():
    #             """graceful fail if variables are unset"""
    #             try:
    #                 setattr(self, d, getattr(__import__(config_file, fromlist=[d]), d))
    #             except:
    #                 pass



    # def setup(self):
    #     pass


def main():
    """
    For example
    """
    V = OVConfig()


if __name__ == '__main__':
    sys.exit(main())











