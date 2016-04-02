import logging
import os.path
import yaml


__all__ = ['Manifest']
logger = logging.getLogger(__name__)

MANIFEST_FILE = "manifest.yaml"


class Manifest(dict):
    def __init__(self, package=None, path="."):
        if package is not None:
            self.update(yaml.safe_load(package.manifest))
            super(Manifest, self).__init__()

        elif path is not None:
            self.mfile = os.path.join(path, MANIFEST_FILE)
            self._load_yaml(self.mfile)

    def _load_yaml(self, mfile):
        try:
            y = yaml.safe_load(open(mfile, 'r'))
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
