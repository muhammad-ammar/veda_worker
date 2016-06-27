import os
import sys

"""
simple pip tester

"""
from openveda import openVEDA


def test_openveda():
    OV = openVEDA(
        mezz_video=os.path.join(
            os.path.dirname(__file__), 
            'VEDA_TESTFILES', 
            'OVTESTFILE_01.mp4'
            )
        )

    OV.test()
    """Actually Run"""
    OV.activate()
    OV.complete()

if __name__ == '__main__':
    test_openveda()


