
from __future__ import absolute_import
import os
import sys

"""

Start Celery Worker (if VEDA-attached node)

"""
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from celery import Celery
from config import WorkerSetup

WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
import celery_task_fire


def cel_Start():
    app = Celery(
        settings['celery_app_name'],
        broker='amqp://' + settings['rabbitmq_user'] + \
            ':' + settings['rabbitmq_pass'] + '@' + settings['rabbitmq_broker'] + ':5672//',
        backend='amqp://' + settings['rabbitmq_user'] + \
            ':' + settings['rabbitmq_pass'] + '@' + settings['rabbitmq_broker'] + ':5672//',
        include=['celery_task_fire']
        )

    app.conf.update(
        CELERY_IGNORE_RESULT = True,
        CELERY_TASK_RESULT_EXPIRES = 10,
        CELERYD_PREFETCH_MULTIPLIER = 1
        )

    return app


if __name__ == '__main__':
    app = cel_Start()
    app.start()
