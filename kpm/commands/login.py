import json
import getpass
import argparse
import kpm.registry
from kpm.commands.command_base import CommandBase


class LoginCmd(CommandBase):
    name = 'login'
    help_message = "login"

    def __init__(self, options):
        self.output = options.output
        self.registry_host = options.registry_host
        self.signup = options.signup
        self.password = options.password
        self.email = options.email
        self.user = options.user
        self.status = None
        super(LoginCmd, self).__init__(options)

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)

        parser.add_argument("-s", "--signup", action='store_true', default=False,
                            help="Create a new account and login")
        parser.add_argument("-u", "--user", nargs="?", default=None,
                            help="username")
        parser.add_argument("-p", "--password", nargs="?", default=None,
                            help="password")
        parser.add_argument("-e", "--email", nargs="?", default=None,
                            help="email for signup")

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        if self.user is not None:
            user = self.user
        else:
            user = raw_input("Username: ")
        if self.password is not None:
            p1 = self.password
        else:
            p1 = getpass.getpass()

        if self.signup:
            if self.password is not None:
                p2 = p1
            else:
                p2 = getpass.getpass('Password confirmation: ')
            if self.email is not None:
                email = self.email
            else:
                email = raw_input("Email: ")
            if p1 != p2:
                raise argparse.ArgumentError("Error: password mismatch")
            r.signup(user, p1, p2, email)
            self.status = "Registration complete"
        else:
            r.login(user, p1)
            self.status = "Login succeeded"

    def _render_json(self):
        print json.dumps({"user": self.user, "status": self.status})

    def _render_console(self):
        print " >>> %s" % self.status
