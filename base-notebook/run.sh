#!/usr/bin/env bash
export WORK=/home/jovyan/work

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh

export WORKON_HOME=${WORK}

workon .localenv

#echo 0 `date`
#if [ ! -e ${WORK}/.localenv  ] ; then
#    virtualenv-clone /home/jovyan/.virtualenvs/jlenv ${WORK}/.localenv
#fi
#echo 1 `date`
##mkvirtualenv .localenv
#workon .localenv
#echo 2 `date`
#
#add2virtualenv /home/jovyan/.virtualenvs/basenv/lib/python3.5/site-packages

#echo 3 `date`

#tensorboard --logdir=${WORK}/results/tb_results --host=0.0.0.0 &
cd /home/jovyan/pyls && npm run start:ext &
${WORK}/.localenv/bin/jupyter labhub --ip=0.0.0.0 --NotebookApp.allow_origin=* --NotebookApp.disable_check_xsrf=True --NotebookApp.iopub_data_rate_limit=10000000000 \
--NotebookApp.notebook_dir=${WORK} --NotebookApp.default_dir=/lab/tree/OVERVIEW.md
