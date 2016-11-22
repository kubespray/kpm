import io
import tempfile
import json
from urlparse import urlparse
import copy
import tarfile
import shutil
import logging
import os.path
import yaml

from cnrclient.discovery import ishosted, split_package_name

import kpm.registry as registry
import kpm.packager as packager
from kpm.utils import mkdir_p
from kpm.utils import convert_utf8
from kpm.manifest_jsonnet import ManifestJsonnet


logger = logging.getLogger(__name__)


class KubBase(object):
    media_type = "kpm-base"
    target = "platform"

    def __init__(self, name,
                 version='default',
                 variables=None,
                 shards=None,
                 namespace=None,
                 endpoint=None,
                 resources=None):

        if shards.__class__ in [str, unicode]:
            shards = json.loads(shards)

        if variables is None:
            variables = {}

        self.endpoint = endpoint
        self._registry = registry.Registry(endpoint=self.endpoint)
        self._dependencies = None
        self._resources = None
        self._deploy_name = name
        self._deploy_version = version
        self._deploy_shards = shards
        self._deploy_resources = resources
        self._package = None
        self._manifest = None
        self.namespace = namespace
        if self.namespace:
            variables["namespace"] = self.namespace

        self._deploy_vars = variables
        self._variables = None

        self.tla_codes = {"variables": self._deploy_vars}
        if shards is not None:
            self.tla_codes["shards"] = shards

    @property
    def package(self):
        if self._package is None:
            result = self._fetch_package()
            self._package = packager.Package(result, b64_encoded=False)
        return self._package

    @property
    def manifest(self):
        if self._manifest is None:
            self._manifest = ManifestJsonnet(self.package,
                                             {"params": json.dumps(self.tla_codes)})
        return self._manifest

    def __unicode__(self):
        return ("(<{class_name}({name}=={version})>".format(class_name=self.__class__.__name__,
                                                            name=self.name,
                                                            version=self.version))

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
    def variables(self):
        if self._variables is None:
            self._variables = copy.deepcopy(self.manifest.variables)
            self._variables.update(self._deploy_vars)
        return self._variables

    def _fetch_package(self):
        parse = urlparse(self._deploy_name)
        if parse.scheme in ["http", "https"]:
            # @TODO
            pass
        elif parse.scheme == "file":
            parts = parse.path.split("/")
            _, ext = os.path.splitext(parts[-1])
            if ext == ".gz":
                filepath = parse.path
            else:
                filepath = tempfile.NamedTemporaryFile().name
                packager.pack_kub(filepath)
            with open(filepath, "rb") as f:
                return f.read()
        else:
            return self._registry.pull(self._deploy_name, self._deploy_version, self.media_type)

    @property
    def kubClass(self):
        raise NotImplementedError

    def _fetch_deps(self):
        self._dependencies = []
        for dep in self.manifest.deploy:
            if dep['name'] != '$self':
                # if the parent app has discovery but not child,
                # use the same domain to the child
                if ishosted(self._deploy_name) and not ishosted(dep['name']):
                    dep['name'] = "%s/%s" % (split_package_name(self._deploy_name)[0], dep['name'])
                variables = dep.get('variables', {})
                variables['kpmparent'] = {'name': self.name,
                                          'shards': self.shards,
                                          'variables': self.variables}

                kub = self.kubClass(dep['name'],
                                    endpoint=self.endpoint,
                                    version=dep.get('version', 'default'),
                                    variables=variables,
                                    resources=dep.get('resources', None),
                                    shards=dep.get('shards', None),
                                    namespace=self.namespace)
                self._dependencies.append(kub)
            else:
                self._dependencies.append(self)
        if not self._dependencies:
            self._dependencies.append(self)

    @property
    def dependencies(self):
        if self._dependencies is None:
            self._fetch_deps()
        return self._dependencies

    def resources(self):
        if self._resources is None:
            self._resources = self.manifest.resources
        return self._resources

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

    def prepare_resources(self, dest="/tmp", index=0):
        for resource in self.resources():
            index += 1
            path = os.path.join(dest, "%02d_%s_%s" % (index,
                                                      self.version,
                                                      resource['file']))
            f = open(path, 'w')
            f.write(yaml.safe_dump(convert_utf8(resource['value'])))
            resource['filepath'] = f.name
            f.close()
        return index

    def build(self):
        raise NotImplementedError

    def convert_to(self):
        raise NotImplementedError

    def deploy(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def status(self):
        raise NotImplementedError
