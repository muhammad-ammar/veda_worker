
import os
import sys
import nose
import subprocess
import boto
try:
    boto.config.add_section('Boto')
except:
    pass
boto.config.set('Boto','http_socket_timeout','10') 
from boto.s3.connection import S3Connection

"""
Generate a serial transcode stream from 
a VEDA instance via Celery

"""

from global_vars import *
from reporting import ErrorObject, Output
from config import WorkerSetup
from abstractions import Video, Encode
from validate import ValidateVideo
from api_communicate import UpdateAPIStatus
from generate_encode import CommandGenerate



class VedaWorker():

    def __init__(self, **kwargs):
        """
        Init settings / 
        """
        self.settings = None
        self.workdir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'VEDA_WORKING'
            )
        self.veda_id =  kwargs.get('veda_id', None)
        self.setup = kwargs.get('setup', False)
        #---#
        self.encode_profile = kwargs.get('encode_profile', None)
        self.VideoObject = None
        #---#
        self.ffcommand = None
        self.source_file = None
        self.output_file = None
        #---#
        # Pipeline Steps
        self.encoded = False
        self.delivered = False
        self.complete = False


    def test(self):
        """
        Run tests
        """
        current_dir = os.getcwd()

        test_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'tests'
            )
        os.chdir(test_dir)
        test_bool = nose.run()

        '''Return to previous state'''
        os.chdir(current_dir)
        return test_bool
    

    def celery_run(self):
        print 'CEL TEST'


    def run(self):
        WS = WorkerSetup()
        if self.setup is True:
            WS.setup = True

        WS.run()
        self.settings = WS.settings_dict

        if self.encode_profile is None:
            ErrorObject().print_error(
                message = 'No Encode Profile Specified'
                )
            return None

        self.VideoObject = Video(
            veda_id=self.veda_id
            )
        self.VideoObject.activate()
        if self.VideoObject.valid is False:
            ErrorObject().print_error(
                message = 'Invalid Video / VEDA Data'
                )
            return None

        """
        Pipeline Steps :
          I. Intake
            Ib. Validate Mezz
          II. change status in APIs
          III. Generate Encode Command
          IV. Execute Encodes
            IVa. Validate Products
          (*)V. Deliver Encodes (sftp and others?), retrieve URLs
          (*)VI. Change Status in APIs, add URLs
          VII. Clean Directory

        """
        self._ENG_INTAKE()

        if self.VideoObject.valid is False:
            ErrorObject().print_error(
                message = 'Invalid Video / Local'
                )
            return None

        self._UPDATE_API()
        self._GENERATE_ENCODE()
        self._EXECUTE_ENCODE()
        self._VALIDATE_ENCODE()
        if self.encoded is True:
            



    def _ENG_INTAKE(self):
        """
        Copy file down from AWS S3 storage bucket
        """
        if self.VideoObject.valid is False:
            ErrorObject().print_error(
                message = 'Invalid Video'
                )
            return None

        if not os.path.exists(self.workdir):
            os.mkdir(self.workdir)

        conn = S3Connection(
            self.settings['aws_access_key'], 
            self.settings['aws_secret_key']
            )
        try:
            bucket = conn.get_bucket(self.settings['aws_storage_bucket'])

        except:
            ErrorObject().print_error(
                message = 'Invalid Storage Bucket'
                )
            return None

        self.source_file = '.'.join((
            self.VideoObject.veda_id, 
            self.VideoObject.mezz_extension
            ))
        source_key = bucket.get_key(self.source_file)

        if source_key == None:
            ErrorObject().print_error(
                message = 'S3 Intake Object NOT FOUND',
                )
            return None
        source_key.get_contents_to_filename(
            os.path.join(self.workdir, self.source_file)
            )

        if not os.path.exists(os.path.join(self.workdir, self.source_file)):
            ErrorObject().print_error(
                message = 'Engine Intake Download',
                )
            return None

        self.VideoObject.valid = ValidateVideo(
            filepath=os.path.join(self.workdir, self.source_file)
            ).valid


    def _UPDATE_API(self):

        V2 = UpdateAPIStatus(
            val_video_status=VAL_TRANSCODE_STATUS,
            veda_video_status=NODE_TRANSCODE_STATUS,
            VideoObject=self.VideoObject, 
            ).run()


    def _GENERATE_ENCODE(self):
        """
        Generate the (shell) command / Encode Object
        """
        E = Encode(
            VideoObject=self.VideoObject,
            profile_name=self.encode_profile
            )
        E.pull_data()
        if E.filetype is None: return None

        self.ffcommand = CommandGenerate(
            VideoObject = self.VideoObject,
            EncodeObject = E
            ).generate()


    def _EXECUTE_ENCODE(self):
        """
        if this is just a filepath, this should just work
        --no need to move the source--
        """
        if not os.path.exists(
            os.path.join(self.workdir, self.source_file)
            ):
            ErrorObject().print_error(
                message = 'Source File (local) NOT FOUND',
                )
            return None

        process = subprocess.Popen(
            self.ffcommand, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            shell=True, 
            universal_newlines=True
            )
        Output.status_bar(process=process)
        # to be polite
        print

        self.output_file = self.ffcommand.split('/')[-1]
        if not os.path.exists(
            os.path.join(self.workdir, self.output_file)
            ):
            ErrorObject().print_error(
                message = 'Source File (local) NOT FOUND',
                )


    def _VALIDATE_ENCODE(self):
        """
        Validate encode by matching (w/in 5 sec) encode duration,
        as well as standard validation tests
        """
        self.encoded = ValidateVideo(
            filepath=os.path.join(self.workdir, self.source_file),
            product_file=True,
            VideoObject=self.VideoObject
            ).valid


    def _DELIVER_FILE(self):
        pass

        # """
        # Run the commands, which tests for a file and returns
        # a bool and the filename
        # """
        # for E in self.AbstractionLayer.Encodes:
        #     FF = CommandExecute(
        #         ffcommand = E.ffcommand, 
        #         )
        #     E.complete = FF.activate()
        #     E.output_file = FF.output
        #     """just polite"""
        #     print('')
        #     """"""
        #     if E.complete is False:
        #         return False
        
        # self.AbstractionLayer.complete = True
        # return True

    # def complete(self):
    #     """
    #     Determine, reportback completion
    #     """
    #     TestReport(self.Pipeline.AbstractionLayer.complete, 'Complete')
    #     TestReport(self.Pipeline.AbstractionLayer.delivered, 'Delivered')

    #     if self.Pipeline.AbstractionLayer.complete is True and \
    #     self.Pipeline.AbstractionLayer.delivered is True:
    #         return True
    #     else:
    #         return False



def main():
    pass
#     #--OK
#     VW1 = VedaWorker(setup=True)
#     VW1.run()


if __name__ == '__main__':
    sys.exit(main())

