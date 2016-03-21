import logging
import os.path
import yaml


__all__ = ['Manifest']
logger = logging.getLogger(__name__)

MANIFEST_FILE = "manifest.yaml"


class Manifest(dict):
    def __init__(self, package=None, path="."):
        if package is not None:
            self.update(yaml.load(package.manifest))
            super(Manifest, self).__init__()

        elif path is not None:
            self.mfile = os.path.join(path, MANIFEST_FILE)
            self._load_yaml(self.mfile)

    def _load_yaml(self, mfile):
        try:
            y = yaml.load(open(mfile, 'r'))
            self.update(y)
        except yaml.YAMLError, exc:
            print "Error in configuration file:"
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                print "Error position: (%s:%s)" % (mark.line+1, mark.column+1)

    @property
    def resources(self):
        if 'resources' in self.keys():
            return self['resources']
        else:
            return []

    @property
    def deploy(self):
        if 'deploy' in self.keys():
            return self['deploy']
        else:
            return []

    @property
    def variables(self):
        if 'variables' in self.keys():
            return self['variables']
        else:
            return {}

    @property
    def package(self):
        if 'package' in self.keys():
            return self['package']
        else:
            return {}

    @property
    def shards(self):
        if 'shards' in self.keys():
            return self['shards']
        else:
            return []

    def kubname(self):
        sp = self.package['name'].split('/')
        if len(sp) > 1:
            name = "%s_%s" % (sp[0], sp[1])
        else:
            name = self.package['name']
        return name

    def package_name(self):
        package = ("%s_%s" % (self.kubname(), self.package['version']))
        return package
