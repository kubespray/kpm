import logging
import os.path
from collections import OrderedDict
import hashlib
import yaml
import json
import jsonpatch
from kpm.platforms.kubernetes import Kubernetes, get_endpoint
from kpm.utils import colorize, mkdir_p
from kpm.display import print_deploy_result
from kpm.formats.kub_base import KubBase


logger = logging.getLogger(__name__)


_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


class Kub(KubBase):
    media_type = 'kpm'
    platform = "kubernetes"

    def _resource_build(self, kub, resource):
        self._annotate_resource(kub, resource)
        return {"file": resource['file'],
                "hash": resource['value']['metadata']['annotations'].get('kpm.hash', None),
                "protected": resource['protected'],
                "name": resource['name'],
                "kind": resource['value']['kind'].lower(),
                "endpoint": get_endpoint(
                    resource['value']['kind'].lower()).
                format(namespace=self.namespace),
                "body": json.dumps(resource['value'])}

    # @TODO do it in jsonnet
    def _annotate_resource(self, kub, resource):
        sha = None
        if 'annotations' not in resource['value']['metadata']:
            resource['value']['metadata']['annotations'] = {}
        if resource.get('hash', True):
            sha = hashlib.sha256(json.dumps(resource['value'])).hexdigest()
            resource['value']['metadata']['annotations']['kpm.hash'] = sha
        annotation = resource['value']['metadata']['annotations']
        annotation['kpm.version'] = kub.version
        annotation['kpm.package'] = kub.name
        annotation['kpm.parent'] = self.name
        annotation['kpm.protected'] = str(resource['protected']).lower()
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
                resource['patch'].append({"op": op,
                                          "path": "/metadata/namespace",
                                          "value": self.namespace})

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

    def build(self):
        result = []
        for kub in self.dependencies:
            result.append(self._dep_build(kub))
        return {"deploy": result,
                "package": {"name": self.name,
                            "version": self.version}}

    def _dep_build(self, kub):
        package = {"package": kub.name,
                   "version": kub.version,
                   "namespace": kub.namespace,
                   "resources": []}
        for resource in kub.resources():
                package['resources'].\
                    append(self._resource_build(kub, resource))
        return package

    def _process_deploy(self,
                        dry=False,
                        force=False,
                        fmt="txt",
                        proxy=None,
                        action="create",
                        dest="/tmp/kpm"):
        def output_progress(kubsource, status, fmt="text"):
            if fmt == 'text':
                print " --> %s (%s): %s" % (kubsource.name, kubsource.kind, colorize(status))

        dest = os.path.join(dest, self.name, self.version)
        mkdir_p(dest)
        table = []
        results = []
        if fmt == "text":
            print "%s %s " % (action, self.name)
        i = 0
        for kub in self.dependencies:
            package = self._dep_build(kub)
            i += 1
            pname = package["package"]
            version = package["version"]
            namespace = package["namespace"]
            if fmt == "text":
                print "\n %02d - %s:" % (i, package["package"])
            for resource in package["resources"]:
                body = resource["body"]
                endpoint = resource["endpoint"]
                # Use API instead of kubectl
                with open(os.path.join(dest, "%s-%s" % (resource['name'],
                                                        resource['file'].replace("/", "_"))), 'wb') as f:
                    f.write(body)
                kubresource = Kubernetes(namespace=namespace,
                                         body=body,
                                         endpoint=endpoint,
                                         proxy=proxy)
                status = getattr(kubresource, action)(force=force, dry=dry)
                if fmt == "text":
                    output_progress(kubresource, status)
                result_line = OrderedDict([("package", pname),
                                           ("version", version),
                                           ("kind", kubresource.kind),
                                           ("dry", dry),
                                           ("name", kubresource.name),
                                           ("namespace", kubresource.namespace),
                                           ("status", status)])

                if status != 'ok' and action == 'create':
                    kubresource.wait(3)
                results.append(result_line)
                if fmt == "text":
                    header = ["package", "version", "kind", "name",  "namespace", "status"]
                    display_line = []
                    for k in header:
                        display_line.append(result_line[k])
                    table.append(display_line)
        if fmt == "text":
            print_deploy_result(table)
        return results

    def deploy(self, *args, **kwargs):
        kwargs['action'] = 'create'
        return self._process_deploy(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs['action'] = 'delete'
        return self._process_deploy(*args, **kwargs)
