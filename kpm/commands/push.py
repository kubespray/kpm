from appr.commands.push import PushCmd as ApprPushCmd

from kpm.manifest_jsonnet import ManifestJsonnet


class PushCmd(ApprPushCmd):
    default_media_type = 'kpm'

    def _kpm(self):
        self.filter_files = True
        self.manifest = ManifestJsonnet()
        ns, name = self.manifest.package['name'].split("/")
        if not self.namespace:
            self.namespace = ns
        if not self.pname:
            self.pname = name
        self.package_name = "%s/%s" % (self.namespace, self.pname)
        if not self.version or self.version == "default":
            self.version = self.manifest.package['version']
        self.metadata = self.manifest.metadata()
