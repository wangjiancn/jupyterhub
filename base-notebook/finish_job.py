# -*- coding: UTF-8 -*-
import sys
import requests

ENV = 'DEV'
# ENV = 'PROD'
# ENV = 'MO'

if ENV == 'DEV':
    PY_SERVER = 'http://192.168.31.23:8899/pyapi'
elif ENV == 'PROD':
    PY_SERVER = 'http://momodel-ai.s3.natapp.cc/pyapi'
elif ENV == 'MO':
    PY_SERVER = 'http://36.26.77.39:8899/pyapi'
else:
    PY_SERVER = 'htto://127.0.0.1:8899/pyapi'

job_id = sys.argv[1]
if_success = sys.argv[2]
requests.put('{PY_SERVER}/jobs/{job_id}/finish/{if_success}'.format(
    PY_SERVER=PY_SERVER, job_id=job_id, if_success=if_success))
