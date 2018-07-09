FROM jupyter/tensorflow-notebook

LABEL maintainer="Mo Project"

USER root

RUN apt-get update && apt-get install -yq graphviz tzdata

# To change the datetime from UTC to Asia/Shanghai
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ADD run.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/run.sh

ADD add_venv.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/add_venv.sh

ADD remove_venv.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/remove_venv.sh

ADD freeze_venv.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/freeze_venv.sh

ADD modules /home/jovyan/modules
RUN chown -R jovyan:users /home/jovyan/modules

ADD dataset /home/jovyan/dataset
RUN chown -R jovyan:users /home/jovyan/dataset

ADD pip.conf /home/jovyan/.pip/pip.conf
RUN chown -R jovyan:users /home/jovyan/.pip

USER $NB_UID

RUN conda install -c eumetsat virtualenvwrapper
ENV VIRTUALENVWRAPPER_PYTHON $CONDA_DIR/bin/python
ENV VIRTUALENVWRAPPER_VIRTUALENV $CONDA_DIR/bin/virtualenv
SHELL ["/bin/bash", "-c"]

RUN source $CONDA_DIR/bin/virtualenvwrapper.sh && \
    mkvirtualenv jlenv && \
    workon jlenv && \
    pip install -U tensorflow opencv-python jupyter && \
    pip install jupyterlab==0.31.1 && \
    toggleglobalsitepackages

CMD ['bash', '/home/jovyan/run.sh']
