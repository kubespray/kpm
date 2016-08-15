from urlparse import urlparse
import copy
import hashlib
import tarfile
import shutil
import logging
import os.path
import yaml
import io
import tempfile
import json
import kpm.registry as registry
import kpm.packager as packager
from kpm.utils import mkdir_p, recursive_update

# __all__ = ['Kub']

logger = logging.getLogger(__name__)


_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


class KubBase(object):
    def __init__(self, name,
                 version=None,
                 variables=None,
                 shards=None,
                 namespace=None,
                 endpoint=None,
                 resources=None):
        if variables is None:
            variables = {}
        self.endpoint = endpoint

        self._dependencies = None
        self._resources = None
        self._deploy_name = name
        self._deploy_version = version
        self._deploy_shards = shards
        self._deploy_resources = resources
        self.namespace = namespace
        result = self._fetch_package()
        self.package = packager.Package(result)
        if self.namespace:
            variables["namespace"] = self.namespace
        self.manifest = None
        self._deploy_vars = variables
        self._variables = None

    def __unicode__(self):
        return ("(<{class_name}({name}=={version})>".format(class_name=self.__class__.__name__,
                                                            name=self.name, version=self.version))

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return unicode(self).encode('utf-8')

    @property
    def author(self):
        return self.manifest.package['author']

    @property
    def version(self):
        return self.manifest.package['version']

    @property
    def description(self):
        return self.manifest.package['description']

    @property
    def name(self):
        return self.manifest.package['name']

    @property
    def deploy(self):
        return self.manifest.deploy

    @property
    def variables(self):
        if self._variables is None:
            self._variables = copy.deepcopy(self.manifest.variables)
            self._variables = recursive_update(self._variables, self._deploy_vars)
        return self._variables

    def _fetch_package(self):
        parse = urlparse(self._deploy_name)
        if parse.scheme in ["http", "https"]:
            pass
        elif parse.scheme == "file":
            parts = parse.path.split("/")
            _, ext = os.path.splitext(parts[-1])
            if ext == "tar.gz":
                filepath = parse.path
            else:
                filepath = tempfile.NamedTemporaryFile().name
                packager.pack_kub(filepath)
            with open(filepath, "rb") as f:
                return f.read()

        elif parse.scheme == "":
            self._registry = registry.Registry(endpoint=self.endpoint)
            return self._registry.pull(self._deploy_name, self._deploy_version)
        else:
            raise ValueError("Unknown package (%s) scheme: %s" % (self._deploy_name, parse.scheme))

    @property
    def kubClass(self):
        raise NotImplementedError

    def _fetch_deps(self):
        self._dependencies = []
        for dep in self.manifest.deploy:
            if dep['name'] != '$self':
                variables = dep.get('variables', {})
                variables['kpmparent'] = {'name': self.name,
                                          'shards': self.shards,
                                          'variables': self.variables}

                kub = self.kubClass(dep['name'],
                                    endpoint=self.endpoint,
                                    version=dep.get('version', None),
                                    variables=variables,
                                    resources=dep.get('resources', None),
                                    shards=dep.get('shards', None),
                                    namespace=self.namespace)
                self._dependencies.append(kub)
            else:
                self._dependencies.append(self)

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

    @property
    def dependencies(self):
        if self._dependencies is None:
            self._fetch_deps()
        return self._dependencies

    @property
    def shards(self):
        shards = self.manifest.shards
        if self._deploy_shards is not None and len(self._deploy_shards):
            shards = self._deploy_shards
        return shards

    def make_tarfile(self, source_dir):
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        return output

    def build_tar(self, dest="/tmp"):
        package_json = self.build()

        tempdir = tempfile.mkdtemp()
        dest = os.path.join(tempdir, self.manifest.package_name())
        mkdir_p(dest)
        index = 0
        for kub in self.dependencies:
            index = kub.prepare_resources(dest, index)

        with open(os.path.join(dest, ".package.json"), mode="w") as f:
            f.write(json.dumps(package_json))

        tar = self.make_tarfile(dest)
        tar.flush()
        tar.seek(0)
        shutil.rmtree(tempdir)
        return tar.read()

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
