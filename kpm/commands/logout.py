import json
from kpm.commands.command_base import CommandBase
from kpm.auth import KpmAuth


class LogoutCmd(CommandBase):
    name = 'logout'
    help_message = "logout"

    def __init__(self, options):
        self.output = options.output
        self.status = None
        super(LogoutCmd, self).__init__(options)

    @classmethod
    def _add_arguments(self, parser):
        pass

    def _call(self):
        KpmAuth().delete_token()
        self.status = "Logout complete"

    def _render_json(self):
        print json.dumps({"status": self.status})

    def _render_console(self):
        print " >>> %s" % self.status
