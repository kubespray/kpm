import json
import kpm.registry
from kpm.commands.command_base import CommandBase


class DeletePackageCmd(CommandBase):
    name = 'delete-package'
    help_message = 'delete package from the registry'

    def __init__(self, options):
        self.output = options.output
        self.package = options.package[0]
        self.registry_host = options.registry_host
        self.version = options.version
        self.media_type = options.media_type
        self.result = None
        super(DeletePackageCmd, self).__init__(options)

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser)
        cls._add_packagename_option(parser)
        cls._add_packageversion_option(parser)

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        self.result = r.delete_package(self.package, version=self.version, media_type=self.media_type)

    def _render_json(self):
        print json.dumps(self.result)

    def _render_console(self):
        print "Deleted package: %s - %s" % (self.result['package'], self.result['release'])
