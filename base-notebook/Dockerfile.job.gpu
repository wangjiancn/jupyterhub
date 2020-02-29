FROM magicalion/singleuser:build-gpu

USER $NB_UID

EXPOSE 8888
WORKDIR /home/$NB_USER/work

USER root

ADD sc.py /usr/lib/python3.5/sitecustomize.py

ADD run_job.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/run_job.sh

ADD job_funcs.py /home/jovyan
RUN chown jovyan:users /home/jovyan/job_funcs.py

# insert localenv path
ENV ENV_PATH=${HOME}/.virtualenvs/basenv
ENV WORK=/home/jovyan/work
ENV path_file=${ENV_PATH}/lib/python3.5/site-packages/_virtualenv_path_extensions.pth
RUN echo "import sys; sys.__plen = len(sys.path)" > "$path_file"
RUN echo ${HOME}/.virtualenvs/jlenv/lib/python3.5/site-packages >> "$path_file"
RUN echo ${WORK}/.localenv/lib/python3.5/site-packages >> "$path_file"
RUN echo "import sys; new=sys.path[sys.__plen:]; del sys.path[sys.__plen:]; p=getattr(sys,'__egginsert',0); sys.path[p:p]=new; sys.__egginsert = p+len(new)" >> "$path_file"

CMD ['bash', '/home/jovyan/run_job.sh']
