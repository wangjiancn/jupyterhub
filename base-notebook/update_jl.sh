#!/usr/bin/env bash
# script to build '.localenv'
export WORK=/home/jovyan/work
export path_file=${WORK}/.localenv/lib/python3.5/site-packages/_virtualenv_path_extensions.pth

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

export WORKON_HOME=${WORK}

workon .localenv

pip install -U jupyterlab==1.0.0a1 -i https://pypi.python.org/simple
