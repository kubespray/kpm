import json
import kpm
import kpm.registry
from kpm.commands.command_base import CommandBase


class VersionCmd(CommandBase):
    name = 'version'
    help_message = "show versions"

    def __init__(self, options):
        self.output = options.output
        self.api_version = None
        self.client_version = None
        self.registry_host = options.registry_host
        super(VersionCmd, self).__init__(options)

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)

    def _call(self):
        r = kpm.version(self.registry_host)
        self.api_version = r['api-version']
        self.client_version = r['client-version']

    def _render_json(self):
        print json.dumps({"api-version": self.api_version,
                          "client-version": self.client_version})

    def _render_console(self):
        print "Api-version: %s" % self.api_version
        print "Client-version: %s" % self.client_version
