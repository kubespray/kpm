from kpm.commands.command_base import CommandBase
from kpm.auth import KpmAuth


class LogoutCmd(CommandBase):
    name = 'logout'
    help_message = "logout"

    def __init__(self, options):
        super(LogoutCmd, self).__init__(options)
        self.status = None
        self.registry_host = options.registry_host

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)

    def _call(self):
        KpmAuth().delete_token(self.registry_host)
        self.status = "Logout complete"
        if self.registry_host != '*':
            self.status += " from %s" % self.registry_host

    def _render_dict(self):
        return {"status": self.status, 'host': self.registry_host}

    def _render_console(self):
        print " >>> %s" % self.status
