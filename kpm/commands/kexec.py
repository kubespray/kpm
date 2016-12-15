from kpm.console import KubernetesExec
from kpm.commands.command_base import CommandBase


class ExecCmd(CommandBase):
    name = 'exec'
    help_message = "exec a command in pod from the RC or RS name.\
    It executes the command on the first matching pod'"

    def __init__(self, options):
        super(ExecCmd, self).__init__(options)
        self.kind = options.kind
        self.container = options.container
        self.namespace = options.namespace
        self.resource = options.name
        self.cmd = options.cmd
        self.result = None

    @classmethod
    def _add_arguments(cls, parser):
        parser.add_argument('cmd', nargs='+', help="command to execute")
        parser.add_argument("--namespace",
                            help="kubernetes namespace", default='default')

        parser.add_argument('-k', '--kind', choices=['deployment', 'rs', 'rc'],
                            help="deployment, rc or rs", default='rc')
        parser.add_argument('-n', '--name', help="resource name", default='rs')
        parser.add_argument('-c', '--container', nargs='?', help="container name", default=None)

    def _call(self):
        c = KubernetesExec(self.resource,
                           cmd=" ".join(self.cmd),
                           namespace=self.namespace,
                           container=self.container,
                           kind=self.kind)
        self.result = c.call()

    def _render_dict(self):
        return {'stdout': self.result}

    def _render_console(self):
        print self.result
