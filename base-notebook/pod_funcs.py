# -*- coding: UTF-8 -*-
import sys
import requests
import os

func_name = sys.argv[1]
project_name = sys.argv[2]
env = os.environ
py_server = env['PY_SERVER']


def insert_envs():
    """
    add env to jupyterlab
    :param tb_port:
    :param project_name:
    :return: dict of res json
    """
    return requests.put(f'{py_server}/apps/insert_envs/{project_name}')


def insert_dataset():
    """
    mount dataset
    :param tb_port:
    :param project_name:
    :return: dict of res json
    """
    return requests.put(
        f'{py_server}/project/mount_all_dataset/{project_name}')


def install_reset_req():
    """
    add env to jupyterlab
    :param tb_port:
    :param project_name:
    :return: dict of res json
    """
    return requests.put(
        f'{py_server}/project/install_reset_req/{project_name}')


def run_all():
    """
    exec all above
    :return:
    """
    insert_envs()
    insert_dataset()
    install_reset_req()


locals().get(func_name)()
