
import os
import sys
import boto
import boto.s3
from boto.s3.key import Key
import shutil
import hashlib

from os.path import expanduser
homedir = expanduser("~")

"""
Gets specified Video and Encode object, and delivers file to endpoint
from VEDA_WORK_DIR, retrieves and checks URL, and passes info to objects

"""

from global_vars import *
from reporting import ErrorObject
from config import WorkerSetup

WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict



class Deliverable():

    def __init__(self, VideoObject, encode_profile, output_file, **kwargs):
        self.VideoObject = VideoObject
        self.encode_profile = encode_profile
        self.output_file = output_file
        self.jobid = kwargs.get('jobid', None)
        if self.jobid is None:
            self.workdir = os.path.join(
                homedir,
                'VEDA_WORKING'
                )
        else:
            self.workdir = os.path.join(
                homedir,
                'VEDA_WORKING',
                self.jobid
                )
        #---#
        self.endpoint_url = None
        self.hash_sum = 0
        self.upload_filesize = 0
        self.delivered = False


    def run(self):
        """
        Get file particulars, upload to s3
        """
        # file size
        self.upload_filesize = os.stat(
            os.path.join(self.workdir, self.output_file)
            ).st_size
        # hash sum
        self.hash_sum = hashlib.md5(
            open(
                os.path.join(
                    self.workdir, 
                    self.output_file
                    ), 'rb').read()
            ).hexdigest()

        if self.upload_filesize < MULTI_UPLOAD_BARRIER:
            """
            Upload single part
            """
            self.delivered = self._s3_upload()
        else:
            """
            Upload multipart
            """
            self.delivered = self._boto_multipart()

        if self.delivered is False:
            return None

        self.endpoint_url = '/'.join((
            'https://s3.amazonaws.com',
                settings['aws_deliver_bucket'], 
                self.output_file
                ))
        return True


    def _s3_upload(self):
        """
        Upload single part (under threshold in node_config)
        node_config MULTI_UPLOAD_BARRIER
        """
        try:
            conn = boto.connect_s3(
                settings['aws_deliver_access_key'],
                settings['aws_deliver_secret_key']
                )
            delv_bucket = conn.get_bucket(settings['aws_deliver_bucket'])

        except:
            ErrorObject().print_error(
                message = 'Deliverable Fail: s3 Connection Error - Singleton'
                )
            return False

        upload_key = Key(delv_bucket)
        upload_key.key = self.output_file
        upload_key.set_contents_from_filename(
            os.path.join(self.workdir, self.output_file)
            )
        return True


    def _boto_multipart(self):
        """
        Split file into chunks, upload chunks

        NOTE: this should never happen, as your files should be much
        smaller than this, but one never knows
        """
        if not os.path.exists(
            os.path.join(
                self.workdir, 
                self.output_file.split('.')[0]
                )
            ):
            os.mkdir(os.path.join(
                self.workdir, 
                self.output_file.split('.')[0]
                ))

        os.chdir(
            os.path.join(self.workdir, self.output_file.split('.')[0])
            )
        """
        Split File into chunks
        """ 
        split_command = 'split -b10m -a5' ##5 part names of 5mb
        sys.stdout.write('%s : %s\n' % (self.output_file, 'Generating Multipart'))
        os.system(' '.join((split_command, os.path.join(self.workdir, self.output_file))))
        sys.stdout.flush()

        """
        Connect to s3
        """
        try:
            c = boto.connect_s3(
                settings['aws_deliver_access_key'],
                settings['aws_deliver_secret_key']
                )
            b = c.lookup(settings['aws_deliver_bucket'])
        except:
            ErrorObject().print_error(
                message = 'Deliverable Fail: s3 Connection Error - Multipart'
                )
            return False

        if b == None:
            ErrorObject().print_error(
                message = 'Deliverable Fail: s3 Bucket Connection Error'
                )
            return False

        """
        Upload and stitch parts
        """
        mp = b.initiate_multipart_upload(self.output_file)

        x = 1
        for file in sorted(os.listdir(
            os.path.join(
                self.workdir, 
                self.output_file.split('.')[0]
                )
            )):
            sys.stdout.write('%s : %s\r' % (file, 'uploading part'))
            fp = open(file, 'rb')
            mp.upload_part_from_file(fp, x)
            fp.close()
            sys.stdout.flush()            
            x += 1
        sys.stdout.write('\n')
        mp.complete_upload()
        """Clean up multipart"""
        shutil.rmtree(os.path.join(self.workdir, self.output_file.split('.')[0]))
        return True



def main():
    pass


if __name__ == '__main__':
    sys.exit(main())

