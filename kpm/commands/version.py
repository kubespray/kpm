import kpm
import kpm.registry
from kpm.commands.command_base import CommandBase


class VersionCmd(CommandBase):
    name = 'version'
    help_message = "show versions"

    def __init__(self, options):
        super(VersionCmd, self).__init__(options)
        self.api_version = None
        self.client_version = None
        self.registry_host = options.registry_host

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)

    def _call(self):
        r = kpm.version(self.registry_host)
        self.api_version = r['api-version']
        self.client_version = r['client-version']

    def _render_dict(self):
        return {"api-version": self.api_version,
                "client-version": self.client_version}

    def _render_console(self):
        print "Api-version: %s" % self.api_version
        print "Client-version: %s" % self.client_version
