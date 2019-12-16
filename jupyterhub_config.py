# Configuration file for jupyterhub.
import os
import jwt
from tornado import gen
from jupyterhub.auth import Authenticator
import hashlib
import sentry_sdk
from sentry_sdk.integrations.tornado import TornadoIntegration

SECRET = 'super-super-secret'
ALGORITHM = 'HS256'
IDENTITY = 'identity'

ENV = 'DEFAULT'
# ENV = 'PROD'
# ENV = 'MO'
# ENV = 'ZJU'
# ENV = 'LOCAL'
# ENV = 'ZKY'
# ENV = 'TEST'

ENV = os.environ.get('ENV', ENV)

origin = '*'

if ENV == 'ZJU':
    SERVER = 'http://10.214.223.202:5005'
    SENTRY_DSN = 'http://941eb6c899504cea8ecbcb4ddd251f64@sentry.momodel.cn:9900/7'
elif ENV == 'ZKY':
    SERVER = 'http://10.3.3.1:5005'
    SENTRY_DSN = 'http://941eb6c899504cea8ecbcb4ddd251f64@sentry.momodel.cn:9900/7'
elif ENV == 'MO':
    SERVER = 'http://192.168.1.79:8899/pyapi'
    SENTRY_DSN = 'http://941eb6c899504cea8ecbcb4ddd251f64@sentry.momodel.cn:9900/7'
elif ENV == 'PROD':
    SERVER = 'http://192.168.31.11:5005'
    SENTRY_DSN = 'http://941eb6c899504cea8ecbcb4ddd251f64@test.local.momodel.cn:9000/7'
elif ENV == 'TEST':
    SERVER = 'http://192.168.31.89:5005'
    SENTRY_DSN = 'http://941eb6c899504cea8ecbcb4ddd251f64@test.local.momodel.cn:9000/7'
else:
    SERVER = 'http://localhost:5005'
    SENTRY_DSN = 'http://941eb6c899504cea8ecbcb4ddd251f64@test.local.momodel.cn:9000/7'

sentry_sdk.init(
    environment=ENV,
    dsn=SENTRY_DSN,
    integrations=[TornadoIntegration()]
)

import base64
from Crypto.Cipher import AES

AKEY = '27cfbc4d262403839797636105d0a476'  # AES key must be either 16, 24, or 32 bytes long

# iv = Random.new().read(AES.block_size)
iv = 'This is an IV456'


def encode(message):
    obj = AES.new(AKEY.encode("utf8"), AES.MODE_CFB, iv.encode("utf8"))
    message = bytes(message, encoding="utf8")
    return base64.urlsafe_b64encode(obj.encrypt(message)).decode("utf-8")


def decode(cipher):
    obj2 = AES.new(AKEY.encode('utf-8'), AES.MODE_CFB, iv.encode('utf-8'))
    if not isinstance(cipher, str):
        cipher = cipher.encode("uft-8")
    return obj2.decrypt(base64.urlsafe_b64decode(cipher))


class SuperSecureAuthenticator(Authenticator):
    @gen.coroutine
    def authenticate(self, handler, data):
        tmp_username = data['username']
        unhash_name = decode(tmp_username).decode('utf-8').split('+')[0]
        # decode token:
        token_data = jwt.decode(data['password'], SECRET, algorithms=[
            ALGORITHM])
        # print(tmp_username, unhash_name, token_data[IDENTITY])
        if token_data[IDENTITY] == unhash_name:
            # if token_data[IDENTITY] == 'zhaofengli':
            # print('user tmp_username:', tmp_username)
            # hash_name = encode(tmp_username)
            # return tmp_username
            return tmp_username

    def normalize_username(self, username):
        """Normalize the given username and return it

        Override in subclasses if usernames need different normalization rules.

        The default attempts to lowercase the username and apply `username_map` if it is
        set.
        """
        # username = username.lower()
        username = self.username_map.get(username, username)
        return username


import sys
import string

from kubespawner import KubeSpawner
from traitlets import default
from kubernetes.client.rest import ApiException
from jupyterhub.utils import exponential_backoff
import escapism

import jupyterhub
import requests


class MyKubeSpawner(KubeSpawner):
    """
    deal with tb and pyls ports, run some shell scripts when starting
    """
    tb_port = 6006
    tb_host = None
    tb_proxy_spec = None
    pyls_port = 3000
    pyls_host = None
    pyls_proxy_spec = None

    # @property
    # def uid(self):
    #     return self.user.id

    @property
    def cmd(self):
        # return ['bash', '/home/jovyan/run.sh', str(self.user.id)]
        return ['bash', '/home/jovyan/run.sh', SERVER, self.user.name]

    def _expand_user_properties(self, template):
        # Make sure username and servername match the restrictions for DNS labels
        # Note: '-' is not in safe_chars, as it is being used as escape character
        safe_chars = set(string.ascii_lowercase + string.digits)
        # Set servername based on whether named-server initialised
        if self.name:
            servername = '-{}'.format(self.name)
            safe_servername = escapism.escape(servername, safe=safe_chars,
                                              escape_char='-').lower()
        else:
            servername = ''
            safe_servername = ''

        legacy_escaped_username = ''.join(
            [s if s in safe_chars else '-' for s in self.user.name.lower()])
        safe_username = escapism.escape(self.user.name,
                                        safe=safe_chars,
                                        escape_char='').lower()
        split_username = self.user.name.split('+')
        # print('split_username:', split_username, self.user.name, self.name)
        if len(split_username) <= 1 and self.user.name != 'admin':
            split_username = decode(self.user.name).decode('utf-8').split('+')
        user_ID = split_username[0]
        if len(split_username) > 1:
            project_name = split_username[1]
        else:
            project_name = user_ID
        return template.format(
            userid=self.user.id,
            username=safe_username,
            user_ID=user_ID,
            project_name=project_name,
            unescaped_username=self.user.name,
            legacy_escape_username=legacy_escaped_username,
            servername=safe_servername,
            unescaped_servername=servername
        )

    # @staticmethod
    # def insert_envs(project_name):
    #     """
    #     add env to jupyterlab
    #     :param tb_port:
    #     :param project_name:
    #     :return: dict of res json
    #     """
    #     return requests.put(f'{SERVER}/apps/insert_envs/{project_name}')
    #
    # @staticmethod
    # def insert_dataset(project_name):
    #     """
    #     mount dataset
    #     :param tb_port:
    #     :param project_name:
    #     :return: dict of res json
    #     """
    #     return requests.put(
    #         f'{SERVER}/project/mount_all_dataset/{project_name}')
    #
    # @staticmethod
    # def install_reset_req(project_name):
    #     """
    #     add env to jupyterlab
    #     :param tb_port:
    #     :param project_name:
    #     :return: dict of res json
    #     """
    #     return requests.put(
    #         f'{SERVER}/project/install_reset_req/{project_name}')

    @gen.coroutine
    def _start(self):
        """Start the user's pod"""
        # record latest event so we don't include old
        # events from previous pods in self.events
        # track by order and name instead of uid
        # so we get events like deletion of a previously stale
        # pod if it's part of this spawn process
        events = self.events
        if events:
            self._last_event = events[-1].metadata.uid

        if self.storage_pvc_ensure:
            # Try and create the pvc. If it succeeds we are good. If
            # returns a 409 indicating it already exists we are good. If
            # it returns a 403, indicating potential quota issue we need
            # to see if pvc already exists before we decide to raise the
            # error for quota being exceeded. This is because quota is
            # checked before determining if the PVC needed to be
            # created.

            pvc = self.get_pvc_manifest()

            try:
                yield self.asynchronize(
                    self.api.create_namespaced_persistent_volume_claim,
                    namespace=self.namespace,
                    body=pvc
                )
            except ApiException as e:
                if e.status == 409:
                    self.log.info(
                        "PVC " + self.pvc_name + " already exists, so did not create new pvc.")

                elif e.status == 403:
                    t, v, tb = sys.exc_info()

                    try:
                        yield self.asynchronize(
                            self.api.read_namespaced_persistent_volume_claim,
                            name=self.pvc_name,
                            namespace=self.namespace)

                    except ApiException as e:
                        raise v.with_traceback(tb)

                    self.log.info(
                        "PVC " + self.pvc_name + " already exists, possibly have reached quota though.")

                else:
                    raise

        # from sys import platform
        # if platform != 'darwin':
        #     host_config.update({'extra_hosts': {
        #         'host.docker.internal': '172.17.0.1'
        #     }})
        # If we run into a 409 Conflict error, it means a pod with the
        # same name already exists. We stop it, wait for it to stop, and
        # try again. We try 4 times, and if it still fails we give up.
        # FIXME: Have better / cleaner retry logic!
        retry_times = 4
        pod = yield self.get_pod_manifest()
        if self.modify_pod_hook:
            pod = yield gen.maybe_future(self.modify_pod_hook(self, pod))
        for i in range(retry_times):
            try:
                # import yaml
                # with open('singleuser.yml', 'w') as stream:
                #     yaml.dump(pod.to_dict(), stream, default_flow_style=False)
                yield self.asynchronize(
                    self.api.create_namespaced_pod,
                    self.namespace,
                    pod,
                )
                break
            except ApiException as e:
                if e.status != 409:
                    # We only want to handle 409 conflict errors
                    self.log.exception("Failed for %s", pod.to_str())
                    raise
                self.log.info('Found existing pod %s, attempting to kill',
                              self.pod_name)
                # TODO: this should show up in events
                yield self.stop(True)

                self.log.info(
                    'Killed pod %s, will try starting singleuser pod again',
                    self.pod_name)
        else:
            raise Exception(
                'Can not create user pod %s already exists & could not be deleted' % self.pod_name)

        # we need a timeout here even though start itself has a timeout
        # in order for this coroutine to finish at some point.
        # using the same start_timeout here
        # essentially ensures that this timeout should never propagate up
        # because the handler will have stopped waiting after
        # start_timeout, starting from a slightly earlier point.
        try:
            yield exponential_backoff(
                lambda: self.is_pod_running(
                    self.pod_reflector.pods.get(self.pod_name, None)),
                'pod/%s did not start in %s seconds!' % (
                    self.pod_name, self.start_timeout),
                timeout=self.start_timeout,
            )
        except TimeoutError:
            if self.pod_name not in self.pod_reflector.pods:
                # if pod never showed up at all,
                # restart the pod reflector which may have become disconnected.
                self.log.error(
                    "Pod %s never showed up in reflector, restarting pod reflector",
                    self.pod_name,
                )
                self._start_watching_pods(replace=True)
            raise

        pod = self.pod_reflector.pods[self.pod_name]
        self.pod_id = pod.metadata.uid
        if self.event_reflector:
            self.log.debug(
                'pod %s events before launch: %s',
                self.pod_name,
                "\n".join(
                    [
                        "%s [%s] %s" % (
                            event.last_timestamp, event.type, event.message)
                        for event in self.events
                    ]
                ),
            )

        # self.insert_envs(self.user.name)
        # self.install_reset_req(self.user.name)
        # self.insert_dataset(self.user.name)

        return (pod.status.pod_ip, self.port)


import os
import json
from subprocess import Popen
from jupyterhub.proxy import ConfigurableHTTPProxy
from tornado.ioloop import PeriodicCallback
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from traitlets import Any

from jupyterhub.objects import Server
from jupyterhub.utils import url_path_join


class MyProxy(ConfigurableHTTPProxy):
    proxy_tb_process = Any()
    proxy_pyls_process = Any()

    tb_public_url = 'http://0.0.0.0:8111'
    tb_api_url = 'http://0.0.0.0:8222'

    pyls_public_url = 'http://0.0.0.0:8333'
    pyls_api_url = 'http://0.0.0.0:8444'

    # @property
    # def tb_public_url(self):
    #     """I'm the 'x' property."""
    #     return 'http{s}://{ip}:{port}{base_url}'.format(
    #         s='s' if self.ssl_cert else '',
    #         ip=self.ip,
    #         port=self.tb_public_port,
    #         base_url=self.base_url,
    #     )

    @gen.coroutine
    def start(self):
        # start tensorboard proxy
        yield self.start_tb_proxy()
        # start pyls proxy
        yield self.start_pyls_proxy()

        public_server = Server.from_url(self.public_url)
        api_server = Server.from_url(self.api_url)
        env = os.environ.copy()
        env['CONFIGPROXY_AUTH_TOKEN'] = self.auth_token
        cmd = self.command + [
            '--ip', public_server.ip,
            '--port', str(public_server.port),
            '--api-ip', api_server.ip,
            '--api-port', str(api_server.port),
            '--error-target', url_path_join(self.hub.url, 'error'),
        ]
        if self.app.subdomain_host:
            cmd.append('--host-routing')
        if self.debug:
            cmd.extend(['--log-level', 'debug'])
        if self.ssl_key:
            cmd.extend(['--ssl-key', self.ssl_key])
        if self.ssl_cert:
            cmd.extend(['--ssl-cert', self.ssl_cert])
        if self.app.statsd_host:
            cmd.extend([
                '--statsd-host', self.app.statsd_host,
                '--statsd-port', str(self.app.statsd_port),
                '--statsd-prefix', self.app.statsd_prefix + '.chp'
            ])
        # Warn if SSL is not used
        if ' --ssl' not in ' '.join(cmd):
            self.log.warning("Running JupyterHub without SSL."
                             "  I hope there is SSL termination happening somewhere else...")
        self.log.info("Starting proxy @ %s", public_server.bind_url)
        self.log.debug("Proxy cmd: %s", cmd)
        shell = os.name == 'nt'
        try:
            self.proxy_process = Popen(cmd, env=env, start_new_session=True,
                                       shell=shell)
        except FileNotFoundError as e:
            self.log.error(
                "Failed to find proxy %r\n"
                "The proxy can be installed with `npm install -g configurable-http-proxy`"
                % self.command
            )
            raise

        def _check_process():
            status = self.proxy_process.poll()
            if status is not None:
                e = RuntimeError(
                    "Proxy failed to start with exit code %i" % status)
                # py2-compatible `raise e from None`
                e.__cause__ = None
                raise e

        for server in (public_server, api_server):
            for i in range(10):
                _check_process()
                try:
                    yield server.wait_up(1)
                except TimeoutError:
                    continue
                else:
                    break
            yield server.wait_up(1)
        _check_process()
        self.log.debug("Proxy started and appears to be up")
        pc = PeriodicCallback(self.check_running,
                              1e3 * self.check_running_interval)
        pc.start()

    @gen.coroutine
    def start_tb_proxy(self):
        public_server = Server.from_url(self.tb_public_url)
        api_server = Server.from_url(self.tb_api_url)
        env = os.environ.copy()
        env['CONFIGPROXY_AUTH_TOKEN'] = self.auth_token
        cmd = self.command + [
            '--ip', public_server.ip,
            '--port', str(public_server.port),
            '--api-ip', api_server.ip,
            '--api-port', str(api_server.port),
            '--error-target', url_path_join(self.hub.url, 'error'),
            '--no-include-prefix',
        ]
        if self.app.subdomain_host:
            cmd.append('--host-routing')
        if self.debug:
            cmd.extend(['--log-level', 'debug'])
        if self.ssl_key:
            cmd.extend(['--ssl-key', self.ssl_key])
        if self.ssl_cert:
            cmd.extend(['--ssl-cert', self.ssl_cert])
        if self.app.statsd_host:
            cmd.extend([
                '--statsd-host', self.app.statsd_host,
                '--statsd-port', str(self.app.statsd_port),
                '--statsd-prefix', self.app.statsd_prefix + '.chp'
            ])
        # Warn if SSL is not used
        if ' --ssl' not in ' '.join(cmd):
            self.log.warning("Running JupyterHub without SSL."
                             "  I hope there is SSL termination happening somewhere else...")
        self.log.info("Starting proxy @ %s", public_server.bind_url)
        self.log.debug("Proxy cmd: %s", cmd)
        shell = os.name == 'nt'
        try:
            self.proxy_tb_process = Popen(cmd, env=env, start_new_session=True,
                                          shell=shell)
        except FileNotFoundError as e:
            self.log.error(
                "Failed to find proxy %r\n"
                "The proxy can be installed with `npm install -g configurable-http-proxy`"
                % self.command
            )
            raise

        def _check_process():
            status = self.proxy_tb_process.poll()
            if status is not None:
                e = RuntimeError(
                    "Proxy failed to start with exit code %i" % status)
                # py2-compatible `raise e from None`
                e.__cause__ = None
                raise e

        for server in (public_server, api_server):
            for i in range(10):
                _check_process()
                try:
                    yield server.wait_up(1)
                except TimeoutError:
                    continue
                else:
                    break
            yield server.wait_up(1)
        _check_process()
        self.log.debug("Proxy started and appears to be up")
        pc = PeriodicCallback(self.check_running,
                              1e3 * self.check_running_interval)
        pc.start()

    @gen.coroutine
    def start_pyls_proxy(self):
        public_server = Server.from_url(self.pyls_public_url)
        api_server = Server.from_url(self.pyls_api_url)
        env = os.environ.copy()
        env['CONFIGPROXY_AUTH_TOKEN'] = self.auth_token
        cmd = self.command + [
            '--ip', public_server.ip,
            '--port', str(public_server.port),
            '--api-ip', api_server.ip,
            '--api-port', str(api_server.port),
            '--error-target', url_path_join(self.hub.url, 'error'),
            '--no-include-prefix',
        ]
        if self.app.subdomain_host:
            cmd.append('--host-routing')
        if self.debug:
            cmd.extend(['--log-level', 'debug'])
        if self.ssl_key:
            cmd.extend(['--ssl-key', self.ssl_key])
        if self.ssl_cert:
            cmd.extend(['--ssl-cert', self.ssl_cert])
        if self.app.statsd_host:
            cmd.extend([
                '--statsd-host', self.app.statsd_host,
                '--statsd-port', str(self.app.statsd_port),
                '--statsd-prefix', self.app.statsd_prefix + '.chp'
            ])
        # Warn if SSL is not used
        if ' --ssl' not in ' '.join(cmd):
            self.log.warning("Running JupyterHub without SSL."
                             "  I hope there is SSL termination happening somewhere else...")
        self.log.info("Starting proxy @ %s", public_server.bind_url)
        self.log.debug("Proxy cmd: %s", cmd)
        shell = os.name == 'nt'
        try:
            self.proxy_pyls_process = Popen(cmd, env=env,
                                            start_new_session=True,
                                            shell=shell)
        except FileNotFoundError as e:
            self.log.error(
                "Failed to find proxy %r\n"
                "The proxy can be installed with `npm install -g configurable-http-proxy`"
                % self.command
            )
            raise

        def _check_process():
            status = self.proxy_pyls_process.poll()
            if status is not None:
                e = RuntimeError(
                    "Proxy failed to start with exit code %i" % status)
                # py2-compatible `raise e from None`
                e.__cause__ = None
                raise e

        for server in (public_server, api_server):
            for i in range(10):
                _check_process()
                try:
                    yield server.wait_up(1)
                except TimeoutError:
                    continue
                else:
                    break
            yield server.wait_up(1)
        _check_process()
        self.log.debug("Proxy started and appears to be up")
        pc = PeriodicCallback(self.check_running,
                              1e3 * self.check_running_interval)
        pc.start()

    def stop(self):
        self.log.info("Cleaning up proxy[%i]...", self.proxy_process.pid)
        if self.proxy_process.poll() is None:
            try:
                self.proxy_process.terminate()
            except Exception as e:
                self.log.error("Failed to terminate proxy process: %s", e)

        self.log.info("Cleaning up tb proxy[%i]...", self.proxy_tb_process.pid)
        if self.proxy_tb_process.poll() is None:
            try:
                self.proxy_tb_process.terminate()
            except Exception as e:
                self.log.error("Failed to terminate tb proxy process: %s", e)

        self.log.info("Cleaning up pyls proxy[%i]...",
                      self.proxy_pyls_process.pid)
        if self.proxy_pyls_process.poll() is None:
            try:
                self.proxy_pyls_process.terminate()
            except Exception as e:
                self.log.error("Failed to terminate pyls proxy process: %s", e)

    @gen.coroutine
    def add_tb(self, user, server_name='', client=None):
        """Add a user's server to the proxy table."""
        spawner = user.spawners[server_name]
        spawner.tb_host = spawner.server.host.replace(
            str(spawner.user.server.port),
            str(spawner.tb_port))
        spawner.tb_proxy_spec = spawner.proxy_spec.replace('/user/', '/tb/')
        self.log.info("Adding user %s's tensorboard to proxy %s => %s",
                      user.name, spawner.tb_proxy_spec, spawner.tb_host,
                      )

        if spawner.pending and spawner.pending != 'spawn':
            raise RuntimeError(
                "%s is pending %s, shouldn't be added to the proxy yet!" % (
                    spawner._log_name, spawner.pending)
            )

        yield self.add_route(
            spawner.tb_proxy_spec,
            spawner.tb_host,
            {
                'user': user.name,
                # 'includePrefix': False,
                # 'prependPath': False
            },
            tb=True
        )

    @gen.coroutine
    def add_pyls(self, user, server_name='', client=None):
        """Add a user's server to the proxy table."""
        spawner = user.spawners[server_name]
        spawner.pyls_host = spawner.server.host.replace(
            str(spawner.user.server.port),
            str(spawner.pyls_port))
        spawner.pyls_proxy_spec = spawner.proxy_spec.replace('/user/',
                                                             '/pyls/')
        self.log.info("Adding user %s's tensorboard to proxy %s => %s",
                      user.name, spawner.pyls_proxy_spec, spawner.pyls_host,
                      )

        if spawner.pending and spawner.pending != 'spawn':
            raise RuntimeError(
                "%s is pending %s, shouldn't be added to the proxy yet!" % (
                    spawner._log_name, spawner.pending)
            )

        yield self.add_route(
            spawner.pyls_proxy_spec,
            spawner.pyls_host,
            {
                'user': user.name,
                # 'includePrefix': False,
                # 'prependPath': False
            },
            pyls=True
        )

    def add_route(self, routespec, target, data, **kwargs):
        if not routespec:
            return
        body = data or {}
        body['target'] = target
        body['jupyterhub'] = True
        path = self._routespec_to_chp_path(routespec)
        if kwargs.get('tb'):
            return self.tb_api_request(path,
                                       method='POST',
                                       body=body,
                                       )
        elif kwargs.get('pyls'):
            return self.pyls_api_request(path,
                                         method='POST',
                                         body=body,
                                         )
        else:
            return self.api_request(path,
                                    method='POST',
                                    body=body,
                                    )

    def tb_api_request(self, path, method='GET', body=None, client=None):
        """Make an authenticated API request of the proxy."""
        client = client or AsyncHTTPClient()
        url = url_path_join(self.tb_api_url, 'api/routes', path)

        if isinstance(body, dict):
            body = json.dumps(body)
        self.log.debug("Proxy: Fetching %s %s", method, url)
        req = HTTPRequest(url,
                          method=method,
                          headers={'Authorization': 'token {}'.format(
                              self.auth_token)},
                          body=body,
                          )

        return client.fetch(req)

    def pyls_api_request(self, path, method='GET', body=None, client=None):
        """Make an authenticated API request of the proxy."""
        client = client or AsyncHTTPClient()
        url = url_path_join(self.pyls_api_url, 'api/routes', path)

        if isinstance(body, dict):
            body = json.dumps(body)
        self.log.debug("Proxy: Fetching %s %s", method, url)
        req = HTTPRequest(url,
                          method=method,
                          headers={'Authorization': 'token {}'.format(
                              self.auth_token)},
                          body=body,
                          )

        return client.fetch(req)

    @gen.coroutine
    def add_user(self, user, server_name='', client=None):
        """Add a user's server to the proxy table."""
        spawner = user.spawners[server_name]
        self.log.info("Adding user %s to proxy %s => %s",
                      user.name, spawner.proxy_spec, spawner.server.host,
                      )

        if spawner.pending and spawner.pending != 'spawn':
            raise RuntimeError(
                "%s is pending %s, shouldn't be added to the proxy yet!" % (
                    spawner._log_name, spawner.pending)
            )

        yield self.add_tb(user)
        yield self.add_pyls(user)

        yield self.add_route(
            spawner.proxy_spec,
            spawner.server.host,
            {
                'user': user.name,
                'server_name': server_name,
            }
        )


from jupyterhub.handlers.base import PrefixRedirectHandler

# c.JupyterHub.init_handlers =
# ------------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
# ------------------------------------------------------------------------------

## This is an application.

## The date format used by logging formatters for %(asctime)s
# c.Application.log_datefmt = '%Y-%m-%d %H:%M:%S'

## The Logging format template
# c.Application.log_format = '[%(name)s]%(highlevel)s %(message)s'

## Set the log level by value or name.
# c.Application.log_level = 30

# ------------------------------------------------------------------------------
# JupyterHub(Application) configuration
# ------------------------------------------------------------------------------

## An Application for starting a Multi-User Jupyter Notebook server.

## Maximum number of concurrent servers that can be active at a time.
#
#  Setting this can limit the total resources your users can consume.
#
#  An active server is any server that's not fully stopped. It is considered
#  active from the time it has been requested until the time that it has
#  completely stopped.
#
#  If this many user servers are active, users will not be able to launch new
#  servers until a server is shutdown. Spawn requests will be rejected with a 429
#  error asking them to try again.
#
#  If set to 0, no limit is enforced.
# c.JupyterHub.active_server_limit = 0

## Grant admin users permission to access single-user servers.
#
#  Users should be properly informed if this is enabled.
c.JupyterHub.admin_access = True

## DEPRECATED since version 0.7.2, use Authenticator.admin_users instead.
# c.JupyterHub.admin_users = set()

## Allow named single-user servers per user
c.JupyterHub.allow_named_servers = True

## Answer yes to any questions (e.g. confirm overwrite)
# c.JupyterHub.answer_yes = False

## PENDING DEPRECATION: consider using service_tokens
#
#  Dict of token:username to be loaded into the database.
#
#  Allows ahead-of-time generation of API tokens for use by externally managed
#  services, which authenticate as JupyterHub users.
#
#  Consider using service_tokens for general services that talk to the JupyterHub
#  API.
# c.JupyterHub.service_tokens = {
#     '1d4afa72b00c4ffd9db82f26e1628f89': 'admin',
# }
c.JupyterHub.api_tokens = {
    '1d4afa72b00c4ffd9db82f26e1628f89': 'admin',
}

## Class for authenticating users.
#
#  This should be a class with the following form:
#
#  - constructor takes one kwarg: `config`, the IPython config object.
#
#  - is a tornado.gen.coroutine
#  - returns username on success, None on failure
#  - takes two arguments: (handler, data),
#    where `handler` is the calling web.RequestHandler,
#    and `data` is the POST form data from the login page.
c.JupyterHub.authenticator_class = SuperSecureAuthenticator
# c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'
# c.JupyterHub.authenticator_class = 'jupyterhub.auth.PAMAuthenticator'
## The base URL of the entire application
c.JupyterHub.base_url = '/hub_api'

## Whether to shutdown the proxy when the Hub shuts down.
#
#  Disable if you want to be able to teardown the Hub while leaving the proxy
#  running.
#
#  Only valid if the proxy was starting by the Hub process.
#
#  If both this and cleanup_servers are False, sending SIGINT to the Hub will
#  only shutdown the Hub, leaving everything else running.
#
#  The Hub should be able to resume from database state.
# c.JupyterHub.cleanup_proxy = True

## Whether to shutdown single-user servers when the Hub shuts down.
#
#  Disable if you want to be able to teardown the Hub while leaving the single-
#  user servers running.
#
#  If both this and cleanup_proxy are False, sending SIGINT to the Hub will only
#  shutdown the Hub, leaving everything else running.
#
#  The Hub should be able to resume from database state.
c.JupyterHub.cleanup_servers = False

## Maximum number of concurrent users that can be spawning at a time.
#
#  Spawning lots of servers at the same time can cause performance problems for
#  the Hub or the underlying spawning system. Set this limit to prevent bursts of
#  logins from attempting to spawn too many servers at the same time.
#
#  This does not limit the number of total running servers. See
#  active_server_limit for that.
#
#  If more than this many users attempt to spawn at a time, their requests will
#  be rejected with a 429 error asking them to try again. Users will have to wait
#  for some of the spawning services to finish starting before they can start
#  their own.
#
#  If set to 0, no limit is enforced.
c.JupyterHub.concurrent_spawn_limit = 200

## The config file to load
# c.JupyterHub.config_file = 'jupyterhub_config.py'

## DEPRECATED: does nothing
# c.JupyterHub.confirm_no_ssl = False

## Number of days for a login cookie to be valid. Default is two weeks.
# c.JupyterHub.cookie_max_age_days = 14

## The cookie secret to use to encrypt cookies.
#
#  Loaded from the JPY_COOKIE_SECRET env variable by default.
#
#  Should be exactly 256 bits (32 bytes).
# c.JupyterHub.cookie_secret = b''

## File in which to store the cookie secret.
# c.JupyterHub.cookie_secret_file = 'jupyterhub_cookie_secret'

## The location of jupyterhub data files (e.g. /usr/local/share/jupyter/hub)
# c.JupyterHub.data_files_path = '/usr/local/share/jupyter/hub'

## Include any kwargs to pass to the database connection. See
#  sqlalchemy.create_engine for details.
# c.JupyterHub.db_kwargs = {}

## url for the database. e.g. `sqlite:///jupyterhub.sqlite`
# c.JupyterHub.db_url = 'sqlite:///jupyterhub.sqlite'

## log all database transactions. This has A LOT of output
# c.JupyterHub.debug_db = False

## DEPRECATED since version 0.8: Use ConfigurableHTTPProxy.debug
c.JupyterHub.debug_proxy = True

## Send JupyterHub's logs to this file.
#
#  This will *only* include the logs of the Hub itself, not the logs of the proxy
#  or any single-user servers.
# c.JupyterHub.extra_log_file = ''

## Extra log handlers to set on JupyterHub logger
# c.JupyterHub.extra_log_handlers = []

## Generate default config file
# c.JupyterHub.generate_config = False

## The ip or hostname for proxies and spawners to use for connecting to the Hub.
#
#  Use when the bind address (`hub_ip`) is 0.0.0.0 or otherwise different from
#  the connect address.
#
#  Default: when `hub_ip` is 0.0.0.0, use `socket.gethostname()`, otherwise use
#  `hub_ip`.
#
#  .. versionadded:: 0.8
# c.JupyterHub.hub_connect_ip = ''

## The port for proxies & spawners to connect to the hub on.
#
#  Used alongside `hub_connect_ip`
#
#  .. versionadded:: 0.8
# c.JupyterHub.hub_connect_port = 0

from jupyter_client.localinterfaces import public_ips

## The ip address for the Hub process to *bind* to.
#
#  See `hub_connect_ip` for cases where the bind and connect address should
#  differ.
# c.JupyterHub.hub_ip = '127.0.0.1'
# c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_ip = public_ips()[0]
# c.JupyterHub.hub_ip = '192.168.32.3'  # upstairs ip
#
## The port for the Hub process
# c.JupyterHub.hub_port = 8081

## The public facing ip of the whole application (the proxy)
# c.JupyterHub.ip = ''
c.JupyterHub.ip = '0.0.0.0'

## Supply extra arguments that will be passed to Jinja environment.
# c.JupyterHub.jinja_environment_options = {}

## Interval (in seconds) at which to update last-activity timestamps.
# c.JupyterHub.last_activity_interval = 300

## Dict of 'group': ['usernames'] to load at startup.
#
#  This strictly *adds* groups and users to groups.
#
#  Loading one set of groups, then starting JupyterHub again with a different set
#  will not remove users or groups from previous launches. That must be done
#  through the API.
# c.JupyterHub.load_groups = {}

## Specify path to a logo image to override the Jupyter logo in the banner.
# c.JupyterHub.logo_file = ''

## File to write PID Useful for daemonizing jupyterhub.
# c.JupyterHub.pid_file = ''

## The public facing port of the proxy
# c.JupyterHub.port = 8000

## DEPRECATED since version 0.8 : Use ConfigurableHTTPProxy.api_url
# c.JupyterHub.proxy_api_ip = ''

## DEPRECATED since version 0.8 : Use ConfigurableHTTPProxy.api_url
# c.JupyterHub.proxy_api_port = 0

## DEPRECATED since version 0.8: Use ConfigurableHTTPProxy.auth_token
# c.JupyterHub.proxy_auth_token = '08ef15eafbe64d82a96938cb22e929ef'

## Interval (in seconds) at which to check if the proxy is running.
# c.JupyterHub.proxy_check_interval = 30

## Select the Proxy API implementation.
# c.JupyterHub.proxy_class = 'jupyterhub.proxy.ConfigurableHTTPProxy'
c.JupyterHub.proxy_class = MyProxy

## DEPRECATED since version 0.8. Use ConfigurableHTTPProxy.command
# c.JupyterHub.proxy_cmd = []

## Purge and reset the database.
# c.JupyterHub.reset_db = False

## Interval (in seconds) at which to check connectivity of services with web
#  endpoints.
# c.JupyterHub.service_check_interval = 60

## Dict of token:servicename to be loaded into the database.
#
#  Allows ahead-of-time generation of API tokens for use by externally managed
#  services.
# c.JupyterHub.service_tokens = {}

## List of service specification dictionaries.
#
#  A service
#
#  For instance::
#
#      services = [
#          {
#              'name': 'cull_idle',
#              'command': ['/path/to/cull_idle_servers.py'],
#          },
#          {
#              'name': 'formgrader',
#              'url': 'http://127.0.0.1:1234',
#              'api_token': 'super-secret',
#              'environment':
#          }
#      ]
# c.JupyterHub.services = []

## The class to use for spawning single-user servers.
#
#  Should be a subclass of Spawner.
# c.JupyterHub.spawner_class = 'jupyterhub.spawner.LocalProcessSpawner'
# c.JupyterHub.spawner_class = MyDockerSpawner
c.JupyterHub.spawner_class = MyKubeSpawner

## Path to SSL certificate file for the public facing interface of the proxy
#
#  When setting this, you should also set ssl_key
# c.JupyterHub.ssl_cert = ''

## Path to SSL key file for the public facing interface of the proxy
#
#  When setting this, you should also set ssl_cert
# c.JupyterHub.ssl_key = ''

## Host to send statsd metrics to
# c.JupyterHub.statsd_host = ''

## Port on which to send statsd metrics about the hub
# c.JupyterHub.statsd_port = 8125

## Prefix to use for all metrics sent by jupyterhub to statsd
# c.JupyterHub.statsd_prefix = 'jupyterhub'

## Run single-user servers on subdomains of this host.
#
#  This should be the full `https://hub.domain.tld[:port]`.
#
#  Provides additional cross-site protections for javascript served by single-
#  user servers.
#
#  Requires `<username>.hub.domain.tld` to resolve to the same host as
#  `hub.domain.tld`.
#
#  In general, this is most easily achieved with wildcard DNS.
#
#  When using SSL (i.e. always) this also requires a wildcard SSL certificate.
# c.JupyterHub.subdomain_host = ''

## Paths to search for jinja templates.
# c.JupyterHub.template_paths = []

## Extra settings overrides to pass to the tornado application.
c.JupyterHub.tornado_settings = {
    'headers': {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS',
        "Access-Control-Allow-Headers": "*",
        "Sec-Fetch-Mode": "cors",
    }
}

## Trust user-provided tokens (via JupyterHub.service_tokens) to have good
#  entropy.
#
#  If you are not inserting additional tokens via configuration file, this flag
#  has no effect.
#
#  In JupyterHub 0.8, internally generated tokens do not pass through additional
#  hashing because the hashing is costly and does not increase the entropy of
#  already-good UUIDs.
#
#  User-provided tokens, on the other hand, are not trusted to have good entropy
#  by default, and are passed through many rounds of hashing to stretch the
#  entropy of the key (i.e. user-provided tokens are treated as passwords instead
#  of random keys). These keys are more costly to check.
#
#  If your inserted tokens are generated by a good-quality mechanism, e.g.
#  `openssl rand -hex 32`, then you can set this flag to True to reduce the cost
#  of checking authentication tokens.
c.JupyterHub.trust_user_provided_tokens = True

## Upgrade the database automatically on start.
#
#  Only safe if database is regularly backed up. Only SQLite databases will be
#  backed up to a local file automatically.
# c.JupyterHub.upgrade_db = False

# ------------------------------------------------------------------------------
# Spawner(LoggingConfigurable) configuration
# ------------------------------------------------------------------------------

## Base class for spawning single-user notebook servers.
#
#  Subclass this, and override the following methods:
#
#  - load_state - get_state - start - stop - poll
#
#  As JupyterHub supports multiple users, an instance of the Spawner subclass is
#  created for each user. If there are 20 JupyterHub users, there will be 20
#  instances of the subclass.

## Extra arguments to be passed to the single-user server.
#
#  Some spawners allow shell-style expansion here, allowing you to use
#  environment variables here. Most, including the default, do not. Consult the
#  documentation for your spawner to verify!

c.Spawner.args = [f'--NotebookApp.allow_origin={origin}']

## The command used for starting the single-user server.
#
#  Provide either a string or a list containing the path to the startup script
#  command. Extra arguments, other than this path, should be provided via `args`.
#
#  This is usually set if you want to start the single-user server in a different
#  python environment (with virtualenv/conda) than JupyterHub itself.
#
#  Some spawners allow shell-style expansion here, allowing you to use
#  environment variables. Most, including the default, do not. Consult the
#  documentation for your spawner to verify!
# c.Spawner.cmd = ['jupyter', 'labhub']
# c.Spawner.cmd = ['bash', '/home/jovyan/run.sh']

## Minimum number of cpu-cores a single-user notebook server is guaranteed to
#  have available.
#
#  If this value is set to 0.5, allows use of 50% of one CPU. If this value is
#  set to 2, allows use of up to 2 CPUs.
#
#  Note that this needs to be supported by your spawner for it to work.
# c.Spawner.cpu_guarantee = None

## Maximum number of cpu-cores a single-user notebook server is allowed to use.
#
#  If this value is set to 0.5, allows use of 50% of one CPU. If this value is
#  set to 2, allows use of up to 2 CPUs.
#
#  The single-user notebook server will never be scheduled by the kernel to use
#  more cpu-cores than this. There is no guarantee that it can access this many
#  cpu-cores.
#
#  This needs to be supported by your spawner for it to work.
# c.Spawner.cpu_limit = None

## Enable debug-logging of the single-user server
# c.Spawner.debug = False

## The URL the single-user server should start in.
#
#  `{username}` will be expanded to the user's username
#
#  Example uses:
#
#  - You can set `notebook_dir` to `/` and `default_url` to `/tree/home/{username}` to allow people to
#    navigate the whole filesystem from their notebook server, but still start in their home directory.
#  - Start with `/notebooks` instead of `/tree` if `default_url` points to a notebook instead of a directory.
#  - You can set this to `/lab` to have JupyterLab start by default, rather than Jupyter Notebook.
c.Spawner.default_url = '/lab'

## Disable per-user configuration of single-user servers.
#
#  When starting the user's single-user server, any config file found in the
#  user's $HOME directory will be ignored.
#
#  Note: a user could circumvent this if the user modifies their Python
#  environment, such as when they have their own conda environments / virtualenvs
#  / containers.
# c.Spawner.disable_user_config = False

## Whitelist of environment variables for the single-user server to inherit from
#  the JupyterHub process.
#
#  This whitelist is used to ensure that sensitive information in the JupyterHub
#  process's environment (such as `CONFIGPROXY_AUTH_TOKEN`) is not passed to the
#  single-user server's process.
# c.Spawner.env_keep = ['PATH', 'PYTHONPATH', 'CONDA_ROOT', 'CONDA_DEFAULT_ENV', 'VIRTUAL_ENV', 'LANG', 'LC_ALL']

## Extra environment variables to set for the single-user server's process.
#
#  Environment variables that end up in the single-user server's process come from 3 sources:
#    - This `environment` configurable
#    - The JupyterHub process' environment variables that are whitelisted in `env_keep`
#    - Variables to establish contact between the single-user notebook and the hub (such as JUPYTERHUB_API_TOKEN)
#
#  The `enviornment` configurable should be set by JupyterHub administrators to
#  add installation specific environment variables. It is a dict where the key is
#  the name of the environment variable, and the value can be a string or a
#  callable. If it is a callable, it will be called with one parameter (the
#  spawner instance), and should return a string fairly quickly (no blocking
#  operations please!).
#
#  Note that the spawner class' interface is not guaranteed to be exactly same
#  across upgrades, so if you are using the callable take care to verify it
#  continues to work after upgrades!
# c.Spawner.environment = {}

## Timeout (in seconds) before giving up on a spawned HTTP server
#
#  Once a server has successfully been spawned, this is the amount of time we
#  wait before assuming that the server is unable to accept connections.
# c.Spawner.http_timeout = 30

## The IP address (or hostname) the single-user server should listen on.
#
#  The JupyterHub proxy implementation should be able to send packets to this
#  interface.
# c.Spawner.ip = ''

## Minimum number of bytes a single-user notebook server is guaranteed to have
#  available.
#
#  Allows the following suffixes:
#    - K -> Kilobytes
#    - M -> Megabytes
#    - G -> Gigabytes
#    - T -> Terabytes
#
#  This needs to be supported by your spawner for it to work.
# c.Spawner.mem_guarantee = None

## Maximum number of bytes a single-user notebook server is allowed to use.
#
#  Allows the following suffixes:
#    - K -> Kilobytes
#    - M -> Megabytes
#    - G -> Gigabytes
#    - T -> Terabytes
#
#  If the single user server tries to allocate more memory than this, it will
#  fail. There is no guarantee that the single-user notebook server will be able
#  to allocate this much memory - only that it can not allocate more than this.
#
#  This needs to be supported by your spawner for it to work.
# c.Spawner.mem_limit = None

## Path to the notebook directory for the single-user server.
#
#  The user sees a file listing of this directory when the notebook interface is
#  started. The current interface does not easily allow browsing beyond the
#  subdirectories in this directory's tree.
#
#  `~` will be expanded to the home directory of the user, and {username} will be
#  replaced with the name of the user.
#
#  Note that this does *not* prevent users from accessing files outside of this
#  path! They can do so with many other means.
# notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
# c.Spawner.notebook_dir = notebook_dir

## An HTML form for options a user can specify on launching their server.
#
#  The surrounding `<form>` element and the submit button are already provided.
#
#  For example:
#
#  .. code:: html
#
#      Set your key:
#      <input name="key" val="default_key"></input>
#      <br>
#      Choose a letter:
#      <select name="letter" multiple="true">
#        <option value="A">The letter A</option>
#        <option value="B">The letter B</option>
#      </select>
#
#  The data from this form submission will be passed on to your spawner in
#  `self.user_options`
# c.Spawner.options_form = ''

## Interval (in seconds) on which to poll the spawner for single-user server's
#  status.
#
#  At every poll interval, each spawner's `.poll` method is called, which checks
#  if the single-user server is still running. If it isn't running, then
#  JupyterHub modifies its own state accordingly and removes appropriate routes
#  from the configurable proxy.
# c.Spawner.poll_interval = 30

## The port for single-user servers to listen on.
#
#  Defaults to `0`, which uses a randomly allocated port number each time.
#
#  If set to a non-zero value, all Spawners will use the same port, which only
#  makes sense if each server is on a different address, e.g. in containers.
#
#  New in version 0.7.
# c.Spawner.port = 0

## An optional hook function that you can implement to do some bootstrapping work
#  before the spawner starts. For example, create a directory for your user or
#  load initial content.
#
#  This can be set independent of any concrete spawner implementation.
#
#  Example::
#
#      from subprocess import check_call
#      def my_hook(spawner):
#          username = spawner.user.name
#          check_call(['./examples/bootstrap-script/bootstrap.sh', username])
#
#      c.Spawner.pre_spawn_hook = my_hook
# c.Spawner.pre_spawn_hook = None

## Timeout (in seconds) before giving up on starting of single-user server.
#
#  This is the timeout for start to return, not the timeout for the server to
#  respond. Callers of spawner.start will assume that startup has failed if it
#  takes longer than this. start should return when the server process is started
#  and its location is known.
# c.Spawner.start_timeout = 60

# ------------------------------------------------------------------------------
# LocalProcessSpawner(Spawner) configuration
# ------------------------------------------------------------------------------

## A Spawner that uses `subprocess.Popen` to start single-user servers as local
#  processes.
#
#  Requires local UNIX users matching the authenticated users to exist. Does not
#  work on Windows.
#
#  This is the default spawner for JupyterHub.

## Seconds to wait for single-user server process to halt after SIGINT.
#
#  If the process has not exited cleanly after this many seconds, a SIGTERM is
#  sent.
# c.LocalProcessSpawner.interrupt_timeout = 10

## Seconds to wait for process to halt after SIGKILL before giving up.
#
#  If the process does not exit cleanly after this many seconds of SIGKILL, it
#  becomes a zombie process. The hub process will log a warning and then give up.
# c.LocalProcessSpawner.kill_timeout = 5

## Extra keyword arguments to pass to Popen
#
#  when spawning single-user servers.
#
#  For example::
#
#      popen_kwargs = dict(shell=True)
# c.LocalProcessSpawner.popen_kwargs = {}

## Seconds to wait for single-user server process to halt after SIGTERM.
#
#  If the process does not exit cleanly after this many seconds of SIGTERM, a
#  SIGKILL is sent.
# c.LocalProcessSpawner.term_timeout = 5

# ------------------------------------------------------------------------------
# Authenticator(LoggingConfigurable) configuration
# ------------------------------------------------------------------------------

## Base class for implementing an authentication provider for JupyterHub

## Set of users that will have admin rights on this JupyterHub.
#
#  Admin users have extra privileges:
#   - Use the admin panel to see list of users logged in
#   - Add / remove users in some authenticators
#   - Restart / halt the hub
#   - Start / stop users' single-user servers
#   - Can access each individual users' single-user server (if configured)
#
#  Admin access should be treated the same way root access is.
#
#  Defaults to an empty set, in which case no user has admin access.
c.Authenticator.admin_users = {'admin'}

## Automatically begin the login process
#
#  rather than starting with a "Login with..." link at `/hub/login`
#
#  To work, `.login_url()` must give a URL other than the default `/hub/login`,
#  such as an oauth handler or another automatic login handler, registered with
#  `.get_handlers()`.
#
#  .. versionadded:: 0.8
# c.Authenticator.auto_login = False

## Enable persisting auth_state (if available).
#
#  auth_state will be encrypted and stored in the Hub's database. This can
#  include things like authentication tokens, etc. to be passed to Spawners as
#  environment variables.
#
#  Encrypting auth_state requires the cryptography package.
#
#  Additionally, the JUPYTERHUB_CRYPTO_KEY envirionment variable must contain one
#  (or more, separated by ;) 32B encryption keys. These can be either base64 or
#  hex-encoded.
#
#  If encryption is unavailable, auth_state cannot be persisted.
#
#  New in JupyterHub 0.8
# c.Authenticator.enable_auth_state = False

## Dictionary mapping authenticator usernames to JupyterHub users.
#
#  Primarily used to normalize OAuth user names to local users.
# c.Authenticator.username_map = {}

## Regular expression pattern that all valid usernames must match.
#
#  If a username does not match the pattern specified here, authentication will
#  not be attempted.
#
#  If not set, allow any username.
# c.Authenticator.username_pattern = ''

## Whitelist of usernames that are allowed to log in.
#
#  Use this with supported authenticators to restrict which users can log in.
#  This is an additional whitelist that further restricts users, beyond whatever
#  restrictions the authenticator has in place.
#
#  If empty, does not perform any additional restriction.
# c.Authenticator.whitelist = set()

# ------------------------------------------------------------------------------
# LocalAuthenticator(Authenticator) configuration
# ------------------------------------------------------------------------------

## Base class for Authenticators that work with local Linux/UNIX users
#
#  Checks for local users, and can attempt to create them if they exist.

## The command to use for creating users as a list of strings
#
#  For each element in the list, the string USERNAME will be replaced with the
#  user's username. The username will also be appended as the final argument.
#
#  For Linux, the default value is:
#
#      ['adduser', '-q', '--gecos', '""', '--disabled-password']
#
#  To specify a custom home directory, set this to:
#
#      ['adduser', '-q', '--gecos', '""', '--home', '/customhome/USERNAME', '--
#  disabled-password']
#
#  This will run the command:
#
#      adduser -q --gecos "" --home /customhome/river --disabled-password river
#
#  when the user 'river' is created.
# c.LocalAuthenticator.add_user_cmd = []

## If set to True, will attempt to create local system users if they do not exist
#  already.
#
#  Supports Linux and BSD variants only.
# c.LocalAuthenticator.create_system_users = False

## Whitelist all users from this UNIX group.
#
#  This makes the username whitelist ineffective.
# c.LocalAuthenticator.group_whitelist = set()

# ------------------------------------------------------------------------------
# PAMAuthenticator(LocalAuthenticator) configuration
# ------------------------------------------------------------------------------

## Authenticate local UNIX users with PAM

## The text encoding to use when communicating with PAM
# c.PAMAuthenticator.encoding = 'utf8'

## Whether to open a new PAM session when spawners are started.
#
#  This may trigger things like mounting shared filsystems, loading credentials,
#  etc. depending on system configuration, but it does not always work.
#
#  If any errors are encountered when opening/closing PAM sessions, this is
#  automatically set to False.
# c.PAMAuthenticator.open_sessions = True

## The name of the PAM service to use for authentication
# c.PAMAuthenticator.service = 'login'

# ------------------------------------------------------------------------------
# CryptKeeper(SingletonConfigurable) configuration
# ------------------------------------------------------------------------------

## Encapsulate encryption configuration
#
#  Use via the encryption_config singleton below.

##
# c.CryptKeeper.keys = []

## The number of threads to allocate for encryption
# c.CryptKeeper.n_threads = 8

# import os
#
# cwd = os.getcwd()
# user_path = os.path.abspath(cwd). \
#     replace('jupyterhub', 'user_directory/{user_ID}/{project_name}')


# dev
if ENV in ['MO', 'ZJU', 'ZKY']:
    c.KubeSpawner.image_spec = 'magicalion/singleuser:latest'
else:
    c.KubeSpawner.image_spec = 'magicalion/singleuser:dev'

# gpu machine
# c.DockerSpawner.image = 'magicalion/singleuser:latest-gpu'
# c.DockerSpawner.extra_host_config = {
#     'runtime': 'nvidia',
# }

c.KubeSpawner.service_account = 'default'
# c.KubeSpawner.namespace = 'jupyter'

volume_name = 'notebook-volume-{userid}'
c.KubeSpawner.start_timeout = 60 * 5
c.KubeSpawner.http_timeout = 60 * 5
# c.JupyterHub.slow_spawn_timeout = 60 * 5
c.KubeSpawner.uid = 1000
c.KubeSpawner.gid = 100
c.KubeSpawner.fs_gid = 100
CLAIM_NAME = 'nfs-pvc-user-dir'
if ENV == 'DEFAULT':
    c.KubeSpawner.environment = {
        'PY_SERVER': 'http://{ip}:8899/pyapi'.format(ip=public_ips()[0])
        # 'PY_SERVER': 'http://{ip}:8899/pyapi'.format(ip='192.168.32.3')  # upstairs ip
    }
    CLAIM_NAME = 'nfs-pvc-user-dir-dev'
    USER_DIRECTORY = 'user_directory_dev'
elif ENV == 'PROD':
    c.KubeSpawner.environment = {
        'PY_SERVER': 'http://192.168.31.11:8899/pyapi'
    }
    USER_DIRECTORY = 'user_directory'
elif ENV == 'MO':
    c.KubeSpawner.environment = {
        'PY_SERVER': 'http://36.26.77.39:8899/pyapi'
    }
    USER_DIRECTORY = 'user_directory'
elif ENV == 'ZJU':
    c.KubeSpawner.environment = {
        'PY_SERVER': 'http://10.214.223.221:8899/pyapi'
    }
    USER_DIRECTORY = 'user_directory'
elif ENV == 'ZKY':
    c.KubeSpawner.environment = {
        'PY_SERVER': 'http://10.3.3.2:8899/pyapi'
    }
    USER_DIRECTORY = 'user_directory'
elif ENV == 'TEST':
    c.KubeSpawner.environment = {
        'PY_SERVER': 'http://192.168.31.89:8899/pyapi'
    }
    USER_DIRECTORY = 'user_directory'
c.KubeSpawner.extra_container_config = {
    'ports': [
        {
            'containerPort': 8888,
            'name': 'notebook-port'
        },
        {
            'containerPort': 6006,
            'name': 'tb-port'
        },
        {
            'containerPort': 3000,
            'name': 'pyls-port'
        },
    ],
    # "securityContext": {
    #     "privileged": True,
    # },
    'resources': {
        'limits': {
            'cpu': '1',
            'memory': '4Gi'
        },
        'requests': {
            'cpu': '0.2',
            'memory': '500Mi'
        }
    }
}


c.KubeSpawner.extra_pod_config = {
    'hostname': 'notebook',
}

if ENV in ['MO']:
    c.KubeSpawner.extra_pod_config['nodeSelector'] = {
        # run notebooks on cpu nodes
        'accelerator': 'non-gpu'
    }

# c.DockerSpawner.remove_containers = True
# c.DockerSpawner.container_ip = '0.0.0.0'
# c.DockerSpawner.host_ip = '0.0.0.0'
c.KubeSpawner.volume_mounts = [
    {
        "mountPath": "/home/jovyan/work/",
        "name": volume_name,
        # "subPath": '{user_ID}/{project_name}',
        "mount_propagation": 'HostToContainer',
    },
]
c.KubeSpawner.volumes = [
    {
        "name": volume_name,
        # "persistentVolumeClaim": {
        #     "claimName": CLAIM_NAME
        # }
        'hostPath': {
            # directory location on host
            'path': '/mnt/' + USER_DIRECTORY + '/{user_ID}/{project_name}',
            # this field is optional
            'type': 'Directory',
        }
    }
]

# NOTE:  sudo route -n add -net 172.16.0.0/16 192.168.31.11
