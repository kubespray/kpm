import json
import yaml
import kpm.command
import kpm.registry


class CommandBase(object):
    name = 'command-base'
    help_message = 'describe the command'

    def __init__(self, args_options):
        self.args_options = args_options
        self.output = args_options.output

    def render(self):
        if self.output == 'none':
            return
        elif self.output == 'json':
            self._render_json()
        elif self.output == 'yaml':
            self._render_yaml()
        else:
            self._render_console()

    @classmethod
    def call(cls, options):
        cls(options)()

    def __call__(self):
        self._call()
        self.render()

    @classmethod
    def add_parser(cls, subparsers):
        parser = subparsers.add_parser(cls.name, help=cls.help_message)
        cls._add_output_option(parser)
        cls._add_arguments(parser)
        parser.set_defaults(func=cls.call)

    def _render_json(self):
        print json.dumps(self._render_dict(), indent=2, separators=(',', ': '))

    def _render_dict(self):
        raise NotImplementedError

    def _render_console(self):
        raise NotImplementedError

    def _render_yaml(self):
        print yaml.safe_dump(self._render_dict())

    def _call(self):
        raise NotImplementedError

    @classmethod
    def _add_arguments(cls, parser):
        raise NotImplementedError

    @classmethod
    def _add_registryhost_option(cls, parser):
        parser.add_argument("-H", "--registry-host", default=kpm.registry.DEFAULT_REGISTRY,
                            help='registry API url')

    @classmethod
    def _add_output_option(cls, parser):
        parser.add_argument("--output", default="text",  choices=['text',
                                                                  'none',
                                                                  'json',
                                                                  'yaml'],
                            help="output format")

    @classmethod
    def _add_mediatype_option(cls, parser):
        parser.add_argument("-t", "--media-type", default='kpm',
                            help='package format: [kpm, kpm-compose, helm]')

    @classmethod
    def _add_packagename_option(cls, parser):
        parser.add_argument('package', nargs=1, action=kpm.command.PackageName, help="package-name")

    @classmethod
    def _add_packageversion_option(cls, parser):
        parser.add_argument("-v", "--version",
                            help="package VERSION", default='default')
