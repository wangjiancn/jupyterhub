#!/usr/bin/env bash
export WORK=/home/jovyan/work

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

export WORKON_HOME=${WORK}
if [ ! -e ${WORK}/.localenv  ] ; then
    ls -l ${WORK}
    virtualenv-clone /home/jovyan/.virtualenvs/jlenv ${WORK}/.localenv
fi
#mkvirtualenv .localenv
workon .localenv

tensorboard --logdir=${WORK}/logs --host=0.0.0.0 &
${WORK}/.localenv/bin/jupyter labhub --ip=0.0.0.0 --NotebookApp.allow_origin=* --NotebookApp.notebook_dir=${WORK}
#python3 -m http.server 8888