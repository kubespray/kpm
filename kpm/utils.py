import errno
import os
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
