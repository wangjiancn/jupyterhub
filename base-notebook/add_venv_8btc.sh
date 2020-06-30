#!/usr/bin/env bash
M_DIR=/mnt/modules/${1}
JOB_ID=${2}
WORK=/mnt/work
HOME=/home/jovyan
PACKAGE_DIR=${M_DIR}/.localenv/lib/python3.6/site-packages

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

if [ ! -d ${M_DIR}  ] || [ ! -d ${PACKAGE_DIR} ] ; then
    echo "No such directory: $M_DIR"
    exit
fi

if [ ${JOB_ID} ] ; then
    echo "activating env"
    workon ${JOB_ID}
    path_file=${HOME}/.virtualenvs/${JOB_ID}/lib/python3.6/site-packages/_virtualenv_path_extensions.pth

else
    export WORKON_HOME=${WORK}
    echo "activating env"
    workon .localenv
    path_file=${WORK}/.localenv/lib/python3.6/site-packages/_virtualenv_path_extensions.pth

fi

echo "adding env"
sed -i '1 a\
'"$PACKAGE_DIR"'
' "$path_file"
#add2virtualenv ${PACKAGE_DIR}
echo "add env done"


