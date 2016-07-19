
import os
import sys
import unittest

"""
Test 'Command' class

"""
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

from config import OVConfig
from openveda.__init__ import OpenVeda
from abstractions import Video
from global_vars import *


class TestEncode(unittest.TestCase):

    def setUp(self):
        CF = OVConfig(settings_yaml=DEFAULT_YAML)
        CF.run()
        self.settings = CF.settings_dict
        self.test_file = os.path.join(
            TEST_VIDEO_DIR, 
            TEST_VIDEO_FILE
            )
        """
        rework settings to minimal encode
        """
        for key, entry in self.settings['encode_library'].iteritems():
            new_encode_lib = {key : entry}
            break
        self.settings['encode_library'] = new_encode_lib

        self.OVT = OpenVeda(
            mezz_video=self.test_file,
            localfile=True
            )
        self.OVT.settings = self.settings

        #----
        # Pipeline Steps
        self.OVT._INGEST()
        self.OVT._PIPELINE_INITIALIZE()
        for E in self.OVT.AbstractionLayer.Encodes:
            self.OVT._ENCODE(E=E)


    def tearDown(self):
        for file in os.listdir(self.settings['workdir']):
            os.remove(os.path.join(
                self.settings['workdir'],
                file
                ))


    def test_testfile(self):
        """
        Make sure test file exists
        """
        self.assertTrue(os.path.exists(self.test_file))


    def test_instantiate(self):
        """
        Video Object
        """
        self.assertFalse(self.OVT.mezz_video == None)


    def test_ingest(self):
        """
        check validity and existance of mezz file
        """
        self.assertTrue(self.OVT.VideoObject.valid)
        self.assertTrue(os.path.exists(
            os.path.join(
                self.settings['workdir'],
                self.OVT.mezz_video
                )
            ))


    def test_encode_gen(self):
        """
        Super Basic Test
        """
        for E in self.OVT.AbstractionLayer.Encodes:
            self.assertTrue(len(E.ffcommand) > 0)


    def test_encode_run(self):
        """
        Check for encoded files
        """
        for E in self.OVT.AbstractionLayer.Encodes:
            self.assertTrue(E.encoded)
            self.assertTrue(os.path.exists(E.output_file))


    def test_encode_valid(self):
        """
        Test validity of encodes
        """
        for E in self.OVT.AbstractionLayer.Encodes:
            # Check if valid
            VT = Video(mezz_video=E.output_file)
            VT.validate()
            self.assertTrue(VT.valid is True)
            """
            TODO:
            check aspect ratio
            check duration
            """


def main():
    unittest.main()

if __name__ == '__main__':
    sys.exit(main())

