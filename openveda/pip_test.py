import os
import sys

"""
simple pip tester

"""
from openveda import OpenVeda


def test_openveda():
    OV = OpenVeda(
        mezz_video='OVTESTFILE_01.mp4',
        hls=True
        )
    # OV.test_config()
    # run encodes
    OV.run()
    print OV.complete


if __name__ == '__main__':
    test_openveda()

