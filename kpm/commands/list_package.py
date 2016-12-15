import kpm.registry
import kpm.packager
import kpm.manifest
import kpm.manifest_jsonnet
from kpm.display import print_packages
from kpm.commands.command_base import CommandBase


class ListPackageCmd(CommandBase):
    name = 'list'
    help_message = "list packages"

    def __init__(self, options):
        super(ListPackageCmd, self).__init__(options)
        self.registry_host = options.registry_host
        self.user = options.user
        self.organization = options.organization
        self.query = options.search
        self.result = None

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)

        parser.add_argument("-u", "--user", nargs="?", default=None,
                            help="list packages owned by USER")
        parser.add_argument("-o", "--organization", nargs="?", default=None,
                            help="list ORGANIZATION packages")
        parser.add_argument("search", nargs="?", default=None,
                            help="search query")

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        self.result = r.list_packages(user=self.user, organization=self.organization,
                                      text_search=self.query)

    def _render_json(self):
        return self.result

    def _render_console(self):
        print_packages(self.result)
