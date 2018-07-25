#!/usr/bin/env bash
WORK=/home/jovyan/work

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

export WORKON_HOME=${WORK}

workon localenv
echo "freezing env"
pip freeze > /home/jovyan/work/faas_requirements.txt
echo "freeze env done"

