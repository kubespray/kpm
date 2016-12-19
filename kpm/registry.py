import re
import json
import logging
import requests

from cnrclient.client import CnrClient

from kpm.auth import KpmAuth
import kpm


__all__ = ['Registry']


logger = logging.getLogger(__name__)
DEFAULT_REGISTRY = 'http://localhost:5000'
API_PREFIX = '/api/v1'
DEFAULT_PREFIX = ""


class Registry(CnrClient):
    def __init__(self, endpoint=DEFAULT_REGISTRY, api_prefix=DEFAULT_PREFIX, insecure=False):
        if not re.match("https?://", endpoint):
            if insecure or str.startswith(endpoint, "localhost"):
                scheme = "http://"
            else:
                scheme = "https://"
            endpoint = scheme + endpoint
        super(Registry, self).__init__(endpoint, api_prefix)
        self._headers = {'Content-Type': 'application/json',
                         'User-Agent': "kpmpy-cli: %s" % kpm.__version__}
        self.auth = KpmAuth(".kpm")
        self.host = self.endpoint.geturl()

    def auth_token(self):
        """ Override auth_token """
        return self.auth.token(self.host)

    def generate(self, name, namespace=None,
                 variables={}, version=None,
                 shards=None):
        path = "/api/v1/packages/%s/generate" % name
        params = {}
        body = {}

        body['variables'] = variables
        if namespace:
            params['namespace'] = namespace
        if shards:
            body['shards'] = shards
        if version:
            params['version'] = version
        r = requests.get(self._url(path),
                         data=json.dumps(body),
                         params=params,
                         headers=self.headers)
        r.raise_for_status()
        return r.json()

    def login(self, username, password):
        path = "/api/v1/users/login"
        resp = requests.post(self._url(path),
                             data=json.dumps({"user": {"username": username, "password": password}}),
                             headers=self.headers)
        resp.raise_for_status()
        result = resp.json()
        self.auth.add_token(self.host, result['token'])
        return result

    def signup(self, username, password, password_confirmation, email):
        path = "/api/v1/users"
        resp = requests.post(self._url(path),
                             data=json.dumps({"user": {"username": username,
                                                       "password": password,
                                                       "password_confirmation": password_confirmation,
                                                       "email": email}}),
                             headers=self.headers)
        resp.raise_for_status()
        result = resp.json()
        self.auth.add_token(self.host, result['token'])
        return result
