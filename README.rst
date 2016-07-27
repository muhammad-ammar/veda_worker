¡INCOMPLETE!
=====================
VEDA Worker 
=====================

Worker node clone for edx-VEDA
------------------------------

[ALPHA] / 2016.08
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

**Sample Usage** instantiate class:

::

    VW = VedaWorker(
        veda_id = '${ID_STRING}'
        encode_profile = '${ENCODE_ID}'
        )


Test (nose)

::

    VW.test()


**@yro / 2016**