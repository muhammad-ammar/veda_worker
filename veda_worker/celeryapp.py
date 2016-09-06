
from __future__ import absolute_import
import os
import sys
from os.path import expanduser
from celery import Celery
import shutil

"""

Start Celery Worker (if VEDA-attached node)

"""
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import WorkerSetup

WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict

homedir = expanduser("~")

def cel_Start():
    app = Celery(
        settings['celery_app_name'],
        broker='amqp://' + settings['rabbitmq_user'] + \
            ':' + settings['rabbitmq_pass'] + '@' + settings['rabbitmq_broker'] + ':5672//',
        backend='amqp://' + settings['rabbitmq_user'] + \
            ':' + settings['rabbitmq_pass'] + '@' + settings['rabbitmq_broker'] + ':5672//',
        include=['celeryapp']
        )

    app.conf.update(
        BROKER_CONNECTION_TIMEOUT = 60,
        CELERY_IGNORE_RESULT = True,
        CELERY_TASK_RESULT_EXPIRES = 10,
        CELERYD_PREFETCH_MULTIPLIER = 1
        )

    return app

app = cel_Start()


@app.task(name='worker_encode')
def worker_task_fire(veda_id, encode_profile, jobid):
    task_command = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'bin',
        'veda_worker_cli'
        )
    task_command += ' '
    task_command += '-v ' + veda_id
    task_command += ' '
    task_command += '-e ' + encode_profile
    task_command += ' '
    task_command += '-j ' + jobid

    os.system(task_command)

    """
    Add secondary directory protection
    """
    if jobid is not None and os.path.exists(
        os.path.join(
            homedir,
            'ENCODE_WORKDIR',
            jobid
            )
        ):
        shutil.rmtree(
            os.path.join(
                homedir,
                'ENCODE_WORKDIR',
                jobid
                )
            )


@app.task(name='supervisor_deliver')
def deliverable_route(veda_id, encode_profile):
    """
    Just register this task with big veda
    """
    pass


@app.task
def queue_transcode(vid_name, encode_command):
    """
    Just register this task with big veda
    """
    pass


@app.task
def test_command(message):
    print message


if __name__ == '__main__':
    app = cel_Start()
    app.start()
