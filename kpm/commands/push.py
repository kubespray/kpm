from cnrclient.commands.push import PushCmd as CnrPushCmd

from kpm.manifest_jsonnet import ManifestJsonnet


class PushCmd(CnrPushCmd):
    default_media_type = 'kpm'

    def _kpm(self):
        self.filter_files = True
        self.manifest = ManifestJsonnet()
        if not self.package_name:
            self.package_name = self.manifest.package['name']
        if not self.version or self.version == "default":
            self.version = self.manifest.package['version']
