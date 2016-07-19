
import os
import sys
import boto
import boto.s3
from boto.s3.key import Key
import shutil
import hashlib
import requests

"""
Gets specified Video and Encode object, and delivers file to endpoint
from VEDA_WORK_DIR, retrieves and checks URL, and passes info to objects

"""

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
from global_vars import *
from reporting import ErrorObject
from config import OVConfig

CF = OVConfig()
CF.run()
settings = CF.settings_dict



class Deliver():


    def __init__(self, EncodeObject, VideoObject):
        self.EncodeObject = EncodeObject
        self.VideoObject = VideoObject
        ## Internal
        self.deliverable = self.EncodeObject.output_file
        # Reporting
        self.endpoint_url = None
        self.hash_sum = None
        self.upload_filesize = None
        self.complete = False


    def deliver_file(self):
        """
        Determine and run deliverable protocol
        """
        if not os.path.exists(self.deliverable):
            return False

        self.upload_filesize = os.stat(self.deliverable).st_size
        self.hash_sum = hashlib.md5(
            open(self.deliverable, 'rb').read()
            ).hexdigest()
                
        if self.upload_filesize < MULTI_UPLOAD_BARRIER:
            """
            Upload single part
            """
            self.complete = self._BOTO_SINGLEPART()
        else:
            """
            Upload multipart
            """
            self.complete = self._BOTO_MULTIPART()

        if self.complete is False:
            return None

        self.endpoint_url = '/'.join((
            'https://s3.amazonaws.com', 
            settings['aws_deliver_bucket'], 
            os.path.basename(self.deliverable)
            ))

        # Validate URL
        self.complete = self._VALIDATE_URL()


    def _BOTO_SINGLEPART(self):
        """
        Upload single part (under threshold in node_config)
        node_config MULTI_UPLOAD_BARRIER
        """
        try:
            conn = boto.connect_s3(
                settings['aws_access_key'],
                settings['aws_secret_key']
                )
            delv_bucket = conn.get_bucket(
                settings['aws_deliver_bucket']
                )
        except:
            ErrorObject.print_error(
                message = 'Deliverable Fail: s3 Connection Error\n \
                Check node_config DELIVERY_ENDPOINT'
                )
            return False

        upload_key = Key(delv_bucket)
        upload_key.key = os.path.basename(self.deliverable)
        upload_key.set_contents_from_filename(self.deliverable)
        upload_key.set_acl('public-read')
        return True

    def _BOTO_MULTIPART(self):
        """
        Split file into chunks, upload chunks

        NOTE: this should never happen, as your files should be much
        smaller than this, but one never knows
        """
        path_to_multipart = os.path.dirname(self.deliverable)
        filename = os.path.basename(self.deliverable)

        if not os.path.exists(
            os.path.join(path_to_multipart, filename.split('.')[0])
            ):
            os.mkdir(
                os.path.join(path_to_multipart, filename.split('.')[0])
                )

        os.chdir(os.path.join(path_to_multipart, filename.split('.')[0]))
        """
        Split File into chunks
        """ 
        split_command = 'split -b5m -a5' ##5 part names of 5mb
        sys.stdout.write('%s : %s\n' % (filename, 'Generating Multipart'))
        os.system(' '.join((split_command, self.deliverable)))
        sys.stdout.flush()

        """
        Connect to s3
        """
        try:
            c = boto.connect_s3(
                settings['aws_access_key'],
                settings['aws_secret_key']
                )
            b = c.lookup(settings['aws_deliver_bucket'])
        except:
            ErrorObject.print_error(
                message = 'Deliverable Fail: s3 Connection Error\n \
                Check node_config DELIVERY_ENDPOINT'
                )
            return False

        if b == None:
            ErrorObject.print_error(
                message = 'Deliverable Fail: s3 Connection Error\n \
                Check node_config DELIVERY_ENDPOINT'
                )
            return False

        """
        Upload and stitch parts
        """
        mp = b.initiate_multipart_upload(filename)

        x = 1
        for file in os.listdir(os.path.join(path_to_multipart, filename.split('.')[0])):
            sys.stdout.write('%s : %s\r' % (file, 'uploading part'))
            fp = open(file, 'rb')
            mp.upload_part_from_file(fp, x)
            fp.close()
            sys.stdout.flush()            
            x += 1
        sys.stdout.write('\n')
        mp.complete_upload()
        mp.set_acl('public-read')
        """Clean up multipart"""
        shutil.rmtree(os.path.join(path_to_multipart, filename.split('.')[0]))
        return True


    def _VALIDATE_URL(self):
        u = requests.head(self.endpoint_url)
        if u.status_code > 399:
            return False
        return True


def main():
    pass


if __name__ == '__main__':
    sys.exit(main())

