from cnrclient.commands.push import PushCmd as CnrPushCmd

from kpm.manifest_jsonnet import ManifestJsonnet


class PushCmd(CnrPushCmd):
    default_media_type = 'kpm'

    def _kpm(self):
        self.filter_files = True
        self.manifest = ManifestJsonnet()
        ns, name = self.manifest.package['name'].split("/")
        if not self.namespace:
            self.namespace = ns
        if not self.name:
            self.name = name
        self.package_name = "%s/%s" % (self.namespace, self.name)

        if not self.version or self.version == "default":
            self.version = self.manifest.package['version']
