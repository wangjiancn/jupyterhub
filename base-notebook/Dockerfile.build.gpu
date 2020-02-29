FROM tensorflow/tensorflow:1.13.1-gpu-py3

LABEL maintainer="Mo Model Team"

USER root

# fix nvidia repo connection inside GFW
RUN rm -f /etc/apt/sources.list.d/cuda.list
RUN rm -f /etc/apt/sources.list.d/nvidia-ml.list
RUN apt-get update && apt-get install -yq apt-utils apt-transport-https
ADD cuda.list /etc/apt/sources.list.d/cuda.list
ADD nvidia-ml.list /etc/apt/sources.list.d/nvidia-ml.list

RUN apt-get update && apt-get install -yq curl
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
# To change the datetime from UTC to Asia/Shanghai
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -yq graphviz tzdata nano vim wget git python3-tk nodejs pandoc texlive-xetex texlive-generic-extra texlive-lang-cjk \
&& apt-get clean && rm -rf /var/lib/apt/lists/*
# After install node, python2 will be installed
# move back python3 to be default python
#RUN ln -snf /usr/bin/python3 /usr/bin/python
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
ENV LANG=C.UTF-8

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

ADD pip.conf /home/jovyan/.pip/pip.conf
RUN chown -R jovyan:users /home/jovyan/.pip

ADD base_requirements.txt .
RUN pip --default-timeout=100 install -r base_requirements.txt

USER $NB_UID

# Setup work directory for backward-compatibility
RUN mkdir /home/$NB_USER/work && \
    fix-permissions /home/$NB_USER

ENV VIRTUALENVWRAPPER_PYTHON $USR_DIR/bin/python3
ENV VIRTUALENVWRAPPER_VIRTUALENV $LOCAL_DIR/bin/virtualenv
SHELL ["/bin/bash", "-c"]

ADD requirements.txt .

RUN source $LOCAL_DIR/bin/virtualenvwrapper.sh && \
    mkvirtualenv jlenv && \
    workon jlenv && \
    pip --default-timeout=100 install pip==19.1.1 jupyterlab==1.0.0a1 -i https://pypi.python.org/simple && \
    toggleglobalsitepackages && \
    #make basenv
    mkvirtualenv basenv && \
    workon basenv && \
    pip --default-timeout=100 install -U opencv-python nltk notebook seaborn keras Cython && \
    pip --default-timeout=100 install -r requirements.txt && \
    pip --default-timeout=100 install jupyterhub==1.0.0 pip==19.1.1 && \
    pip --default-timeout=100 install torch==1.3.0 torchvision==0.4.1 && \
    toggleglobalsitepackages


# support export PDF with chinese char
RUN sed -i 's/\\documentclass\[11pt\]{article}/\\documentclass[11pt]{ctexart}/g' /home/jovyan/.virtualenvs/basenv/lib/python3.5/site-packages/nbconvert/templates/latex/article.tplx

USER root

ADD SimHei.ttf .
RUN chown jovyan:users /SimHei.ttf
RUN mv SimHei.ttf /home/jovyan/.virtualenvs/basenv/lib/python3.5/site-packages/matplotlib/mpl-data/fonts/ttf
RUN echo 'font.sans-serif: SimHei' >> /home/jovyan/.virtualenvs/basenv/lib/python3.5/site-packages/matplotlib/mpl-data/matplotlibrc

ADD run.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/run.sh

ADD run_tb.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/run_tb.sh

ADD add_venv.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/add_venv.sh

ADD install_venv.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/install_venv.sh

ADD remove_venv.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/remove_venv.sh

ADD freeze_venv.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/freeze_venv.sh

ADD modules /home/jovyan/modules
RUN chown -R jovyan:users /home/jovyan/modules

ADD dataset /home/jovyan/dataset
RUN chown -R jovyan:users /home/jovyan/dataset

ADD build.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/build.sh

ADD update_jl.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/update_jl.sh

USER $NB_UID

EXPOSE 8888
WORKDIR /home/$NB_USER/work

CMD ['bash', '/home/jovyan/build.sh']
