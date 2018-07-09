#!/usr/bin/env bash
M_DIR=/home/jovyan/modules/${1}
W_DIR=/home/jovyan
PACKAGE_DIR=${M_DIR}/mynewenv/lib/python3.6/site-packages

export VIRTUALENVWRAPPER_PYTHON=/opt/conda/bin/python
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
echo "adding env"
add2virtualenv ${PACKAGE_DIR}
echo "add env done"


