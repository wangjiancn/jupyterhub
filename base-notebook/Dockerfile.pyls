FROM magicalion/singleuser:build

USER root

ADD pyls /home/jovyan/pyls
RUN chown -R jovyan:users /home/jovyan/pyls

ADD run_pyls.sh /home/jovyan
RUN chown jovyan:users /home/jovyan/run_pyls.sh


USER jovyan

RUN cd /home/jovyan/pyls && npm i && npm run build && cd -


USER root

EXPOSE 3111
WORKDIR /home/jovyan/work


CMD 'bash' '/home/jovyan/run_pyls.sh'

