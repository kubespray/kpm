import kpm.registry
import kpm.packager
import kpm.manifest
import kpm.manifest_jsonnet
from kpm.commands.command_base import CommandBase


class ShowCmd(CommandBase):
    name = 'show'
    help_message = "print the package manifest"

    def __init__(self, options):
        super(ShowCmd, self).__init__(options)
        self.package = options.package
        self.registry_host = options.registry_host
        self.version = options.version
        self.file = options.file
        self.tree = options.tree
        self.media_type = options.media_type
        self.result = None
        self.format = options.media_type

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser)
        cls._add_packagename_option(parser)
        cls._add_packageversion_option(parser)
        parser.add_argument('--tree', help="List files inside the package", action='store_true', default=False)
        parser.add_argument('-f', '--file', help="Display a file", default=None)

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        result = r.pull(self.package, version=self.version, media_type=self.media_type)
        p = kpm.packager.Package(result, b64_encoded=False)
        if self.tree:
            self.result = "\n".join(p.tree())
        elif self.file:
            self.result = p.file(self.file)
        else:
            self.result = p.manifest

    def _render_dict(self):
        return {"show": self.package,
                "output": self.result}

    def _render_console(self):
        print self.result
