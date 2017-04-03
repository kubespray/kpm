import logging
import os.path
import yaml
from kpm.manifest import ManifestBase

__all__ = ['ManifestChart']
logger = logging.getLogger(__name__)

MANIFEST_FILES = ["Chart.yaml", "Chart.yml"]


class ManifestChart(ManifestBase):

    def __init__(self, package=None, values=None):
        self.values = values
        if package is None:
            self._load_from_path()
        else:
            self._load_yaml(package.manifest)

    def _load_yaml(self, yamlstr):
        try:
            self.update(yaml.load(yamlstr))
        except yaml.YAMLError, exc:
            print "Error in configuration file:"
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                print "Error position: (%s:%s)" % (mark.line + 1, mark.column + 1)
            raise exc

    def _load_from_path(self):
        for f in MANIFEST_FILES:
            if os.path.exists(f):
                mfile = f
                break
        with open(mfile) as f:
            self._load_yaml(f.read())

    @property
    def keywords(self):
        return self.get("keywords", [])

    @property
    def engine(self):
        return self.get("engine", "gotpl")

    @property
    def home(self):
        return self.get("home", "")

    @property
    def description(self):
        return self.get("description", "")

    @property
    def version(self):
        return self.get("version", "")

    @property
    def maintainers(self):
        return self.get("maintainers", [])

    @property
    def sources(self):
        return self.get("sources", [])

    @property
    def name(self):
        return self.get("name", [])

    def metadata(self):
        return {"maintainers": self.maintainers, "source": self.sources}
