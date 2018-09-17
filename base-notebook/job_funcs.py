# -*- coding: UTF-8 -*-
import sys
import requests

ENV = 'DEV'
# ENV = 'PROD'
# ENV = 'MO'

if ENV == 'DEV':
    PY_SERVER = 'http://192.168.31.23:8899/pyapi'
    # PY_SERVER = 'http://192.168.31.23:8899/pyapi'
elif ENV == 'PROD':
    PY_SERVER = 'http://momodel-ai.s3.natapp.cc/pyapi'
elif ENV == 'MO':
    PY_SERVER = 'http://36.26.77.39:8899/pyapi'
else:
    PY_SERVER = 'htto://127.0.0.1:8899/pyapi'

func_name = sys.argv[1]
job_id = sys.argv[2]
try:
    if_success = sys.argv[3]
except IndexError:
    pass


def finish_job():
    requests.put('{PY_SERVER}/jobs/{job_id}/finish/{if_success}'.format(
        PY_SERVER=PY_SERVER, job_id=job_id, if_success=if_success))


def insert_module():
    requests.put('{PY_SERVER}/jobs/{job_id}/insert_modules'.format(
        PY_SERVER=PY_SERVER, job_id=job_id))


locals().get(func_name)()
