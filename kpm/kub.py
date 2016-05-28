import copy
import hashlib
import tarfile
import shutil
import logging
import os.path
import jinja2
import yaml
import io
import tempfile
import jsonpatch
import json
from collections import OrderedDict
import kpm.registry as registry
import kpm.packager as packager
import kpm.manifest as manifest
import kpm.jinja_filters as jinja_filters
from kpm.kubernetes import get_endpoint
from kpm.utils import mkdir_p, convert_utf8
from kpm.render_jsonnet import RenderJsonnet

# __all__ = ['Kub']

logger = logging.getLogger(__name__)


_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


def dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())


def dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))


# yaml.add_representer(OrderedDict, dict_representer)
# yaml.add_constructor(_mapping_tag, dict_constructor)

jinja_env = jinja2.Environment()
jinja_env.filters.update(jinja_filters.filters())


class Kub(object):
    def __init__(self, name, version=None, resources=[], variables={}, shards=[], namespace=None, endpoint=None):
        self.name = name
        self.endpoint = endpoint
        self._dependencies = None
        self._resources = None
        self._deploy_resources = resources
        self._deploy_shards = shards
        self.namespace = namespace
        self._registry = registry.Registry(endpoint=endpoint)
        result = self._registry.pull(self.name, version)
        self.package = packager.Package(result)

        self.manifest = manifest.Manifest(self.package)
        self.version = self.manifest.package['version']
        self.author = self.manifest.package['author']
        self.description = self.manifest.package['description']
        self.deploy = self.manifest.deploy
        self.variables = copy.deepcopy(self.manifest.variables)
        if self.namespace:
            variables["namespace"] = self.namespace
        self.variables.update(variables)

    def __unicode__(self):
        return ("(<{class_name}({name}=={version})>".format(class_name=self.__class__.__name__,
                                                            name=self.name, version=self.version))

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def _create_namespaces(self, resources):
        # @TODO create namespaces for all manifests
        if self.namespace:
            ns = self.create_namespace(self.namespace)
            resources[ns['file']] = ns
        return resources

    def create_namespace(self, namespace):
        value = {"apiVersion": "v1",
                 "kind": "Namespace",
                 "metadata": {"name": namespace}}

        resource = {"file": "%s-ns.yaml" % namespace,
                    "template": yaml.dump(value),
                    "name": namespace,
                    "generated": True,
                    "order": -1,
                    "hash": False,
                    "protected": True,
                    "patch": [],
                    "variables": {},
                    "type": "namespace"}
        return resource

    @property
    def dependencies(self):
        if self._dependencies is None:
            self._fetch_deps()
        return self._dependencies

    def _append_patch(self, resources={}):
        index = 0

        for resource in self.manifest.resources:
            index += 1
            resources[resource['file']] = resource
            resource["order"] = index
            if 'protected' not in resource:
                resource["protected"] = False
            if 'patch' not in resource:
                resource['patch'] = []

        for resource in self._deploy_resources:
            if 'patch' in resource and len(resource['patch']) > 0:
                resources[resource['file']]["patch"] += resource['patch']

        return resources

    @property
    def shards(self):
        shards = self.manifest.shards
        if len(self._deploy_shards):
            shards = self._deploy_shards
        return shards

    def _default_patch(self, resources):
        for _, resource in resources.iteritems():
            patch = [
                {"op": "replace",
                 "path": "/metadata/name",
                 "value": resource['name']},
            ]
            if 'patch' not in resource:
                resource['patch'] = []
            resource['patch'] += patch
        return resources

    def _resolve_jinja(self, resource):
        val = resource['template']
        template = jinja_env.from_string(val)
        variables = copy.deepcopy(self.variables)
        if 'variables' in resource:
            variables.update(resource['variables'])
        if len(self.shards):
            variables['kpmshards'] = self.shards
        t = template.render(variables)
        resource['value'] = yaml.load(t)
        return resource

    def _apply_patches(self, resource):
        if self.namespace:
            if 'namespace' in resource['value']['metadata']:
                op = 'replace'
            else:
                op = 'add'
            resource['patch'].append({"op": op, "path": "/metadata/namespace", "value": self.namespace})

        if len(resource['patch']):
            patch = jsonpatch.JsonPatch(resource['patch'])
            resource['value'] = patch.apply(resource['value'])
        return resource

    def _resolve_jsonnet(self, resource):
        renderer = RenderJsonnet()
        resource['value'] = renderer.render_jsonnet(resource['template'])

    def _resolve_templates(self, resources):
        for _, resource in resources.iteritems():
            _, ext = os.path.splitext(resource['file'])
            if ext == ".j2":
                self._resolve_jinja(resource)
                self._apply_patches(resource)
                self._resolve_jinja(resource)
            elif ext == ".jsonnet":
                self._resolve_jsonnet(resource)

    def resources(self):
        if self._resources is None:
            self._resources = OrderedDict()
            resources = self._resources
            resources = self._create_namespaces(resources)
            resources = self._append_patch(resources)
            resources = self._default_patch(resources)
            resources = self._resolve_templates(resources)
        return self._resources

    def prepare_resources(self, dest="/tmp", index=0):
        for _, resource in self.resources().iteritems():
            index += 1
            path = os.path.join(dest, "%02d_%s_%s" % (index,
                                                      self.version,
                                                      resource['file']))
            f = open(path, 'w')
            f.write(yaml.safe_dump(convert_utf8(resource['value'])))
            resource['filepath'] = f.name
            f.close()
        return index

    def make_tarfile(self, source_dir):
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        return output

    def build_tar(self, dest="/tmp"):
        tempdir = tempfile.mkdtemp()
        dest = os.path.join(tempdir, self.manifest.package_name())
        mkdir_p(dest)
        index = 0
        for kub in self.dependencies:
            index = kub.prepare_resources(dest, index)

        package_json = self.build()
        with open(os.path.join(dest, ".package.json"), mode="w") as f:
            f.write(json.dumps(package_json))

        tar = self.make_tarfile(dest)
        tar.flush()
        tar.seek(0)
        shutil.rmtree(tempdir)
        return tar.read()

    def build(self):
        result = []
        for kub in self.dependencies:
            kubresources = OrderedDict([("package",  kub.name),
                                        ("version", kub.version),
                                        ("namespace", kub.namespace),
                                        ("resources", [])])
            for _, resource in kub.resources().iteritems():
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

                kubresources['resources'].\
                    append(OrderedDict({"file": resource['file'],
                                        "hash": sha,
                                        "protected": resource['protected'],
                                        "name": resource['name'],
                                        "kind": resource['value']['kind'].lower(),
                                        "endpoint": get_endpoint(
                                            resource['value']['kind'].lower()).
                                        format(namespace=self.namespace),
                                        "body": json.dumps(resource['value'])}))

            result.append(kubresources)
        return {"deploy": result,
                "package": {"name": self.name,
                            "version": self.version}}

    def _fetch_deps(self):
        self._dependencies = []
        for dep in self.manifest.deploy:
            if dep['name'] != '$self':
                variables = dep.get('variables', {})
                variables['kpmparent'] = {'name': self.name,
                                          'shards': self.shards,
                                          'variables': self.variables}
                kub = Kub(dep['name'],
                          endpoint=self.endpoint,
                          version=dep.get('version', None),
                          variables=variables,
                          shards=dep.get('shards', []),
                          resources=dep.get('resources', []),
                          namespace=self.namespace)
                self._dependencies.append(kub)
            else:
                self._dependencies.append(self)
