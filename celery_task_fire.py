#!/usr/bin/env python
from __future__ import absolute_import
import os
import sys
import argparse


"""
Copyright (C) 2016 @yro | Gregory Martin

Command Line Interface
"""
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'veda_worker'
        )
    )
from celeryapp import cel_Start
app = cel_Start()


@app.task
def vw_task_fire(veda_id, encode_profile):
    task_command = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'bin',
        'veda_worker'
        )
    task_command += ' '
    task_command += '-v ' + veda_id
    task_command += ' '
    task_command += '-e ' + encode_profile

    os.system(task_command)

@app.task
def deliverable_route(final_name):
    """
    Just register this task with big veda
    """
    pass


if __name__ == "__main__":
    pass
