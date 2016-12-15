import argparse

from kpm.commands.command_base import CommandBase
import kpm.new


class NewCmd(CommandBase):
    name = 'new'
    help_message = "initiate a new package"

    def __init__(self, options):
        super(NewCmd, self).__init__(options)
        self.package = options.package[0]
        self.with_comments = options.with_comments
        self.directory = options.directory
        self.path = None

    @classmethod
    def _add_arguments(self, parser):
        parser.add_argument('package', nargs=1, help="package-name")
        parser.add_argument("--directory",  nargs="?", default=".",
                            help="destionation directory")
        parser.add_argument("--with-comments", action='store_true', default=False,
                            help="Add 'help' comments to manifest")

    def _call(self):
        try:
            self.path = kpm.new.new_package(self.package, self.directory, self.with_comments)
        except ValueError as e:
            argparse.ArgumentTypeError(e.message)

    def _render_dict(self):
        return {"new": self.package,
                "path": self.path}

    def _render_console(self):
        print "New package created in %s" % self.path
