#!/usr/bin/env bash
WORK=/home/jovyan/work
HOME=/home/jovyan
JOB_ID=${1}
SCRIPT=${2}
RUN_FUNC=${3}
TASK_ID=${4}
ARGS=${5}
TIMEOUT=${6}

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
${ENV_PATH}/bin/python /home/jovyan/job_funcs.py insert_module ${JOB_ID}

echo 'SYSTEM: Running...'
${ENV_PATH}/bin/python /home/jovyan/job_funcs.py start_job ${JOB_ID}
/usr/bin/timeout ${TIMEOUT} ${ENV_PATH}/bin/python ${SCRIPT} ${RUN_FUNC} ${TASK_ID} ${ARGS}
SUCCESS=$?
echo 'SYSTEM: Finishing...'
${ENV_PATH}/bin/python /home/jovyan/job_funcs.py finish_job ${JOB_ID} ${SUCCESS}
if [ ${SUCCESS} != 0 ] ; then
    echo 'SYSTEM: Error Exists!'
    exit 1
fi
echo 'SYSTEM: Done!'
exit 0
