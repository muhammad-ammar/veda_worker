#!/bin/bash
#--- Startup Script for VEDA Worker --#

echo "
__     _______ ____    _   __        __         _             
\ \   / | ____|  _ \  / \  \ \      / ___  _ __| | _____ _ __ 
 \ \ / /|  _| | | | |/ _ \  \ \ /\ / / _ \| '__| |/ / _ | '__|
  \ V / | |___| |_| / ___ \  \ V  V | (_) | |  |   |  __| |   
   \_/  |_____|____/_/   \_\  \_/\_/ \___/|_|  |_|\_\___|_|   
                                                              
"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}

echo "Initializing"
nosetests

# Get vars from yaml
QUEUE=$(cat ${DIR}/instance_config.yaml | grep celery_queue)
QUEUE=${QUEUE#*: }
CONCUR=$(cat ${DIR}/instance_config.yaml | grep celery_threads)
CONCUR=${CONCUR#*: }

python /Users/tiagorodriguez/Desktop/veda_worker/veda_worker/celeryapp.py worker --loglevel=info --concurrency=${CONCUR} -Q ${QUEUE}

