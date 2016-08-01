import errno
import os
import collections
import json
import re
from termcolor import colored


def parse_cmdline_variables(l):
    r = {}
    for var in l:
        try:
            r.update(json.loads(var))
        except ValueError:
            for v in var.split(","):
                sp = re.match("(.+?)=(.+)", v)
                if sp is None:
                    raise ValueError("Malformed variable: %s" % v)
                key, value = sp.group(1), sp.group(2)
                r[key] = value
    return r


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def colorize(status):
    msg = {'ok': 'green',
           'created': 'yellow',
           'updated': 'yellow',
           'absent': 'green',
           'deleted': 'red',
           'protected': 'blue'}
    return colored(status, msg[status])


def convert_utf8(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_utf8, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_utf8, data))
    else:
        return data
