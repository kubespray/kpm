from kpm.commands.command_base import CommandBase
from kpm.auth import KpmAuth


class LogoutCmd(CommandBase):
    name = 'logout'
    help_message = "logout"

    def __init__(self, options):
        super(LogoutCmd, self).__init__(options)
        self.status = None

    @classmethod
    def _add_arguments(self, parser):
        pass

    def _call(self):
        KpmAuth().delete_token()
        self.status = "Logout complete"

    def _render_dict(self):
        return {"status": self.status}

    def _render_console(self):
        print " >>> %s" % self.status
