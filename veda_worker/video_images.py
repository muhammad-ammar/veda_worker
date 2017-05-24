"""
Generate 3 images for a course video.
"""

import json
import os
from os.path import expanduser
import subprocess
from uuid import uuid4

from boto.exception import S3ResponseError
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import requests

import generate_apitoken
from veda_worker.reporting import ErrorObject, Output
from veda_worker.config import WorkerSetup


WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()

SETTINGS = WS.settings_dict
HOME_DIR = expanduser("~")
IMAGE_COUNT = 3


class VideoImages(object):
    """
    Video Images related functionality.
    """

    def __init__(self, video_object, work_dir, source_file, **kwargs):
        self.video_object = video_object
        self.work_dir = work_dir
        self.source_file = source_file
        self.source_video_file = os.path.join(self.work_dir, self.source_file)
        self.jobid = kwargs.get('jobid', None)

    def create_and_update(self):
        """
        Creat images and update S3 and edxval
        """
        generated_images = self.generate()
        image_keys = self.upload(generated_images)
        self.update_val(image_keys)

    def generate(self):
        """
        Generate video images using ffmpeg.
        """
        if self.video_object is None:
            ErrorObject().print_error(
                message='Video Images generation failed: No Video Object'
            )
            return None

        # We need to generate images from different positions
        # starting from 5 second. We choose 5 to skip initial
        # credits shown in video.
        step = self.video_object.mezz_duration/IMAGE_COUNT
        positions = [5 + i * step for i in range(IMAGE_COUNT)]
        generated_images = []

        for position in positions:
            generated_images.append(
                os.path.join(self.work_dir, '{}.png'.format(uuid4().hex))
            )
            command = '{ffmpeg} -ss {position} -i {video_file} -vf ' \
                     r'select="eq(pict_type\,PICT_TYPE_I)*gt(scene\,0.4)"' \
                      ',scale=1280:720 -vsync vfr -vframes 1 {output_file}' \
                      ' -hide_banner -y'.format(
                          ffmpeg=SETTINGS['ffmpeg_compiled'],
                          position=position,
                          video_file=self.source_video_file,
                          output_file=generated_images[-1])

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                universal_newlines=True
            )
            print 'executing command >> {}'.format(command)
            Output.status_bar(process=process)

        return generated_images


    def upload(self, generated_images):
        """
        Upload auto generated images to S3.
        """
        s3_connection = S3Connection(
            SETTINGS['aws_video_images_access_key'],
            SETTINGS['aws_video_images_secret_key']
        )

        try:
            bucket = s3_connection.get_bucket(SETTINGS['aws_video_images_bucket'])
        except S3ResponseError:
            ErrorObject().print_error(
                message='Invalid Storage Bucket for Video Images'
            )
            return None

        image_keys = []
        for generated_image in generated_images:
            upload_key = Key(bucket)
            upload_key.key = '{prefix}/{generated_image}'.format(
                prefix=SETTINGS['aws_video_images_prefix'] if SETTINGS['aws_video_images_prefix'] is not None else '',
                generated_image=os.path.basename(generated_image)
            )
            image_keys.append(upload_key.key)
            upload_key.set_contents_from_filename(generated_image)

        return image_keys

    def update_val(self, image_keys):
        """
        Update a course video in edxval database for auto generated images.
        """
        data = {
            'course_id': self.video_object.course_url,
            'generated_images': image_keys
        }

        val_headers = {
            'Authorization': 'Bearer ' + generate_apitoken.val_tokengen(),
            'content-type': 'application/json'
        }

        response = requests.post(
            SETTINGS['val_video_images_url'],
            data=json.dumps(data),
            headers=val_headers,
            timeout=20
        )

        if not response.ok:
            ErrorObject.print_error(message=response.content)
