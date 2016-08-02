
import os
import sys
import boto
import boto.s3
from boto.s3.key import Key
import shutil
# import ftplib
# import pysftp
import hashlib

"""
Gets specified Video and Encode object, and delivers file to endpoint
from VEDA_WORK_DIR, retrieves and checks URL, and passes info to objects

"""

# root_dir = os.path.dirname(os.path.dirname(__file__))
# sys.path.append(os.path.dirname(os.path.dirname(
#     os.path.abspath(__file__)
#     )))
from global_vars import *
from reporting import ErrorObject
from config import WorkerSetup
WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict



class Deliverable():

    def __init__(self, VideoObject, encode_profile, output_file):
        self.VideoObject = VideoObject
        self.encode_profile = encode_profile
        self.output_file = output_file
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
            open(os.path.join(self.workdir, self.output_file), 'rb').read()
            ).hexdigest()

        # if len(self.Settings.DELIVERY_ENDPOINT) > 0:
            # if self.Settings.S3_DELIVER is True:
                
                if self.upload_filesize < self.Settings.MULTI_UPLOAD_BARRIER:
                    """
                    Upload single part
                    """
                    self.complete = self._s3_upload()
                else:
                    """
                    Upload multipart
                    """
                    self.complete = self._boto_multipart()

                if self.complete is False:
                    return False

                self.endpoint_url = '/'.join((
                    'https://s3.amazonaws.com', 
                    self.Settings.DELIVERY_ENDPOINT, 
                    self.EncodeObject.output_file.split('/')[-1]
                    ))
                return True

            else:
                self.complete = self._ftp_upload()
                if self.complete is False:
                    return False

                """
                Groom URL
                TODO : Dir cleaning
                """
                if self.Settings.DELIVERY_ENDPOINT[-1] == '/':
                    url = self.Settings.DELIVERY_ENDPOINT + self.EncodeObject.output_file.split('/')[-1]
                else:
                    url = '/'.join((
                        self.Settings.DELIVERY_ENDPOINT, 
                        self.EncodeObject.output_file.split('/')[-1]
                        ))

                if self.Settings.SSL_ENDPOINT is True:
                    self.endpoint_url = url.replace('ftp://', 'https://')
                else:
                    self.endpoint_url = url.replace('ftp://', 'http://')
                return True
        else:
            ## No delivery
            return True

    def _s3_upload(self):
        """
        Upload single part (under threshold in node_config)
        node_config MULTI_UPLOAD_BARRIER
        """
        try:
            conn = boto.connect_s3(
                self.Settings.DELIVERY_ID, 
                self.Settings.DELIVERY_PASS
                )
            delv_bucket = conn.get_bucket(self.Settings.DELIVERY_ENDPOINT)
        except:
            ErrorObject(
                method = self,
                message = 'Deliverable Fail: s3 Connection Error\n \
                Check node_config DELIVERY_ENDPOINT'
                )
            return False

        upload_key = Key(delv_bucket)
        upload_key.key = self.EncodeObject.output_file.split('/')[-1]
        upload_key.set_contents_from_filename(self.EncodeObject.output_file)
        return True


    def _boto_multipart(self):
        """
        Split file into chunks, upload chunks

        NOTE: this should never happen, as your files should be much
        smaller than this, but one never knows
        """
        
        path_to_multipart = os.path.dirname(self.EncodeObject.output_file)
        filename = self.EncodeObject.output_file.split('/')[-1]

        if not os.path.exists(
            os.path.join(path_to_multipart, filename.split('.')[0])
            ):
            os.mkdir(os.path.join(path_to_multipart, filename.split('.')[0]))

        os.chdir(os.path.join(path_to_multipart, filename.split('.')[0]))
        """
        Split File into chunks
        """ 
        split_command = 'split -b5m -a5' ##5 part names of 5mb
        sys.stdout.write('%s : %s\n' % (filename, 'Generating Multipart'))
        os.system(' '.join((split_command, self.EncodeObject.output_file)))
        sys.stdout.flush()

        """
        Connect to s3
        """
        try:
            c = boto.connect_s3(
                self.Settings.DELIVERY_ID, 
                self.Settings.DELIVERY_PASS
                )
            b = c.lookup(self.Settings.DELIVERY_ENDPOINT)
        except:
            ErrorObject(
                method = self,
                message = 'Deliverable Fail: s3 Connection Error\n \
                Check node_secrets s3 connection'
                )
            return False

        if b == None:
            ErrorObject(
                method = self,
                message = 'Deliverable Fail: s3 Bucket Connection Error\n \
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
        """Clean up multipart"""
        shutil.rmtree(os.path.join(path_to_multipart, filename.split('.')[0]))
        return True


    def _ftp_upload(self):
        """
        We could make this just look in the WORKDIR, but I think
        it should be more agnostic
        """

        ## Yuck, but it'll get us what we need
        host_array = self.Settings.DELIVERY_ENDPOINT.split('://')[1].split('/')
        delv_host = host_array[0]
        delv_directory = '/'.join(host_array[1:len(host_array)])

        """FTP/SFTP endpoints"""
        if self.Settings.DELIVERY_ENDPOINT[0] == 'f':
            """
            FTP

            """
            ftpD = ftplib.FTP(delv_host)
            ftpD.login(
                self.Settings.DELIVERY_ID, 
                self.Settings.DELIVERY_PASS
                )
            ftpD.cwd(delv_directory)

            os.chdir(os.path.dirname(self.EncodeObject.output_file))

            ftpD.storbinary(
                'STOR ' + self.EncodeObject.output_file.split('/')[-1], 
                open(self.EncodeObject.output_file.split('/')[-1], 'rb')
                )
            ftpD.quit()

        elif self.Settings.DELIVERY_ENDPOINT[0] == 's':
            """
            SFTP

            """
            ## TODO: if '/' in DELIVERY_PASS
            try:
                s1 = pysftp.Connection(
                    delv_host,
                    username=self.Settings.DELIVERY_ID,
                    password=self.Settings.DELIVERY_PASS,
                    port=self.sftp_port,
                    )
            except:
                ErrorObject(
                    method = self,
                    message = 'Deliverable Fail: s3 Bucket Connection Error\n \
                    Check node_config DELIVERY_ENDPOINT'
                    )
            if len(delv_directory) > 0:
                s1.cwd(remote_directory)

            s1.put(
                self.EncodeObject.output_file, 
                )
            return True



def main():
    pass


if __name__ == '__main__':
    sys.exit(main())




































