import json
import kpm.registry
import kpm.command
from kpm.formats.kub import Kub
from kpm.commands.command_base import CommandBase


class GenerateCmd(CommandBase):
    name = 'generate'
    help_message = "Generate a package json"

    def __init__(self, options):
        self.output = options.output
        self.package = options.pull[0]
        self.version = options.version
        self.namespace = options.namespace
        self.variables = options.variables
        self.registry_host = options.registry_host
        self.kub = None
        super(GenerateCmd, self).__init__(options)

    @classmethod
    def _add_arguments(self, parser):
        parser.add_argument("--namespace", nargs="?",
                            help="kubernetes namespace", default='default')
        parser.add_argument("-x", "--variables",
                            help="variables", default={}, action=kpm.command.LoadVariables)
        parser.add_argument('-p', "--pull", nargs=1, help="Fetch package from the registry")
        parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                            help='registry API url')
        parser.add_argument("-v", "--version", nargs="?", default=None,
                            help="package version")

    def _call(self):
        name = self.package
        version = self.version
        namespace = self.namespace
        k = Kub(name, endpoint=self.registry_host,
                variables=self.variables,
                namespace=namespace, version=version)
        filename = "%s_%s.tar.gz" % (k.name.replace("/", "_"), k.version)
        with open(filename, 'wb') as f:
            f.write(k.build_tar("."))
        self.kub = k

    def _render_json(self):
        print json.dumps(self.kub.manifest, indent=2, separators=(',', ': '))

    def _render_console(self):
        self._render_json()
