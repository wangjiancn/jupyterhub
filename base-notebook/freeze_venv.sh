#!/usr/bin/env bash

export VIRTUALENVWRAPPER_PYTHON=/opt/conda/bin/python3.6
export VIRTUALENVWRAPPER_VIRTUALENV=/opt/conda/bin/virtualenv
source /opt/conda/bin/virtualenvwrapper.sh

workon jlenv
echo "freezing env"
pip freeze > /home/jovyan/work/faas_requirements.txt
echo "freeze env done"

