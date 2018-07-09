#!/usr/bin/env bash
M_DIR=/home/jovyan/modules/${1}
W_DIR=/home/jovyan
PACKAGE_DIR=${M_DIR}/mynewenv/lib/python3.6/site-packages

export VIRTUALENVWRAPPER_PYTHON=/opt/conda/bin/python3.6
export VIRTUALENVWRAPPER_VIRTUALENV=/opt/conda/bin/virtualenv
source /opt/conda/bin/virtualenvwrapper.sh

if [ ! -d ${M_DIR}  ] || [ ! -d ${PACKAGE_DIR} ] ; then
    echo "No such directory: $M_DIR"
    exit
fi

cd ${W_DIR}
echo "activating env"
# FIXME will only work when one workon, like now
workon jlenv
echo "removing env"
add2virtualenv -d ${PACKAGE_DIR}
echo "remove env done"


