#!/usr/bin/env python
import argparse

from appr.commands.cli import all_commands as appr_commands
from appr.commands.cli import get_parser

from kpm.commands.command_base import CommandBase
from kpm.commands.push import PushCmd
from kpm.commands.new import NewCmd
from kpm.commands.deploy import DeployCmd
from kpm.commands.version import VersionCmd
from kpm.commands.remove import RemoveCmd
from kpm.commands.kexec import ExecCmd
from kpm.commands.generate import GenerateCmd
from kpm.commands.jsonnet import JsonnetCmd


def all_commands():
    base_cmd = appr_commands()
    for cmd in base_cmd.values():
        cmd.__bases__ = (CommandBase,)

    base_cmd.update({
        VersionCmd.name: VersionCmd,
        PushCmd.name: PushCmd,
        NewCmd.name: NewCmd,
        DeployCmd.name: DeployCmd,
        RemoveCmd.name: RemoveCmd,
        ExecCmd.name: ExecCmd,
        JsonnetCmd.name: JsonnetCmd,
        GenerateCmd.name: GenerateCmd,
    })
    return base_cmd


def cli():
    try:
        parser = get_parser(all_commands())
        args = parser.parse_args()
        args.func(args)
    except (argparse.ArgumentTypeError, argparse.ArgumentError) as exc:
        parser.error(exc.message)
