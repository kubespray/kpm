import copy

from kpm.manifest_chart import ManifestChart
from kpm.formats.kub_base import KubBase
from kpm.platforms.helm import Helm


class Chart(KubBase):
    media_type = "helm"
    platform = "helm"

    @property
    def manifest(self):
        if self._manifest is None:
            self._manifest = ManifestChart(self.package)
        return self._manifest

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
    def kubClass(self):
        return Chart

    def build(self):
        return "chart-release.tar.gz"

    def deploy(self):
        return Helm(self).install()

    def remove(self):
        return Helm(self).remove()

    @property
    def variables(self):
        if self._variables is None:
            self._variables = copy.deepcopy(self.manifest.variables)
            self._variables.update(self._deploy_vars)
        return self._variables

    @property
    def dependencies(self):
        return []

    def resources(self):
        return []

    @property
    def shards(self):
        pass
