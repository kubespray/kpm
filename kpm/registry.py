import json
import logging
import requests

from appr.client import ApprClient
from appr.auth import ApprAuth

import kpm

__all__ = ['Registry']

logger = logging.getLogger(__name__)
DEFAULT_REGISTRY = 'http://localhost:5000'
API_PREFIX = '/api/v1'
DEFAULT_PREFIX = "/cnr"


class Registry(ApprClient):

    def __init__(self, endpoint=DEFAULT_REGISTRY):
        super(Registry, self).__init__(endpoint)
        self._headers = {
            'Content-Type': 'application/json',
            'User-Agent': "kpmpy-cli/%s" % kpm.__version__
        }
        self.host = self.endpoint.geturl()
        self.auth = ApprAuth(".appr")

    def generate(self, name, namespace=None, variables={}, version=None, shards=None):
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
        r = requests.get(
            self._url(path), data=json.dumps(body), params=params, headers=self.headers)
        r.raise_for_status()
        return r.json()
