"""
Generate a serial transcode stream from
a VEDA instance via Celery

"""

import os
import sys
import nose
import subprocess
import shutil
import boto

from boto.s3.connection import S3Connection
from vhls import VHLS
from os.path import expanduser

homedir = expanduser("~")
try:
    boto.config.add_section('Boto')
except:
    pass
boto.config.set('Boto','http_socket_timeout','10')

import celeryapp
from global_vars import *
from reporting import ErrorObject, Output
from config import WorkerSetup
from abstractions import Video, Encode
from validate import ValidateVideo
from api_communicate import UpdateAPIStatus
from generate_encode import CommandGenerate
from generate_delivery import Deliverable


class VedaWorker():

    def __init__(self, **kwargs):
        """
        Init settings / 
        """
        self.settings = None
        self.veda_id =  kwargs.get('veda_id', None)
        self.setup = kwargs.get('setup', False)
        self.jobid = kwargs.get('jobid', None)
        """#---#"""
        self.encode_profile = kwargs.get('encode_profile', None)
        self.VideoObject = None

        """
        Yucky working directory stuff
        """
        if self.jobid is None:
            self.workdir = os.path.join(
                homedir,
                'ENCODE_WORKDIR'
                )
        else:
            self.workdir = os.path.join(
                homedir,
                'ENCODE_WORKDIR',
                self.jobid
                )

        if not os.path.exists(os.path.join(
                homedir,
                'ENCODE_WORKDIR'
                )):
            os.mkdir(os.path.join(
                homedir,
                'ENCODE_WORKDIR'
                ))

        """#---#"""
        self.ffcommand = None
        self.source_file = None
        self.output_file = None
        self.endpoint_url = None

        """Pipeline Steps"""
        self.encoded = False
        self.delivered = False


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

        if not os.path.exists(self.workdir):
            os.mkdir(self.workdir)


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

        if self.encode_profile == 'hls':
            self._HLSPipeline()
        else:
            self._StaticPipeline()

        print self.endpoint_url

        if self.endpoint_url is not None:
            """
            Integrate with main
            """
            veda_id = self.veda_id
            encode_profile = self.encode_profile
            celeryapp.deliverable_route.apply_async(
                (veda_id, encode_profile),
                queue='transcode_stat'
                )
        """
        Clean up workdir
        """
        if self.jobid is not None:
            shutil.rmtree(
                self.workdir
                )


    def _StaticPipeline(self):
        self._GENERATE_ENCODE()
        if self.ffcommand is None:
            print 'No Command'
            return None

        self._EXECUTE_ENCODE()
        self._VALIDATE_ENCODE()
        if self.encoded is True:
            self._DELIVER_FILE()


    def _HLSPipeline(self):
        """
        Activate HLS, use hls lib to upload

        """
        if not os.path.exists(os.path.join(self.workdir, self.source_file)):
            ErrorObject().print_error(
                message = 'Source File (local) NOT FOUND',
                )
            return None
        os.chdir(self.workdir)

        V1 = VHLS(
            mezz_file=os.path.join(self.workdir, self.source_file),
            DELIVER_BUCKET=self.settings['edx_s3_endpoint_bucket'],
            ACCESS_KEY_ID=self.settings['edx_access_key_id'],
            SECRET_ACCESS_KEY = self.settings['edx_secret_access_key']
        )

        if V1.complete is True:
            self.endpoint_url = V1.manifest_url
        else:
            return None


    def _ENG_INTAKE(self):
        """
        Copy file down from AWS S3 storage bucket
        """
        if self.VideoObject.valid is False:
            ErrorObject().print_error(
                message = 'Invalid Video'
                )

            return None


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

        """
        Implement HLS Here

        """

        self.ffcommand = CommandGenerate(
            VideoObject = self.VideoObject,
            EncodeObject = E,
            jobid=self.jobid
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
        print '%s : %s' % (self.VideoObject.veda_id, self.encode_profile)
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
            filepath=os.path.join(self.workdir, self.output_file),
            product_file=True,
            VideoObject=self.VideoObject
            ).valid


    def _DELIVER_FILE(self):
        """
        Deliver Here // FOR NOW: go to the 
        """
        if not os.path.exists(
            os.path.join(self.workdir, self.output_file)
            ):
            return None

        D1 = Deliverable(
            VideoObject=self.VideoObject,
            encode_profile=self.encode_profile,
            output_file=self.output_file,
            jobid=self.jobid
            )
        D1.run()
        self.delivered = D1.delivered
        self.endpoint_url = D1.endpoint_url


def main():
    pass


if __name__ == '__main__':
    sys.exit(main())
