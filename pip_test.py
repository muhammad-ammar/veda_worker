import os
import sys

"""
simple pip tester

"""
from veda_worker import VedaWorker
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
import celery_task_fire


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

    celery_task_fire.vw_task_fire.apply_async(
        (veda_id, encode_profile, jobid),
        queue='test_node'
        )


if __name__ == '__main__':
    cel_test()

