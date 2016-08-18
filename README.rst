=====================
VEDA Worker 
=====================

Worker node clone for edx-VEDA
------------------------------

[BETA] / 2016.08
~~~~~~~~~~~~~~~~

.. image:: https://travis-ci.org/yro/veda_worker.svg?branch=build_1
    :target: https://travis-ci.org/yro/veda_worker

--------------

Installation
------------

::
    
    python setup.py install


Usage
-----

**from command line:**

::

    veda_worker


**Python** instantiate class:

::

    VW = VedaWorker(
        veda_id = '${ID_STRING}'
        encode_profile = '${ENCODE_ID}'
        jobid='${JOB_ID}'
        )


Test (nose)
-----

::

    VW.test()


Celery Async
-----

::

    import celeryapp

::

    veda_id='${ID_STRING}'
    encode_profile='${ENCODE_ID}'
    jobid='${JOB_ID}'

    celeryapp.worker_task_fire.apply_async(
        (veda_id, encode_profile, jobid),
        queue='test_node'
        )


**@yro / 2016**