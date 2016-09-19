import json
import logging
from urlparse import urlparse, urljoin
import requests
import kpm
from kpm.auth import KpmAuth
from kpm.discovery import ishosted, discover_sources

__all__ = ['Registry']

logger = logging.getLogger(__name__)
DEFAULT_REGISTRY = 'http://localhost:5000'
API_PREFIX = '/api/v1'


class Registry(object):
    def __init__(self, endpoint=DEFAULT_REGISTRY):
        if endpoint is None:
            endpoint = DEFAULT_REGISTRY
        self.endpoint = urlparse(endpoint)
        self.auth = KpmAuth()
        self._headers = {'Content-Type': 'application/json',
                         'User-Agent': "kpmpy-cli: %s" % kpm.__version__}

    def _url(self, path, prefix=API_PREFIX):
        return urljoin(self.endpoint.geturl(), self.endpoint.path + prefix + path)

    @property
    def headers(self):
        token = self.auth.token
        headers = {}
        headers.update(self._headers)
        if token is not None:
            headers['Authorization'] = token
        return headers

    def version(self):
        path = "/version"
        r = requests.get(self._url(path, prefix=""), headers=self.headers)
        r.raise_for_status()
        return r.json()

    def pull(self, name, version=None):
        if ishosted(name):
            sources = discover_sources(name)
            path = sources[0]
        else:
            organization, name = name.split("/")
            path = self._url("/packages/%s/%s/pull" % (organization, name))
        params = {"version": version}
        r = requests.get(path, params=params, headers=self.headers)
        r.raise_for_status()
        return r.content

    def list_packages(self, user=None, organization=None):
        path = "/packages"
        params = {}
        if user:
            params['username'] = user
        if organization:
            params["organization"] = organization
        r = requests.get(self._url(path), params=params, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def generate(self, name, namespace=None,
                 variables=None, version=None, tarball=False,
                 shards=None):
        path = "/packages/%s/generate" % name
        params = {}
        body = {}
        if tarball:
            params['tarball'] = 'true'
        if version:
            params['version'] = version
        if namespace:
            params['namespace'] = namespace
        if variables:
            body['variables'] = variables
        if shards:
            body['shards'] = shards
        r = requests.get(self._url(path), data=json.dumps(body), params=params, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def push(self, name, body, force=False):
        organization, pname = name.split("/")
        body['name'] = pname
        body['organization'] = organization
        body['package'] = name
        path = "/packages/%s/%s" % (organization, pname)
        r = requests.post(self._url(path),
                          params={"force": str(force).lower()},
                          data=json.dumps(body), headers=self.headers)
        r.raise_for_status()
        return r.json()

    def login(self, username, password):
        path = "/users/login"
        self.auth.delete_token()
        r = requests.post(self._url(path),
                          data=json.dumps({"user": {"username": username, "password": password}}),
                          headers=self.headers)
        r.raise_for_status()
        result = r.json()
        self.auth.token = result['token']
        return result

    def signup(self, username, password, password_confirmation, email):
        path = "/users"
        self.auth.delete_token()
        r = requests.post(self._url(path),
                          data=json.dumps({"user": {"username": username,
                                                    "password": password,
                                                    "password_confirmation": password_confirmation,
                                                    "email": email}}),
                          headers=self.headers)
        r.raise_for_status()
        result = r.json()
        self.auth.token = result['token']
        return result

    def delete_package(self, name, version=None):
        organization, name = name.split("/")
        path = "/packages/%s/%s" % (organization, name)
        params = {}
        if version:
            params['version'] = version
        r = requests.delete(self._url(path), params=params, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def _crud_channel(self, name, channel='', action='get'):
        if channel is None:
            channel = ''
        path = "/packages/%s/channels/%s" % (name, channel)
        r = getattr(requests, action)(self._url(path), params={}, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def show_channels(self, name, channel=None):
        return self._crud_channel(name, channel)

    def create_channel(self, name, channel):
        return self._crud_channel(name, channel, 'post')

    def delete_channel(self, name, channel):
        return self._crud_channel(name, channel, 'delete')

    def create_channel_release(self, name, channel, release):
        path = "%s/%s" % (channel, release)
        return self._crud_channel(name, path, 'post')

    def delete_channel_release(self, name, channel, release):
        path = "%s/%s" % (channel, release)
        return self._crud_channel(name, path, 'delete')
