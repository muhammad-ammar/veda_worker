
import os
import sys
import argparse
import nose
import subprocess
import requests
import shutil

"""
OpenVeda : A purpose-built tool to transcode video 
for instances of the edX platform.
    
    Copyright (C) 2016 @yro | Gregory Martin

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    greg@willowgrain.io


Generate a serial transcode stream from either an 
open edx studio instance upload or VEDA instance via Celery

"""

from config import OVConfig
from reporting import ErrorObject, Output
from abstractions import AbstractionLayer, Video, Encode
from global_vars import *

sys.path.append(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    'pipeline'
    ))

from pipeline_ingest import Ingest
from pipeline_encode import Command
from pipeline_deliver import Deliver
from pipeline_val import VALData



class OpenVeda():

    def __init__(self, **kwargs):
        self.mezz_video = kwargs.get('mezz_video', None)
        self.localfile = kwargs.get('localfile', False)
        self.settings = None
        self.VideoObject = None
        self.AbstractionLayer = None

        # complete?
        self.complete = False
        self.video_id = None
        self.valid = False

        # hls
        self.hls = kwargs.get('hls', False)

        # specialties
        self.course_url = kwargs.get('course_url', None)
        self.settings_yaml = kwargs.get('settings_file', None)


    def config(self, **kwargs):
        ## for nose
        self.test = kwargs.get('test', False)
        self.testvar = kwargs.get('testvar', None)
        """
        config instance, w/ testcase

        """
        if self.settings_yaml is None:
            CF = OVConfig(
                configure=True, 
                test=self.test, 
                testvar=self.testvar
                )
        else:
            CF = OVConfig(
                configure=True, 
                test=self.test, 
                testvar=self.testvar,
                settings_yaml=self.settings_yaml
                )

        CF.run()
        self.settings = CF.settings_dict


    def test_config(self):
        """
        Run tests
        """
        current_dir = os.getcwd()
        if self.settings is None:
            CF = OVConfig()
            CF.run()
            self.settings = CF.settings_dict

        test_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'tests'
            )
        os.chdir(test_dir)
        result = nose.run()

        '''Return to previous state'''
        os.chdir(current_dir)
        return result


    def run(self):
        if self.settings is None:
            CF = OVConfig()
            CF.run()
            self.settings = CF.settings_dict

        """
        First some basic kwarg checking, then we're off to the races
        """
        if self.mezz_video == None:
            ErrorObject.print_error(
                message = 'No File Specified'
                )
            return None
        """
        Run Pipeline
        """
        self._INGEST()
        if self.VideoObject.valid is False:
            """
            TODO: If corrupt, send to VAL?
            """
            # ErrorObject.print_error(
            #     message = 'Invalid Video File'
            #     )
            return None

        if self.VideoObject.course_url is None:
            self.VideoObject.course_url = self.course_url

        self._PIPELINE_INITIALIZE()
        """
        Encode Videos, Validate Encodes
        """
        for E in self.AbstractionLayer.Encodes:
            self._ENCODE(E=E)
            self._VALIDATE_ENCODES(E=E)

        """
        Deliver to endpoint
        """
        # for E in self.AbstractionLayer.Encodes:
            # print 2
            # print E.profile_name
            # print E.encoded

        for E in self.AbstractionLayer.Encodes:
            self._DELIVER_ENCODES(E=E)

        # Validate, mark complete
        for E in self.AbstractionLayer.Encodes:
            self._VALIDATE_DELIVERY(E=E)
            self._UPDATE_API(E=E)

        """
        cleanup
        """
        self._CLEAN_ENVIRON()


    def _INGEST(self):

        FI = Ingest(
            mezz_video=self.mezz_video,
            localfile=self.localfile
            )
        ingested = FI.run()
        if ingested is False:
            return False

        self.VideoObject = FI.VideoObject
        self.VideoObject.validate()
        self.video_id = self.VideoObject.val_id
        self.valid = self.VideoObject.valid

    
    def _PIPELINE_INITIALIZE(self):
        if self.settings is None:
            CF = OVConfig()
            CF.run()
            self.settings = CF.settings_dict

        self.AbstractionLayer = AbstractionLayer(
            VideoObject=self.VideoObject
            )
        """
        Get all the encode profiles
        """
        for key, entry in self.settings['encode_library'].iteritems():
            """
            Trigger for HLS
            """
            E1 = Encode(
                VideoObject = self.AbstractionLayer.VideoObject,
                profile_name = key,
                )
            self.AbstractionLayer.Encodes.append(E1)

        for E in self.AbstractionLayer.Encodes:
            if self.hls is True and E.profile_name == HLS_SUBSTITUTE:
                """
                We'll let VHLS do this whole thing, and retrieve the 
                url from there
                """
                from vhls import VHLS

                vhls_mezz = '/'.join((
                    'https://s3.amazonaws.com',
                    self.settings['aws_storage_bucket'],
                    self.mezz_video
                    ))

                VH = VHLS(
                    mezz_file = vhls_mezz,
                    ACCESS_KEY_ID = self.settings['aws_access_key'],
                    SECRET_ACCESS_KEY = self.settings['aws_secret_key'],
                    DELIVER_BUCKET = self.settings['aws_deliver_bucket'],
                    WORKDIR = self.settings['workdir'],
                    clean=False,
                    )

                if VH.complete is True:
                    E.encoded = True
                    E.valid = True
                    E.endpoint_url = VH.manifest_url
                    E.upload_filesize = 0
                    E.rate_factor = 0

            else:
                CG = Command(
                    VideoObject = self.AbstractionLayer.VideoObject,
                    EncodeObject = E,
                    )
                CG.generate()
                if CG.ffcommand is None:
                    ErrorObject.print_error(
                        message = 'Command Generation Invalid'
                        )
                    return None
                E.ffcommand = CG.ffcommand


    def _ENCODE(self, E):
        """
        Run the commands, which tests for a file and returns
        a bool and the filename
        """
        files_array = [f for f in E.ffcommand.split(' ') if '/' in f]
        # Source File Check
        if len(files_array) == 0:
            # encode gen error
            return None

        if not os.path.exists(self.VideoObject.mezz_filepath):
            ErrorObject.print_error(
                message = 'Work File Not Found'
                )
            return None

        process = subprocess.Popen(
            E.ffcommand, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            shell=True, 
            universal_newlines=True
            )
        # Status Bar
        Output().status_bar(process=process)
        # just to be polite
        print

        if 'ffmpeg' in files_array[0]:
            E.output_file = files_array[2]
        else:
            E.output_file = files_array[1]

        if os.path.exists(E.output_file):
            E.encoded = True


    def _VALIDATE_ENCODES(self, E):
        if E.output_file is None:
            return None
        VE = Video(mezz_video=E.output_file)
        VE.validate()

        if VE.valid is False:
            E.valid = False
            return None

        if not (self.VideoObject.mezz_duration - 5) <= \
        VE.mezz_duration <= \
        (self.VideoObject.mezz_duration + 5):
            E.valid = False
            return None

        E.valid = True


    def _DELIVER_ENCODES(self, E):
        if E.output_file is None:
            return None

        if not os.path.exists(E.output_file):
            return None

        if E.valid is False:
            return None

        """
        Deliver Here
        """
        D1 = Deliver(
            VideoObject=self.AbstractionLayer.VideoObject, 
            EncodeObject=E
            )
        passed = D1.deliver_file()
        if passed is False: 
            return None

        E.upload_filesize = D1.upload_filesize
        E.hash_sum = D1.hash_sum
        E.endpoint_url = D1.endpoint_url


    def _VALIDATE_DELIVERY(self, E):
        # if E.output_file is None:
            # return None
        v = requests.head(E.endpoint_url)
        if v.status_code > 299:
            print v.status_code
            ErrorObject.print_error(
                message = 'Delivered URL Error'
                )
            return None

        E.delivered = True


    def _UPDATE_API(self, E):
        if E.delivered is False:
            return None

        V1 = VALData(
            VideoObject=self.AbstractionLayer.VideoObject, 
            EncodeObject=E
            )
        E.complete = V1.send_data()


    def _CLEAN_ENVIRON(self):
        for E in self.AbstractionLayer.Encodes:
            if E.output_file is not None:
                os.remove(E.output_file)

        """
        TODO: should test hotstore
        """
        os.remove(os.path.join(
            self.settings['workdir'],
            self.VideoObject.mezz_video
            ))

        """
        test for completion
        """
        self.complete = True
        for E in self.AbstractionLayer.Encodes:
            if E.complete is False:
                self.complete = False



def main():
    pass

if __name__ == '__main__':
    sys.exit(main())

