#!/usr/bin/env python
import argparse
import os
import yaml
import json
import copy
import re
from kpm.utils import parse_package_name
from kpm.render_jsonnet import RenderJsonnet
from kpm.commands import all_commands


class PackageName(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        try:
            name = value[0]
            package_parts = parse_package_name(name)
            if package_parts['host'] is not None:
                setattr(namespace, "registry_host", package_parts['host'])
            if package_parts['version'] is not None:
                setattr(namespace, 'version', package_parts['version'])
            package = package_parts['package']
        except ValueError as e:
            raise parser.error(e.message)
        setattr(namespace, self.dest, package)


class LoadVariables(argparse.Action):

    def _parse_cmd(self, var):
        r = {}
        try:
            return json.loads(var)
        except:
            for v in var.split(","):
                sp = re.match("(.+?)=(.+)", v)
                if sp is None:
                    raise ValueError("Malformed variable: %s" % v)
                key, value = sp.group(1), sp.group(2)
                r[key] = value
        return r

    def _load_from_file(self, filename, ext):
        with open(filename, 'r') as f:
            if ext in ['.yml', '.yaml']:
                return yaml.load(f.read())
            elif ext == '.json':
                return json.loads(f.read())
            elif ext in [".jsonnet", "libjsonnet"]:
                r = RenderJsonnet()
                return r.render_jsonnet(f.read())
            else:
                raise ValueError("File extension is not in [yaml, json, jsonnet]: %s" % filename)

    def load_variables(self, var):
        _, ext = os.path.splitext(var)
        if ext not in ['.yaml', '.yml', '.json', '.jsonnet']:
            return self._parse_cmd(var)
        else:
            return self._load_from_file(var, ext)

    def __call__(self, parser, namespace, values, option_string=None):
        items = copy.copy(argparse._ensure_value(namespace, self.dest, {}))
        try:
            items.update(self.load_variables(values))
        except ValueError as e:
            raise parser.error(option_string + ": " + e.message)
        setattr(namespace, self.dest, items)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='command help')
    for _, commandClass in all_commands.iteritems():
        commandClass.add_parser(subparsers)
    return parser


def cli():
    try:
        parser = get_parser()
        args = parser.parse_args()
        args.func(args)
    except (argparse.ArgumentTypeError, argparse.ArgumentError) as e:
        parser.error(e.message)
