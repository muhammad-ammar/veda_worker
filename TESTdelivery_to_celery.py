
import os
import sys

"""
Test connection to delivery

"""
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'veda_worker'
        )
    )
import celeryapp

final_name = 'ACCFA1MAT215-V000100_100.mp4'

celeryapp.deliverable_route.apply_async(
    (final_name, ),
    queue='transcode_stat'
    )
