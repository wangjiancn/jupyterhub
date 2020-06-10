#!/usr/bin/env bash
PREFIX=faas
if [ ${1} ] ; then
    PREFIX=${1}
fi

M_DIR=/home/jovyan/work
REQ_TXT=/home/jovyan/work/${PREFIX}_requirements.txt

if [ ! -e ${REQ_TXT}  ]  ; then
    echo "No such file: $REQ_TXT"
    exit
fi

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

# create module env
export WORKON_HOME=${M_DIR}
#mkvirtualenv .localenv --system-site-packages
workon .localenv
# install packages
pip install -r ${REQ_TXT}

if [ ${1} == reset ] ; then
    rm ${REQ_TXT}
fi
