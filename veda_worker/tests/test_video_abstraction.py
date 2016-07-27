
import os
import sys
import unittest

"""
init end-to-end function tests

"""
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import WorkerSetup
from reporting import ErrorObject
# from veda_worker.__init__ import VedaWorker
from abstractions import Video
from validate import ValidateVideo


class TestVideoAbstraction(unittest.TestCase):

    def setUp(self):
        self.VideoObject = Video()
        self.VideoObject.activate()
        self.VideoObject.valid = ValidateVideo(
            filepath=self.VideoObject.mezz_filepath
            ).valid


    def test_video_object(self):
        self.assertTrue(os.path.exists(self.VideoObject.mezz_filepath))


    def test_video_validate(self):
        self.assertTrue(self.VideoObject.valid)



def main():
    unittest.main()

if __name__ == '__main__':
    sys.exit(main())
