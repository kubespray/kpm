import errno
import os
import collections
from termcolor import colored


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
