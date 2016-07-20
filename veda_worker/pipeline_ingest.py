
import os
import sys
import requests
import shutil
import boto
boto.config.add_section('Boto') 
boto.config.set('Boto','http_socket_timeout','10') 
from boto.s3.connection import S3Connection
"""
This is the pipeline ingest step,
should intake files dependent on the config of the node, 
which lives in the config file

** This assumes you've tested connections and are ready to go **

"""

root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root_dir)
from abstractions import Video
from reporting import ErrorObject, TestReport


# class Ingest():
#     """
#     This should pull in a file to the workdir, and generate a VideoObject

#     NOTE/TODO: 'ingest' is passed as a kwarg, 
#     but should test against config AS WELL as being a kwarg
#     """

#     def __init__(self, Settings, mezz_video, **kwargs):
#         self.Settings = Settings
#         self.mezz_video = mezz_video
#         self.ingest = kwargs.get('ingest', False)
#         self.hotstore = kwargs.get('hotstore', False)

#         '''
#          * RUN
#         '''
#         self.VideoObject = Video(
#             Settings = self.Settings
#             )

#         self.passed = False 


    def activate(self):
        """
        We'll introduce the use of 'source' to try 
        to clean up filepaths, keys, and s3 dir objects
        """

        # if self.Settings.NODE_VEDA_ATTACH is True:
            # self.VideoObject.video_id = self.mezz_video
            self.VideoObject.activate()
            source = '.'.join((self.mezz_video, self.VideoObject.mezz_extension))
            self.passed = self._s3_asset_intake(source)
        else:
            if self.Settings.S3_ASSET_STORE is True:
                source = self.mezz_video.split('/')[-1]
                self.passed = self._s3_asset_intake(source)

            else:
                self.passed = self._file_asset_intake()
            self.VideoObject.activate()

    def _s3_asset_intake(self, source):

        conn = S3Connection(
            self.Settings.S3_ACCESS_KEY_ID, 
            self.Settings.S3_SECRET_ACCESS_KEY,
            )

        if self.ingest is True:
            bucket = conn.get_bucket(self.Settings.MEZZ_INGEST_LOCATION)
        else:
            bucket = conn.get_bucket(self.Settings.MEZZ_HOTSTORE_LOCATION)
        source_key = bucket.get_key(source)

        if source_key == None: 
            raise ErrorObject(
                message = 'S3 OBJECT NOT FOUND',
                method = self,
            )
        if self.Settings.EDX_STUDIO_UPLOAD is True:
            """
            This will copy the file in as a key 
            under the edx naming convention
            e.g. '165510e0-032d-489c-8b52-53fe432ac7c3'

            """
            self.VideoObject.val_id = source_key.name
            self.VideoObject.upload_token = source_key.get_metadata('course_video_upload_token')
            self.VideoObject.client_title = source_key.get_metadata('client_video_id')
            self.VideoObject.course_url.append(source_key.get_metadata('course_key'))

        else:
            self.filename = source
        source_key.get_contents_to_filename(
            os.path.join(self.Settings.VEDA_WORK_DIR, self.filename),
                        # connect_timeout=50, read_timeout=70
            )
        if not os.path.exists(os.path.join(self.Settings.VEDA_WORK_DIR, self.filename)):
            return False

        """Clean Ingest"""
        if self.ingest is True:
            source_key.copy(MEZZ_HOTSTORE_LOCATION, source)
            source_key.delete()

        self.VideoObject.mezz_filepath = os.path.join(
            self.Settings.VEDA_WORK_DIR, 
            source_key.name.split('/')[-1]
            )
        return True


    def _file_asset_intake(self):
        """
        Ingest from Local directory
        ** errors with config handled earlier

        """
        if self.hotstore is False:
            if not os.path.exists(self.mezz_video):
                raise ErrorObject(
                    message = 'LOCAL FILE NOT FOUND',
                    method = self,
                )
                return False

        file = self.mezz_video.split('/')[-1]

        if not os.path.exists(os.path.join(self.Settings.VEDA_WORK_DIR, file)):
            if self.ingest is False and self.hotstore is True:
                shutil.copyfile(
                    os.path.join(self.Settings.MEZZ_HOTSTORE_LOCATION, file), 
                    os.path.join(self.Settings.VEDA_WORK_DIR, file)
                    )
            if self.ingest is False and self.hotstore is False:
                shutil.copyfile(
                    self.mezz_video, 
                    os.path.join(self.Settings.VEDA_WORK_DIR, file)
                    )

            if self.ingest is True:
                shutil.copyfile(
                    os.path.join(self.Settings.MEZZ_INGEST_LOCATION, file), 
                    os.path.join(self.Settings.MEZZ_HOTSTORE_LOCATION, file), 
                    )
                shutil.copyfile(
                    os.path.join(self.Settings.MEZZ_INGEST_LOCATION, file),                 
                    os.path.join(self.Settings.VEDA_WORK_DIR, file)
                    )

                os.remove(os.path.join(self.Settings.MEZZ_INGEST_LOCATION, file))

        self.VideoObject.mezz_title = file
        self.VideoObject.mezz_filepath = os.path.join(self.Settings.VEDA_WORK_DIR, file)
        self.VideoObject.activate()

        if self.VideoObject == None: 
            return False
        return True


def main():
    pass

if __name__ == '__main__':
    sys.exit(main())





















