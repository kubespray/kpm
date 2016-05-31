import logging
import os.path
import yaml
from kpm.render_jsonnet import RenderJsonnet, yaml_to_jsonnet
from kpm.packager import authorized_files

__all__ = ['Manifest']
logger = logging.getLogger(__name__)

MANIFEST_FILES = ["manifest.jsonnet", "manifest.yaml"]


class Manifest(dict):
    def __init__(self, package=None, tla_codes=None):
        self.tla_codes = tla_codes
        if package is not None:
            self._load_from_package(package)
        else:
            self._load_from_path()

        super(Manifest, self).__init__()

    def _load_from_package(self, package):
        if package.isjsonnet():
            self._load_jsonnet(package.manifest, package.files)
        else:
            self._load_yaml(package.manifest, package.files)

    def _load_from_path(self):
        for f in MANIFEST_FILES:
            if os.path.exists(f):
                mfile = f
                break
        _, ext = os.path.splitext(mfile)
        with open(mfile) as f:
            auth_files = authorized_files()
            files = dict(zip(auth_files, [None] * len(auth_files)))
            if ext == '.jsonnet':
                self._load_jsonnet(f.read(), files)
            else:
                self._load_yaml(f.read(), files)

    def _load_jsonnet(self, jsonnetstr, files):
        k = RenderJsonnet(files)
        r = k.render_jsonnet(jsonnetstr, self.tla_codes)
        self.update(r)

    def _load_yaml(self, yamlstr, files):
        try:
            jsonnetstr = yaml_to_jsonnet(yamlstr)
            files['manifest.jsonnet'] = jsonnetstr
            self._load_jsonnet(jsonnetstr, files)
        except yaml.YAMLError, exc:
            print "Error in configuration file:"
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                print "Error position: (%s:%s)" % (mark.line+1, mark.column+1)
            raise exc

    @property
    def resources(self):
        return self.get("resources", [])

    @property
    def deploy(self):
        return self.get("deploy", [])

    @property
    def variables(self):
        return self.get("variables", {})

    @property
    def package(self):
        return self.get("package", {})

    @property
    def shards(self):
        return self.get("shards", [])

    def kubname(self):
        sp = self.package['name'].split('/')
        name = "%s_%s" % (sp[0], sp[1])
        return name

    def package_name(self):
        package = ("%s_%s" % (self.kubname(), self.package['version']))
        return package
