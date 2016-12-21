import os
import kpm.utils
import kpm.registry
import kpm.packager
import kpm.command
from kpm.commands.command_base import CommandBase


class PullCmd(CommandBase):
    name = 'pull'
    help_message = "download a package"

    def __init__(self, options):
        super(PullCmd, self).__init__(options)
        self.package = options.package
        self.registry_host = options.registry_host
        self.version = options.version
        self.dest = options.dest
        self.media_type = options.media_type
        self.tarball = options.tarball
        self.path = None

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser)
        cls._add_packagename_option(parser)
        cls._add_packageversion_option(parser)
        parser.add_argument("--dest", default="/tmp",
                            help="directory used to extract resources")
        parser.add_argument("--tarball", action="store_true", default=False,
                            help="download the tar.gz")

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        result = r.pull(self.package, version=self.version, media_type=self.media_type)
        p = kpm.packager.Package(result, b64_encoded=False)
        filename = kpm.utils.package_filename(self.package, self.version, self.media_type)
        self.path = os.path.join(self.dest, filename)
        if self.tarball:
            self.path = self.path + ".tar.gz"
            with open(self.path, 'wb') as f:
                f.write(result)
        else:
            p.extract(self.path)

    def _render_dict(self):
        return {"pull": self.package,
                "media_type": self.media_type,
                "version": self.version,
                "path": self.path}

    def _render_console(self):
        print "Pull package: %s... \nStored in %s" % (self.package, self.path)
