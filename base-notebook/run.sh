#!/usr/bin/env bash
WORK=/home/jovyan/work
#ls -la
#export WORKON_HOME=$WORK/.virtualenvs

export VIRTUALENVWRAPPER_PYTHON=/opt/conda/bin/python
export VIRTUALENVWRAPPER_VIRTUALENV=/opt/conda/bin/virtualenv
source /opt/conda/bin/virtualenvwrapper.sh

#lsvirtualenv
#mktmpenv
#toggleglobalsitepackages
/home/jovyan/.virtualenvs/jlenv/bin/tensorboard --logdir=${WORK}/logs --host=0.0.0.0 &
/home/jovyan/.virtualenvs/jlenv/bin/jupyter labhub --ip=0.0.0.0 --NotebookApp.allow_origin=* --NotebookApp.token='' --NotebookApp.notebook_dir=${WORK}
#python3 -m http.server 8888