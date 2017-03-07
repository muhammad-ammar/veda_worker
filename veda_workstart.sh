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

# Get vars from yaml
QUEUE=$(cat ${ROOTDIR}/instance_config.yaml | grep celery_receiver_queue)
QUEUE=${QUEUE#*: }
CONCUR=$(cat ${ROOTDIR}/instance_config.yaml | grep celery_threads)
CONCUR=${CONCUR#*: }
echo $QUEUE
echo $CONCUR

NEW_RELIC_CONFIG_FILE=${ROOTDIR}/veda_worker_newrelic.ini newrelic-admin run-program python ${ROOTDIR}/veda_worker/celeryapp.py worker \
        --loglevel=info --concurrency=${CONCUR} -Q ${QUEUE} -n worker.%h

