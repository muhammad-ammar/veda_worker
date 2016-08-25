#!/bin/bash
#--- Startup Script for VEDA Worker --#

echo "
__     _______ ____    _   __        __         _             
\ \   / | ____|  _ \  / \  \ \      / ___  _ __| | _____ _ __ 
 \ \ / /|  _| | | | |/ _ \  \ \ /\ / / _ \| '__| |/ / _ | '__|
  \ V / | |___| |_| / ___ \  \ V  V | (_) | |  |   |  __| |   
   \_/  |_____|____/_/   \_\  \_/\_/ \___/|_|  |_|\_\___|_|   
                                                              
"

ROOTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${ROOTDIR}

echo "Initializing"
E=`nosetests -s`

# Get vars from yaml
QUEUE=$(cat ${ROOTDIR}/instance_config.yaml | grep celery_receiver_queue)
QUEUE=${QUEUE#*: }
CONCUR=$(cat ${ROOTDIR}/instance_config.yaml | grep celery_threads)
CONCUR=${CONCUR#*: }

if [[ $E == *"*****"* ]]
then
    # purposefully generate an error to raise terraform, etc.
    # exit 64;
    print '[ERROR] : TEST FAILED'
else
    python ${ROOTDIR}/veda_worker/celeryapp.py worker --loglevel=info --concurrency=${CONCUR} -Q ${QUEUE} -n worker1.%h
fi


