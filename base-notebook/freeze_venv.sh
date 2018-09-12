#!/usr/bin/env bash
PREFIX=faas
if [ ${1} ] ; then
    PREFIX=${1}
fi

WORK=/home/jovyan/work

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

export WORKON_HOME=${WORK}

workon .localenv
echo "freezing env"
pip freeze > /home/jovyan/work/${PREFIX}_requirements.txt
echo "freeze env done"

