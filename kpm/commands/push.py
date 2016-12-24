import argparse
import os
import base64
import kpm.utils
import kpm.registry
from kpm.manifest_jsonnet import ManifestJsonnet
from kpm.manifest_chart import ManifestChart
from kpm.packager import pack_kub
from kpm.commands.command_base import CommandBase
from kpm.utils import check_package_name


class PushCmd(CommandBase):
    name = 'push'
    help_message = "push a package to the registry"

    def __init__(self, options):
        super(PushCmd, self).__init__(options)
        self.registry_host = options.registry_host
        self.force = options.force
        self.manifest = None
        self.media_type = options.media_type
        self.version = options.version
        self.namespace = options.namespace
        self.package_name = None
        self.filter_files = True
        self.metadata = None
        self.prefix = None

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser)
        cls._add_packageversion_option(parser)
        parser.add_argument('-n', "--namespace", default=None, action="store", help="package-name")
        parser.add_argument("-f", "--force", action='store_true', default=False,
                            help="force push")

    def _manifest_type(self):
        pass

    def _chart(self):
        self.manifest = ManifestChart()
        self.filter_files = False
        self.package_name = "%s/%s" % (self.namespace, self.manifest.name)
        self.version = self.manifest.version

    def _kub(self):
        self.manifest = ManifestJsonnet()
        if not self.package_name:
            self.package_name = self.manifest.package['name']
        if not self.version or self.version == "default":
            self.version = self.manifest.package['version']

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        if self.media_type in ["kpm", "kpm-compose"]:
            self._kub()
        elif self.media_type in ['helm']:
            self._chart()

        self.metadata = self.manifest.metadata()
        if self.version is None or self.version == "default":
            raise argparse.ArgumentTypeError("Missing option: --version")
        if self.package_name is None or not check_package_name(self.package_name):
            raise argparse.ArgumentTypeError("Missing option: --namespace")

        filename = kpm.utils.package_filename(self.package_name, self.version, self.media_type)
        # @TODO: Pack in memory
        kubepath = os.path.join(".", filename + ".tar.gz")
        pack_kub(kubepath, filter_files=self.filter_files, prefix=self.prefix)
        f = open(kubepath, 'rb')
        body = {"name": self.package_name,
                "release": self.version,
                "metadata": self.metadata,
                "media_type": self.media_type,
                "blob": base64.b64encode(f.read())}
        r.push(self.package_name, body, self.force)
        f.close()
        os.remove(kubepath)

    def _render_dict(self):
        return {"package": self.package_name,
                "version": self.version,
                "media_type": self.media_type}

    def _render_console(self):
        print "package: %s (%s) pushed" % (self.package_name, self.version)
