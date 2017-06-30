import re
import os
import copy
import argparse
import json

import yaml

from appr.commands.command_base import CommandBase as ApprCommandBase

from kpm.registry import Registry
from kpm.render_jsonnet import RenderJsonnet


class CommandBase(ApprCommandBase):
    RegistryClient = Registry
    default_media_type = 'kpm'


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
