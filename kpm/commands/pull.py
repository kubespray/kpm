import os
import json
import kpm.registry
import kpm.packager
import kpm.command
from kpm.manifest_jsonnet import ManifestJsonnet
from kpm.commands.command_base import CommandBase


class PullCmd(CommandBase):
    name = 'pull'
    help_message = "download a package and extract it"

    def __init__(self, options):
        self.output = options.output
        self.package = options.package[0]
        self.registry_host = options.registry_host
        self.version = options.version
        self.dest = options.dest
        self.media_type = options.media_type
        self.tarball = options.tarball
        self.path = None
        super(PullCmd, self).__init__(options)

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser)
        cls._add_packagename_option(parser)
        cls._add_packageversion_option(parser)
        parser.add_argument("--dest", default="/tmp/",
                            help="directory used to extract resources")
        parser.add_argument("--tarball", action="store_true", default=False,
                            help="download the tar.gz")

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        result = r.pull(self.package, version=self.version, media_type=self.media_type)
        p = kpm.packager.Package(result, b64_encoded=False)
        self.path = os.path.join(self.dest, ManifestJsonnet(p).package_name())
        if self.tarball:
            self.path = self.path + ".tar.gz"
            with open(self.path, 'wb') as f:
                f.write(result)
        else:
            p.extract(self.path)

    def _render_json(self):
        print json.dumps({"pull": self.package,
                          "media_type": self.media_type,
                          "version": self.version,
                          "extrated": self.path})

    def _render_console(self):
        print "Pull package: %s... \nExtract to %s" % (self.package, self.path)
