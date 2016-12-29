from cnrclient.commands.push import PushCmd as CnrPushCmd

from kpm.manifest_jsonnet import ManifestJsonnet


class PushCmd(CnrPushCmd):
    def _kpm(self):
        self.manifest = ManifestJsonnet()
        if not self.package_name:
            self.package_name = self.manifest.package['name']
        if not self.version or self.version == "default":
            self.version = self.manifest.package['version']
