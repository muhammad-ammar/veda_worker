
import os
import sys
# import argparse
import nose
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

from reporting import ErrorObject, Output
from config import WorkerSetup
from abstractions import Video
from validate import ValidateVideo
# from pipeline import Pipeline


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

        source_file = '.'.join((
            self.VideoObject.veda_id, 
            self.VideoObject.mezz_extension
            ))
        source_key = bucket.get_key(source_file)

        if source_key == None:
            ErrorObject().print_error(
                message = 'S3 Intake Object NOT FOUND',
                )
            return None
        source_key.get_contents_to_filename(
            os.path.join(self.workdir, source_file)
            )

        if not os.path.exists(os.path.join(self.workdir, source_file)):
            ErrorObject().print_error(
                message = 'Engine Intake Download',
                )
            return None

        self.VideoObject.valid = ValidateVideo(
            filepath=os.path.join(self.workdir, source_file)
            ).valid

    #     if self.Settings.NODE_VEDA_ATTACH is True:
    #         """
    #         For a node attached instance
    #         """
    #         self.Pipeline = Pipeline(
    #             Settings=self.Settings,
    #             mezz_video=self.mezz_video,
    #             encode_profile=self.encode_profile
    #             )
    #         self.Pipeline.activate()
    #         return None
    #     else:
    #         """
    #         Single stream
    #         """
    #         self.Pipeline = Pipeline(
    #             Settings=self.Settings,
    #             mezz_video=self.mezz_video
    #             )
    #         self.Pipeline.activate()
    #         return None


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



# def main():
#     #--OK
#     VW1 = VedaWorker(setup=True)
#     VW1.run()


if __name__ == '__main__':
    sys.exit(main())

