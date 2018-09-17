#!/usr/bin/env bash
WORK=/home/jovyan/work
HOME=/home/jovyan
JOB_ID=${1}
SCRIPT=${2}

VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

#export WORKON_HOME=${HOME}
ENV_PATH=/home/jovyan/.virtualenvs/${JOB_ID}
if [ ! -e ${ENV_PATH} ] ; then
    virtualenv-clone /home/jovyan/.virtualenvs/jlenv ${ENV_PATH}
fi
#mkvirtualenv .localenv
workon ${JOB_ID}

add2virtualenv /home/jovyan/.virtualenvs/basenv/lib/python3.5/site-packages

if [ ! -f ${WORK}/${SCRIPT} ] ; then
    echo 'script path not exists'
    exit 1
fi

export NB_CLIENT_ENV=k8s

cd ${WORK}
echo 'SYSTEM: Preparing env...'
if [ -f ${WORK}/requirements.txt ] ; then
    echo 'SYSTEM: Installing requirements.txt...'
    ${ENV_PATH}/bin/pip install  -r ${WORK}/requirements.txt
fi
${ENV_PATH}/bin/python /home/jovyan/job_funcs.py insert_module ${JOB_ID}
echo 'SYSTEM: Running...'
${ENV_PATH}/bin/python ${SCRIPT}
SUCCESS=$?
echo 'SYSTEM: Finishing...'
${ENV_PATH}/bin/python /home/jovyan/job_funcs.py finish_job ${JOB_ID} ${SUCCESS}
if [ ${SUCCESS} == 1 ] ; then
    echo 'SYSTEM: Error Exists!'
    exit 1
fi
echo 'SYSTEM: Done!'
exit 0
