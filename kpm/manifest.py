import logging
import os.path
import yaml
from kpm.render_jsonnet import RenderJsonnet
from kpm.packager import authorized_files

__all__ = ['Manifest']
logger = logging.getLogger(__name__)

MANIFEST_FILES = ["manifest.jsonnet", "manifest.yaml"]


class Manifest(dict):
    def __init__(self, package=None):
        self.mfile = None
        if package is not None:
            self._load_from_package(package)
        else:
            self._load_from_path()
        super(Manifest, self).__init__()

    def _load_from_package(self, package):
        if package.isjsonnet:
            self._load_jsonnet(package.manifest, package.files)
        else:
            self._load_yaml(package.manifest)

    def _load_from_path(self):
        for f in MANIFEST_FILES:
            if os.path.exists(f):
                self.mfile = f
                break
        _, ext = os.path.splitext(self.mfile)
        with open(self.mfile) as f:
            if ext == '.jsonnet':
                files = authorized_files()
                self._load_jsonnet(f.read(), zip(files, [None] * len(files)))
            else:
                self._load_yaml(f.read())

    def _load_jsonnet(self, jsonnetstr, files):
        k = RenderJsonnet(files)
        self.update(k.render_jsonnet(jsonnetstr))

    def _load_yaml(self, yamlstr):
        try:
            y = yaml.safe_load(yamlstr)
            self.update(y)
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
