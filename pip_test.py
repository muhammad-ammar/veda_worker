import os
import sys

"""
simple pip tester

"""
from veda_worker import VedaWorker


def pip_test():
    VW = VedaWorker(
        veda_id='XXXXXXXX2016-V00TEST', 
        encode_profile='desktop_mp4'
        )
    VW.run()


if __name__ == '__main__':
    pip_test()


