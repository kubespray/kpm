import json
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
        self.output = options.output
        self.registry_host = options.registry_host
        self.user = options.user
        self.organization = options.organization
        self.result = None
        super(ListPackageCmd, self).__init__(options)

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)

        parser.add_argument("-u", "--user", nargs="?", default=None,
                            help="list packages owned by USER")
        parser.add_argument("-o", "--organization", nargs="?", default=None,
                            help="list ORGANIZATION packages")

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        self.result = r.list_packages(user=self.user, organization=self.organization)

    def _render_json(self):
        print json.dumps(self.result)

    def _render_console(self):
        print_packages(self.result)
