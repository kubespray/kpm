import json
import logging
from urlparse import urlparse, urljoin
import requests

from kpm.auth import KpmAuth

__all__ = ['Registry']

logger = logging.getLogger(__name__)
DEFAULT_REGISTRY = "https://api.kpm.sh"
API_PREFIX = '/api/v1'


class Registry(object):
    def __init__(self, endpoint=DEFAULT_REGISTRY):
        if endpoint is None:
            endpoint = DEFAULT_REGISTRY
        self.endpoint = urlparse(endpoint)
        self.auth = KpmAuth()
        self._headers = {'Content-Type': 'application/json'}

    def _url(self, path):
        return urljoin(self.endpoint.geturl(), API_PREFIX + path)

    @property
    def headers(self):
        token = self.auth.token
        headers = self._headers.copy()
        if token is not None:
            headers['Authorization'] = token
        return headers

    def pull(self, name, version=None):
        organization, name = name.split("/")
        path = "/organizations/%s/packages/%s/pull.json" % (organization, name)
        params = {}
        if version:
            params['version'] = version
        r = requests.get(self._url(path), params=params, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def list_packages(self, user=None, organization=None):
        path = "/packages"
        params = {}
        if user:
            params['username'] = user
        if organization:
            params["organizations"] = organization
        r = requests.get(self._url(path), params=params, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def generate(self, name, namespace=None, variables=None, version=None):
        organization, name = name.split("/")
        path = "/organizations/%s/packages/%s/generate.json" % (organization, name)
        params = {}
        if version:
            params['version'] = version
        if namespace:
            params['namespace'] = namespace
        if variables:
            params['variables'] = variables
        r = requests.get(self._url(path), params=params, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def generate_tar(self, name, namespace=None, variables=None, version=None):
        organization, name = name.split("/")
        path = "/organizations/%s/packages/%s/generate.json" % (organization, name)
        params = {'tarball': 'true'}
        if version:
            params['version'] = version
        if namespace:
            params['namespace'] = namespace
        if variables:
            params['variables'] = variables

        r = requests.get(self._url(path), params=params, headers=self.headers)
        r.raise_for_status()
        return r.content

    def push(self, name, body, force=False):
        organization, name = name.split("/")
        body['name'] = name
        path = "/organizations/%s/packages.json" % organization
        r = requests.post(self._url(path),
                          params={"force": str(force).lower()},
                          data=json.dumps(body), headers=self.headers)
        r.raise_for_status()
        return r.json()

    def login(self, username, password):
        path = "/users/sign_in"
        self.auth.delete_token()
        r = requests.post(self._url(path),
                          params={"user[username]": username,
                                  "user[password]": password},
                          headers=self.headers)
        r.raise_for_status()
        result = r.json()
        self.auth.token = result['token']
        return result

    def signup(self, username, password, password_confirmation, email):
        path = "/users"
        self.auth.delete_token()
        r = requests.post(self._url(path),
                          params={"user[username]": username,
                                  "user[password]": password,
                                  "user[password_confirmation]": password_confirmation,
                                  "user[email]": email,
                                  },
                          headers=self._headers)
        r.raise_for_status()
        result = r.json()
        self.auth.token = result['token']
        return result

    def delete_package(self, name, version=None):
        organization, name = name.split("/")
        path = "/organizations/%s/packages/%s" % (organization, name)
        params = {}
        if version:
            params['version'] = version
        r = requests.delete(self._url(path), params=params, headers=self.headers)
        r.raise_for_status()
        return True
