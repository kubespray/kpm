import json
import kpm.deploy
import kpm.command
from kpm.kub_jsonnet import KubJsonnet
from kpm.commands.command_base import CommandBase


class DeployCmd(CommandBase):
    name = 'deploy'
    help_message = "deploy a package on kubernetes"

    def __init__(self, options):
        self.output = options.output
        self.package = options.package[0]
        self.registry_host = options.registry_host
        self.shards = options.shards
        self.force = options.force
        self.dry_run = options.dry_run
        self.namespace = options.namespace
        self.api_proxy = options.api_proxy
        self.version = options.version
        self.tmpdir = options.tmpdir
        self.variables = options.variables
        self.status = None
        super(DeployCmd, self).__init__(options)

    @classmethod
    def _add_arguments(self, parser):
        parser.add_argument('package', nargs=1, help="package-name")
        parser.add_argument("--tmpdir", nargs="?", default="/tmp/",
                            help="directory used to extract resources")
        parser.add_argument("--dry-run", action='store_true', default=False,
                            help="do not create the resources on kubernetes")
        parser.add_argument("--namespace", nargs="?",
                            help="kubernetes namespace", default=None)
        parser.add_argument("--api-proxy", nargs="?",
                            help="kubectl proxy url", const="http://localhost:8001")
        parser.add_argument("-v", "--version", nargs="?",
                            help="package VERSION", default=None)
        parser.add_argument("-x", "--variables",
                            help="variables", default={}, action=kpm.command.LoadVariables)
        parser.add_argument("--shards",
                            help="Shards list/dict/count: eg. --shards=5 ; --shards='[{\"name\": 1, \"name\": 2}]'",
                            default=None)
        parser.add_argument("--force", action='store_true', default=False,
                            help="force upgrade, delete and recreate resources")
        parser.add_argument("-H", "--registry-host", nargs="?", default=None,
                            help='Generate resources server-side')

    def _packages(self):
        packages = None
        if self.registry_host is None:
            k = KubJsonnet(self.package,
                           endpoint=self.registry_host,
                           variables=self.variables,
                           namespace=self.namespace,
                           shards=self.shards,
                           version=self.version)
            packages = k.build()
        return packages

    def _call(self):
        packages = self._packages()
        self.status = kpm.deploy.deploy(self.package,
                                        version=self.version,
                                        dest=self.tmpdir,
                                        namespace=self.namespace,
                                        force=self.force,
                                        dry=self.dry_run,
                                        endpoint=self.registry_host,
                                        proxy=self.api_proxy,
                                        variables=self.variables,
                                        shards=self.shards,
                                        fmt=self.output,
                                        packages=packages)

    def _render_json(self):
        print json.dumps(self.status)

    def _render_console(self):
        """ Handled by deploy """
        pass
