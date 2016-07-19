
import os
import sys
import requests
import shutil
import boto
from boto.s3.connection import S3Connection

"""
Pipeline ingest step
This assumes you've tested connections and are ready to go,
can either ingest from 'ingest' bucket/location, 
or static hotstore location

"""

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

from config import OVConfig
CF = OVConfig()
CF.run()
settings = CF.settings_dict

from abstractions import Video
from reporting import ErrorObject



class Ingest():
    """
    This should pull in a file to the workdir, 
    and generate a VideoObject

    """

    def __init__(self, mezz_video, localfile=False):

        self.mezz_video = mezz_video
        self.localfile = localfile
        self.VideoObject = Video(mezz_video=self.mezz_video)


    def _TRANSFORM_KEY(self, full_bucket_path):
        """
        ugly string handling for key transforms
        """
        if '/' not in full_bucket_path:
            return full_bucket_path, None

        bucket = full_bucket_path.split('/')[0]
        if full_bucket_path[-1] == '/':
            key_addendum = '/'.join(
                full_bucket_path.split('/')[1:len(full_bucket_path.split('/'))-1]
                )
        else:
            key_addendum = '/'.join(
                full_bucket_path.split('/')[1:len(full_bucket_path.split('/'))]
                )

        return bucket, key_addendum


    def run(self):
        '''
         * RUN
        '''

        """
        localfile protect
        """
        if self.localfile is True:
            self._file_asset_intake()
            return True

        """
        move file from ingest bucket to hotstore (if necessary), 
        validate videofile 
        parse metadata

        """
        conn = S3Connection(
            settings['aws_access_key'],
            settings['aws_secret_key']
            )

        if settings['aws_ingest_bucket'] is not None and len(settings['aws_ingest_bucket']) > 0:
            """
            Studio Ingest Function
            ***
            This will copy the file in as a key 
            under the edx naming convention
            e.g. '165510e0-032d-489c-8b52-53fe432ac7c3'

            """
            bucket, key_addendum = self._TRANSFORM_KEY(
                full_bucket_path=settings['aws_ingest_bucket']
                )
            print bucket
            print key_addendum
            ingest_bucket = conn.get_bucket(bucket)
            if key_addendum is not None:
                ingest_key = ingest_bucket.get_key('/'.join((key_addendum, self.mezz_video)))
            else:
                ingest_key = ingest_bucket.get_key(self.mezz_video)

            if ingest_key is None:
                raise ErrorObject().print_error(message='S3 OBJECT NOT FOUND')
                return None

            storage_bucket, key_addendum = self._TRANSFORM_KEY(
                full_bucket_path=settings['aws_storage_bucket']
                )
            if key_addendum is not None:
                ingest_key.copy(storage_bucket, '/'.join((key_addendum, self.mezz_video)))
            else:
                ingest_key.copy(storage_bucket, self.mezz_video)

            ingest_key.delete()

        """
        Prep ingest
        """
        storage_bucket, key_addendum = self._TRANSFORM_KEY(
            full_bucket_path=settings['aws_storage_bucket']
            )
        bucket = conn.get_bucket(storage_bucket)
        if key_addendum is not None:
            source_key = bucket.get_key('/'.join((key_addendum, self.mezz_video)))
        else:
            source_key = bucket.get_key(self.mezz_video)

        """
        Get avail metadata from bucket // Gen ID if none found
        """
        if settings['aws_ingest_bucket'] is not None and len(settings['aws_ingest_bucket']) > 0:
            self.VideoObject.val_id = self.mezz_video

        # --- #
        # Skipping this for now #
        # self.VideoObject.upload_token = source_key.get_metadata('course_video_upload_token')
        self.VideoObject.client_title = source_key.get_metadata('client_video_id')
        if source_key.get_metadata('course_key') is not None:
            self.VideoObject.course_url.append(source_key.get_metadata('course_key'))

        source_key.get_contents_to_filename(
            os.path.join(
                settings['workdir'], 
                self.mezz_video
                )
            )

        if not os.path.exists(os.path.join(
                settings['workdir'], 
                self.mezz_video
                )):
            return False
        return True


    def _file_asset_intake(self):
        """
        Ingest from Local directory
        self.mezz_video should be full filepath

        """
        if not os.path.exists(self.mezz_video):
            raise ErrorObject().print_error(message='LOCAL FILE NOT FOUND')
            return None

        destination_file = os.path.join(
            settings['workdir'],
            os.path.basename(self.mezz_video)
            )
        shutil.copyfile(self.mezz_video, destination_file)

        self.mezz_video = os.path.basename(self.mezz_video)

        if settings['aws_storage_bucket'] is not None:
            ## TODO : Upload Via BOTO / with multipart
            pass

        self.VideoObject.mezz_video = self.mezz_video
        self.VideoObject.client_title = self.mezz_video
        return True


def main():
    pass

if __name__ == '__main__':
    sys.exit(main())
