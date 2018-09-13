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

cd ${WORK}
${ENV_PATH}/bin/python ${SCRIPT}
SUCCESS=$?
${ENV_PATH}/bin/python /home/jovyan/finish_job.py ${JOB_ID} ${SUCCESS}
