#!/usr/bin/env bash
WORK=/mnt/work
HOME=/home/jovyan
JOB_ID=${1}
SCRIPT=${2}
ARGS=${3}
echo 'SYSTEM: Preparing env...'

VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

ENV_PATH=/home/jovyan/.virtualenvs/basenv

workon basenv

if [ ! -f ${WORK}/${SCRIPT} ] ; then
    echo script path ${WORK}/${SCRIPT} not exists
    exit 1
fi

cd ${WORK}
echo 'SYSTEM: Running...'
${ENV_PATH}/bin/python /home/jovyan/job_funcs.py start_job ${JOB_ID}
${ENV_PATH}/bin/python ${SCRIPT} ${ARGS}
SUCCESS=$?
echo 'SYSTEM: Finishing...'
${ENV_PATH}/bin/python /home/jovyan/job_funcs.py finish_job ${JOB_ID} ${SUCCESS}
if [ ${SUCCESS} != 0 ] ; then
    echo 'SYSTEM: Error Exists!'
    exit 1
fi
echo 'SYSTEM: Done!'
exit 0
