import json
import kpm.command
from kpm.render_jsonnet import RenderJsonnet
from kpm.commands.command_base import CommandBase


class JsonnetCmd(CommandBase):
    name = 'jsonnet'
    help_message = "Resolve a jsonnet file with the kpmstd available"

    def __init__(self, options):
        super(JsonnetCmd, self).__init__(options)
        self.shards = options.shards
        self.namespace = options.namespace
        self.variables = options.variables
        self.filepath = options.filepath[0]
        self.result = None

    @classmethod
    def _add_arguments(cls, parser):
        parser.add_argument("--namespace",
                            help="kubernetes namespace", default='default')
        parser.add_argument("-x", "--variables",
                            help="variables", default={}, action=kpm.command.LoadVariables)
        # @TODO shards
        parser.add_argument("--shards",
                            help="Shards list/dict/count: eg. --shards=5 ; --shards='[{\"name\": 1, \"name\": 2}]'",
                            default=None)
        parser.add_argument('filepath', nargs=1, help="Fetch package from the registry")

    def _call(self):
        r = RenderJsonnet()
        namespace = self.namespace
        self.variables['namespace'] = namespace
        tla_codes = {"variables": self.variables}
        p = open(self.filepath).read()
        self.result = r.render_jsonnet(p, tla_codes={"params": json.dumps(tla_codes)})

    def _render_dict(self):
        return self.result

    def _render_console(self):
        self._render_json()
