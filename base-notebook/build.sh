#!/usr/bin/env bash
# script to build '.localenv'
export WORK=/home/jovyan/work
export path_file=${WORK}/.localenv/lib/python3.5/site-packages/_virtualenv_path_extensions.pth

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

export WORKON_HOME=${WORK}

virtualenv-clone /home/jovyan/.virtualenvs/jlenv ${WORK}/.localenv

workon .localenv

echo "import sys; sys.__plen = len(sys.path)" > "$path_file"
echo "/home/jovyan/.virtualenvs/basenv/lib/python3.5/site-packages" >> "$path_file"
echo "import sys; new=sys.path[sys.__plen:]; del sys.path[sys.__plen:]; p=getattr(sys,'__egginsert',0); sys.path[p:p]=new; sys.__egginsert = p+len(new)" >> "$path_file"
