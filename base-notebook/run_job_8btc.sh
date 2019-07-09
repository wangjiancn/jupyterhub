#!/usr/bin/env bash
WORK=/mnt/input
HOME=/home/jovyan
JOB_ID=${1}
SCRIPT=${2}
echo 'SYSTEM: Preparing env...'

VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

ENV_PATH=/home/jovyan/.virtualenvs/${JOB_ID}
path_file=${ENV_PATH}/lib/python3.5/site-packages/_virtualenv_path_extensions.pth

if [ ! -e ${ENV_PATH} ] ; then
    virtualenv-clone /home/jovyan/.virtualenvs/jlenv ${ENV_PATH}
fi

workon ${JOB_ID}

echo "import sys; sys.__plen = len(sys.path)" > "$path_file"
echo ${HOME}/.virtualenvs/basenv/lib/python3.5/site-packages >> "$path_file"
echo ${WORK}/.localenv/lib/python3.5/site-packages >> "$path_file"
echo "import sys; new=sys.path[sys.__plen:]; del sys.path[sys.__plen:]; p=getattr(sys,'__egginsert',0); sys.path[p:p]=new; sys.__egginsert = p+len(new)" >> "$path_file"

if [ ! -f ${WORK}/${SCRIPT} ] ; then
    echo script path ${WORK}/${SCRIPT} not exists
    exit 1
fi

echo 'SYSTEM: Running...'

${ENV_PATH}/bin/python /home/jovyan/job_funcs.py start_job ${JOB_ID}

${ENV_PATH}/bin/python ${SCRIPT}
SUCCESS=$?
echo 'SYSTEM: Finishing...'
${ENV_PATH}/bin/python /home/jovyan/job_funcs.py finish_job ${JOB_ID} ${SUCCESS}
if [ ${SUCCESS} != 0 ] ; then
    echo 'SYSTEM: Error Exists!'
    exit 1
fi
echo 'SYSTEM: Done!'
exit 0
