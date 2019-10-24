#!/usr/bin/env bash
export WORK=/home/jovyan/work

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

export WORKON_HOME=${WORK}

workon .localenv

cd /home/jovyan/pyls && npm run start:ext
