import tempfile
import time
import logging
import json
import subprocess
import requests
from urlparse import urlparse

__all__ = ['Kubernetes', "get_endpoint"]


logger = logging.getLogger(__name__)


resource_endpoints = {
    "daemonsets": "apis/extensions/v1beta1/namespaces/{namespace}/daemonsets",
    "deployments": "apis/extensions/v1beta1/namespaces/{namespace}/deployments",
    "horizontalpodautoscalers": "apis/extensions/v1beta1/namespaces/{namespace}/horizontalpodautoscalers",
    "ingresses": "apis/extensions/v1beta1/namespaces/{namespace}/ingresses",
    "jobs": "apis/extensions/v1beta1/namespaces/{namespace}/jobs",
    "namespaces": "api/v1/namespaces",
    "replicasets": "apis/extensions/v1beta1/namespaces/{namespace}/replicasets",
    "persistentvolumes": "api/v1/namespaces/{namespace}/persistentvolumes",
    "persistentvolumeclaims": "api/v1/namespaces/{namespace}/persistentvolumeclaims",
    "services": "api/v1/namespaces/{namespace}/services",
    "serviceaccounts": "api/v1/namespaces/{namespace}/serviceaccounts",
    "secrets": "api/v1/namespaces/{namespace}/secrets",
    "configmaps": "api/v1/namespaces/{namespace}/configmaps",
    "replicationcontrollers": "api/v1/namespaces/{namespace}/replicationcontrollers",
    "pods": "api/v1/namespaces/{namespace}/pods",
}


resources_alias = {"ds": "daemonsets",
                   "hpa": "horizontalpodautoscalers",
                   "ing": "ingresses",
                   "ingress": "ingresses",
                   "ns": "namespaces",
                   "po": "pods",
                   "pv": "persistentvolumes",
                   "pvc": "persistentvolumeclaims",
                   "rc": "replicationcontrollers",
                   "svc": "services"}


def get_endpoint(kind):
    name = None
    if kind in resource_endpoints:
        name = kind
    elif kind in resources_alias:
        name = resources_alias[kind]
    elif kind + "s" in resource_endpoints:
        name = kind + "s"
    else:
        raise KeyError("Resource name %s not in [%s]" % (kind, resource_endpoints.keys()))
    return resource_endpoints[name]


class Kubernetes(object):
    def __init__(self,
                 namespace=None,
                 endpoint=None,
                 body=None,
                 proxy=None):

        self.proxy = None
        if endpoint is not None and endpoint[0] == "/":
            endpoint = endpoint[1:-1]
        self.endpoint = endpoint
        self.body = body
        self.obj = None
        self.protected = False
        self._resource_load()

        self.kind = self.obj['kind'].lower()
        self.name = self.obj['metadata']['name']
        self.kpmhash = self._get_kpmhash(self.obj)
        self.namespace = self._namespace(namespace)
        self.result = None
        if proxy:
            self.proxy = urlparse(proxy)

    def _resource_load(self):
        self.obj = json.loads(self.body)

        if 'annotations' in self.obj['metadata']:
            if ('kpm.protected' in self.obj['metadata']['annotations'] and
               self.obj['metadata']['annotations']['kpm.protected'] == 'true'):
                self.protected = True

    def _namespace(self, namespace=None):
        if namespace:
            return namespace
        elif 'namespace' in self.obj['metadata']:
            return self.obj['metadata']['namespace']
        else:
            return 'default'

    def create(self, force=False, dry=False):
        """
          - Check if resource name exists
          - if it exists check if the kpmhash is the same
          - if not the same delete the resource and recreate it
          - if force == true, delete the resource and recreate it
          - if doesnt exists create it
        """
        r = self.get()
        f = tempfile.NamedTemporaryFile()
        cmd = ['create', '-f', f.name]
        f.write(self.body)
        f.flush()
        if r is None:
            self._call(cmd, dry=dry)

            return 'created'
        elif (self.kpmhash is None or self._get_kpmhash(r) == self.kpmhash) and force is False:
            return 'ok'
        elif self._get_kpmhash(r) != self.kpmhash or force is True:
            if self.delete(dry=dry) == 'protected':
                return 'protected'
            self._call(cmd, dry=dry)
            return 'updated'

    def _get_kpmhash(self, r):
        if 'annotations' in r['metadata'] and 'kpm.hash' in r['metadata']['annotations']:
            return r['metadata']['annotations']['kpm.hash']
        else:
            return None

    def get(self):
        cmd = ['get', self.kind, self.name, '-o', 'json']
        try:
            self.result = json.loads(self._call(cmd))
            return self.result
        except subprocess.CalledProcessError:
            return None
        except (requests.exceptions.HTTPError) as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e

    def delete(self, dry=False, **kwargs):
        cmd = ['delete', self.kind, self.name]
        if self.protected:
            return 'protected'
        r = self.get()
        if r is not None:
            self._call(cmd, dry=dry)
            return 'deleted'
        else:
            return 'absent'

    def wait(self, retries=3, seconds=1):
        r = 1
        time.sleep(seconds)
        obj = self.get()
        while (r < retries and obj is None):
            r += 1
            time.sleep(seconds)
            obj = self.get()
        return obj

    def exists(self):
        r = self.get()
        if r is None:
            return False
        else:
            return True

    def _call(self, cmd, dry=False):
        command = ['kubectl'] + cmd + ["--namespace", self.namespace]
        if not dry:
            if self.proxy is not None:
                return self._request(cmd[0])
            else:
                return subprocess.check_output(command, stderr=subprocess.STDOUT)
        else:
            return True

    def _request(self, method):
        if method == 'create':
            headers = {'Content-Type': 'application/json'}
            method = 'post'
            url = "%s/%s" % (self.proxy.geturl(), self.endpoint)
            return requests.post(url, data=self.body, headers=headers)
        else:
            url = "%s/%s/%s" % (self.proxy.geturl(), self.endpoint, self.name)
            query = getattr(requests, method)
            r = query(url)
            r.raise_for_status()
            return r.content
