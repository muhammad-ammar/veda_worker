import os
import sys

"""
simple pip tester

"""
from veda_worker import VedaWorker
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'veda_worker'
        )
    )
import celeryapp


def pip_test():
    VW = VedaWorker(
        veda_id='XXXXXXXX2016-V00TEST', 
        encode_profile='desktop_mp4',
        jobid = 'xx4xx'
        )
    VW.run()


def cel_test():

    veda_id='XXXXXXXX2016-V00TEST'
    encode_profile='desktop_mp4'
    jobid='xx4xx'

    celeryapp.worker_task_fire.apply_async(
        (veda_id, encode_profile, jobid),
        queue='test_node'
        )


if __name__ == '__main__':
    pass
    # cel_test()

