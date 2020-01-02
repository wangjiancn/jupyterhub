FROM pyserver:latest
USER root

RUN npm i configurable-http-proxy -g

WORKDIR /home/admin/www/mo_prod/py_server/jupyterhub

ADD . .

RUN chown -R admin:admin /home/admin/www/mo_prod/py_server/jupyterhub
RUN chown -R admin:admin /opt/app-root/src

USER admin
