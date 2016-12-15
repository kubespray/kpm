import argparse
import os
import base64
import kpm.utils
import kpm.registry
from kpm.manifest_jsonnet import ManifestJsonnet
from kpm.packager import pack_kub
from kpm.commands.command_base import CommandBase


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
        self.package_name = options.name
        self.filter_files = True
        self.metadata = None
        self.prefix = None

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser)
        cls._add_packageversion_option(parser)
        parser.add_argument('-n', "--name", default=None, action=kpm.command.PackageName, help="package-name")
        parser.add_argument("-f", "--force", action='store_true', default=False,
                            help="force push")

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        if self.media_type in ["kpm", "kpm-compose"]:
            self.manifest = ManifestJsonnet()
            if not self.package_name:
                self.package_name = self.manifest.package['name']
            if not self.version or self.version == "default":
                self.version = self.manifest.package['version']
            self.metadata = self.manifest.metadata()
        else:
            self.filter_files = False
            _, self.prefix = self.package_name.split("/")
        if self.version is None or self.version == "default":
            raise argparse.ArgumentTypeError("Missing option: --version")
        if self.package_name is None:
            raise argparse.ArgumentTypeError("Missing option: --name")

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
