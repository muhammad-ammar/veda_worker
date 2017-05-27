
import os
import sys
import unittest

from veda_worker.abstractions import Video

"""
init end-to-end function tests

"""


class TestVideoAbstraction(unittest.TestCase):

    def setUp(self):
        self.VideoObject = Video()
        self.VideoObject.activate()

    def test_video_object(self):
        self.assertTrue(os.path.exists(self.VideoObject.mezz_filepath))

    def test_video_validate(self):
        self.assertTrue(self.VideoObject.valid)


def main():
    unittest.main()

if __name__ == '__main__':
    sys.exit(main())
