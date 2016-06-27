
from __future__ import absolute_import
import os
import sys

"""

Start Celery Worker (if VEDA-attached node)

"""
from celery import Celery


def cel_Start(Settings):

    app = Celery(
        Settings.CELERY_APP_NAME,
        broker='amqp://' + Settings.RABBIT_USER + ':' + Settings.RABBIT_PASS + '@' + Settings.RABBIT_BROKER + ':5672//',
        backend='amqp://' + Settings.RABBIT_USER + ':' + Settings.RABBIT_PASS + '@' + Settings.RABBIT_BROKER + ':5672//',
        include=Settings.CELERY_QUEUE
        )

    app.conf.update(
        CELERY_IGNORE_RESULT = True,
        CELERY_TASK_RESULT_EXPIRES = 10,
        CELERYD_PREFETCH_MULTIPLIER = 1
        )

    return app


if __name__ == '__main__':
    from config import Settings
    S1 = Settings(
        node_config = os.path.join(os.path.dirname(__file__), 'settings.py')
        )
    S1.activate()
    app = cel_Start(Settings=S1)
    app.start()
