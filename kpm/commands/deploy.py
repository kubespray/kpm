import kpm.platforms.kubernetes
import kpm.command
import kpm.formats
from kpm.commands.command_base import CommandBase


class DeployCmd(CommandBase):
    name = 'deploy'
    help_message = "deploy a package on kubernetes"

    def __init__(self, options):
        super(DeployCmd, self).__init__(options)
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
        self.target = options.platform
        self.format = options.media_type
        self.status = None
        self._kub = None

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser)
        cls._add_packagename_option(parser)
        cls._add_packageversion_option(parser)

        parser.add_argument("--tmpdir", default="/tmp/",
                            help="directory used to extract resources")
        parser.add_argument("--dry-run", action='store_true', default=False,
                            help="do not create the resources on kubernetes")
        parser.add_argument("--namespace",
                            help="kubernetes namespace", default=None)
        parser.add_argument("--api-proxy",
                            help="kubectl proxy url", nargs="?", const="http://localhost:8001")
        parser.add_argument("-x", "--variables",
                            help="variables", default={}, action=kpm.command.LoadVariables)
        parser.add_argument("--shards",
                            help="Shards list/dict/count: eg. --shards=5 ; --shards='[{\"name\": 1, \"name\": 2}]'",
                            default=None)
        parser.add_argument("--force", action='store_true', default=False,
                            help="force upgrade, delete and recreate resources")

        parser.add_argument("--platform", default=None,
                            help='[experimental] target platform to deploy the package: [kubernetes, docker-compose]')

    def kub(self):
        if self._kub is None:
            self._kub = kpm.formats.kub_factory(self.format,
                                                self.package,
                                                convert_to=self.target,
                                                endpoint=self.registry_host,
                                                variables=self.variables,
                                                namespace=self.namespace,
                                                shards=self.shards,
                                                version=self.version)
        return self._kub

    def _call(self):
        self.status = self.kub().deploy(dest=self.tmpdir,
                                        force=self.force,
                                        dry=self.dry_run,
                                        proxy=self.api_proxy,
                                        fmt=self.output)

    def _render_dict(self):
        return self.status

    def _render_console(self):
        """ Handled by deploy """
        if self.kub().target == "docker-compose":
            print self.status
