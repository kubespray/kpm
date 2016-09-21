import hashlib
import logging
import yaml
import json
from collections import OrderedDict
import jsonpatch
from kpm.kubernetes import get_endpoint
from kpm.kub_jsonnet import KubJsonnet


logger = logging.getLogger(__name__)


_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


class Kub(KubJsonnet):
    def _resource_build(self, kub, resource):
        self._annotate_resource(kub, resource)
        return OrderedDict({"file": resource['file'],
                            "hash": resource['value']['metadata']['annotations'].get('kpm.hash', None),
                            "protected": resource['protected'],
                            "name": resource['name'],
                            "kind": resource['value']['kind'].lower(),
                            "endpoint": get_endpoint(
                                resource['value']['kind'].lower()).
                            format(namespace=self.namespace),
                            "body": json.dumps(resource['value'])})

    # @TODO do it in jsonnet
    def _annotate_resource(self, kub, resource):
        sha = None
        if 'annotations' not in resource['value']['metadata']:
            resource['value']['metadata']['annotations'] = {}
        if resource.get('hash', True):
            sha = hashlib.sha256(json.dumps(resource['value'])).hexdigest()
            resource['value']['metadata']['annotations']['kpm.hash'] = sha
        resource['value']['metadata']['annotations']['kpm.version'] = kub.version
        resource['value']['metadata']['annotations']['kpm.package'] = kub.name
        resource['value']['metadata']['annotations']['kpm.parent'] = self.name
        resource['value']['metadata']['annotations']['kpm.protected'] = str(resource['protected']).lower()
        return resource

    def _create_namespaces(self):
        if self.namespace:
            ns = self.create_namespace(self.namespace)
            self._resources.insert(0, ns)

    def resources(self):
        """ Override resources to auto-create namespace"""
        if self._resources is None:
            self._resources = self.manifest.resources
            self._create_namespaces()
        return self._resources

    def _apply_patches(self, resources):
        for _, resource in resources.iteritems():
            if self.namespace:
                if 'namespace' in resource['value']['metadata']:
                    op = 'replace'
                else:
                    op = 'add'
                resource['patch'].append({"op": op, "path": "/metadata/namespace", "value": self.namespace})

            if len(resource['patch']):
                patch = jsonpatch.JsonPatch(resource['patch'])
                result = patch.apply(resource['value'])
                resource['value'] = result
        return resources

    @property
    def kubClass(self):
        return Kub

    def create_namespace(self, namespace):
        value = {"apiVersion": "v1",
                 "kind": "Namespace",
                 "metadata": {"name": namespace}}

        resource = {"file": "%s-ns.yaml" % namespace,
                    "name": namespace,
                    "generated": True,
                    "order": -1,
                    "hash": False,
                    "protected": True,
                    "value": value,
                    "patch": [],
                    "variables": {},
                    "type": "namespace"}
        return resource
