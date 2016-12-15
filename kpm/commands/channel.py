import argparse
import kpm.registry
from kpm.commands.command_base import CommandBase


class ChannelCmd(CommandBase):
    name = 'channel'
    help_message = "Manage package channels"

    def __init__(self, options):
        super(ChannelCmd, self).__init__(options)
        self.package = options.package[0]
        self.registry_host = options.registry_host
        self.delete = options.delete
        self.channel = options.name
        self.remove = options.remove_release
        self.add = options.add_release
        self.list = options.list
        self.status = None
        self.channels = {}

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_packagename_option(parser)

        parser.add_argument("-n", "--name", default=None,
                            help="channel name")
        parser.add_argument("--add-release", default=None,
                            help="Add a release to the channel")
        parser.add_argument("--list", default=False, action='store_true',
                            help="Create the channel")
        parser.add_argument("--delete", default=False, action='store_true',
                            help="delete the channel")
        parser.add_argument("--remove-release", default=None,
                            help="Remove a release from the channel")

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        package = self.package
        name = self.channel
        if name is None and not self.list:
            raise argparse.ArgumentError(self.channel, "missing channel name")
        if self.delete is True:
            self.channels = r.delete_channel(package, name)
            self.status = "Channel '%s' on '%s' deleted" % (name, package)
        elif self.list:
            self.channels = r.show_channels(package, name)
            # @TODO
            self.status = self.channels
        else:
            if self.add is not None:
                self.channels = r.create_channel_release(package, name, self.add)
                self.status = ">>> Release '%s' added on '%s'" % (self.add, name)
            if self.remove is not None:
                self.channels = r.delete_channel_release(package, name, self.remove)
                self.status = ">>> Release '%s' removed from '%s'" % (self.remove, name)

    def _render_dict(self):
        return self.channels

    def _render_console(self):
        print " >>> %s" % self.status
