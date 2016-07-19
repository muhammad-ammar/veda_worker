
import os
import sys
import unittest

"""
Test 'Delivery Function' class

"""
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

from config import OVConfig
from openveda.__init__ import OpenVeda
from abstractions import Video
from global_vars import *



class TestDeliverable(unittest.TestCase):

    def setUp(self):
        CF = OVConfig(settings_yaml=DEFAULT_YAML)
        CF.run()
        self.settings = CF.settings_dict

        """
        rework settings to minimal encode
        """
        for key, entry in self.settings['encode_library'].iteritems():
            new_encode_lib = {key : entry}
            break
        self.settings['encode_library'] = new_encode_lib
        # print self.settings['encode_library']

        self.test_file = os.path.join(
            TEST_VIDEO_DIR, 
            TEST_VIDEO_FILE
            )
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
            self.OVT._VALIDATE_ENCODES(E=E)
        for E in self.OVT.AbstractionLayer.Encodes:
            self.OVT._DELIVER_ENCODES(E=E)
            self.OVT._VALIDATE_DELIVERY(E=E)


    def tearDown(self):
        for file in os.listdir(self.settings['workdir']):
            os.remove(os.path.join(
                self.settings['workdir'],
                file
                ))

    def test_url_valid(self):
        for E in self.OVT.AbstractionLayer.Encodes:
            self.assertTrue(E.encoded is True)
            self.assertTrue(E.delivered is True)

def main():
    unittest.main()

if __name__ == '__main__':
    sys.exit(main())
