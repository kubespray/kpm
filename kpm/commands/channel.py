import kpm.registry
from kpm.commands.command_base import CommandBase
from kpm.display import print_channels


class ChannelCmd(CommandBase):
    name = 'channel'
    help_message = "Manage package channels"

    def __init__(self, options):
        super(ChannelCmd, self).__init__(options)
        self.package = options.package
        self.registry_host = options.registry_host
        self.delete = options.delete
        self.channel = options.name
        self.remove = options.remove_release
        self.add = options.set_release
        self.version = options.version
        self.status = None
        self.channels = {}

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_packagename_option(parser)
        cls._add_packageversion_option(parser)

        parser.add_argument("-n", "--name", default=None,
                            help="channel name")
        parser.add_argument("--set-release", default=False, action='store_true',
                            help="Add release to the channel")
        parser.add_argument("--delete", default=False, action='store_true',
                            help="delete the channel")
        parser.add_argument("--remove-release", default=False, action='store_true',
                            help="Remove a release from the channel")

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        package = self.package
        name = self.channel
        if self.delete is True:
            self.channels = r.delete_channel(package, name)
            self.status = ">>> Channel '%s' on '%s' deleted" % (name, package)
        elif self.add:
                self.channels = r.create_channel_release(package, name, self.version)
                self.status = ">>> Release '%s' added on '%s'" % (self.version, name)
        elif self.remove:
                self.channels = r.delete_channel_release(package, name, self.version)
                self.status = ">>> Release '%s' removed from '%s'" % (self.version, name)
        else:
            self.channels = r.show_channels(package, name)
            if name is not None:
                self.channels = [self.channels]
            self.status = print_channels(self.channels)

    def _render_dict(self):
        return self.channels

    def _render_console(self):
        print "%s" % self.status
