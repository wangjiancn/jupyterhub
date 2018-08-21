#!/usr/bin/env bash
M_DIR=/home/jovyan/modules/${1}
WORK=/home/jovyan/work
PACKAGE_DIR=${M_DIR}/.localenv/lib/python3.5/site-packages

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

if [ ! -d ${M_DIR}  ] || [ ! -d ${PACKAGE_DIR} ] ; then
    echo "No such directory: $M_DIR"
    exit
fi

export WORKON_HOME=${WORK}
echo "activating env"
# FIXME will only work when one workon, like now
workon .localenv
echo "removing env"
add2virtualenv -d ${PACKAGE_DIR}
echo "remove env done"


