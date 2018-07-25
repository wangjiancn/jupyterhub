FROM tensorflow/tensorflow:latest-py3

LABEL maintainer="Mo Model Team"

USER root

RUN apt-get update

# To change the datetime from UTC to Asia/Shanghai
RUN apt-get install -yq graphviz tzdata nano vim wget
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Configure environment
ENV USR_DIR=/usr \
    LOCAL_DIR=/usr/local \
    SHELL=/bin/bash \
    NB_USER=jovyan \
    NB_UID=1000 \
    NB_GID=100
ENV PATH=$LOCAL_DIR/bin:$PATH \
    HOME=/home/$NB_USER

ADD fix-permissions /usr/local/bin/fix-permissions
# Create jovyan user with UID=1000 and in the 'users' group
# and make sure these dirs are writable by the `users` group.
RUN groupadd wheel -g 11 && \
    echo "auth required pam_wheel.so use_uid" >> /etc/pam.d/su && \
    useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && \
    mkdir -p $LOCAL_DIR && \
    chown $NB_USER:$NB_GID $LOCAL_DIR && \
    chmod g+w /etc/passwd && \
    fix-permissions $HOME && \
    fix-permissions $LOCAL_DIR

ADD run.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/run.sh

ADD add_venv.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/add_venv.sh

#ADD install_venv.sh /home/jovyan
#RUN chown jovyan:users /home/jovyan/install_venv.sh

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

RUN pip install virtualenvwrapper virtualenv-clone

USER $NB_UID

# Setup work directory for backward-compatibility
RUN mkdir /home/$NB_USER/work && \
    fix-permissions /home/$NB_USER

ENV VIRTUALENVWRAPPER_PYTHON $USR_DIR/bin/python
ENV VIRTUALENVWRAPPER_VIRTUALENV $LOCAL_DIR/bin/virtualenv
SHELL ["/bin/bash", "-c"]

RUN source $LOCAL_DIR/bin/virtualenvwrapper.sh && \
    mkvirtualenv jlenv && \
    workon jlenv && \
    pip install -U opencv-python notebook && \
    pip install jupyterhub==0.8.1 jupyterlab==0.31.1 && \
    toggleglobalsitepackages

EXPOSE 8888
WORKDIR /home/$NB_USER/work

CMD ['bash', '/home/jovyan/run.sh']
