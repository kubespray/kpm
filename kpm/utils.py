from __future__ import absolute_import
import re
import importlib
import sys
import errno
import os
import collections
from cnrclient.client import ishosted
from termcolor import colored


def check_package_name(name, force_check=False):
    if not force_check and not ishosted(name):
        if re.match(r"^[a-z0-9_-]+/[a-z0-9_-]+$", name) is None:
            if re.match(r"^.+?/.+?$", name) is not None:
                raise ValueError("Package names are restricted to [a-z0-9_-] ")
            else:
                raise ValueError("Package '%s' does not match format 'namespace/name'" % (name))


def package_filename(name, version, media_type):
    return "%s_%s_%s" % (name.replace("/", "_"), version, media_type)


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


def custom_import(name):
    import importlib
    module, klass_name = name.split(':')
    mod = importlib.import_module(module)
    klass = getattr(mod, klass_name)
    return klass


# from celery/kombu https://github.com/celery/celery (BSD license)
def symbol_by_name(name, aliases={}, imp=None, package=None,
                   sep='.', default=None, **kwargs):
    """Get symbol by qualified name.

    The name should be the full dot-separated path to the class::

        modulename.ClassName

    Example::

        celery.concurrency.processes.TaskPool
                                    ^- class name

    or using ':' to separate module and symbol::

        celery.concurrency.processes:TaskPool

    If `aliases` is provided, a dict containing short name/long name
    mappings, the name is looked up in the aliases first.

    Examples:

        >>> symbol_by_name('celery.concurrency.processes.TaskPool')
        <class 'celery.concurrency.processes.TaskPool'>

        >>> symbol_by_name('default', {
        ...     'default': 'celery.concurrency.processes.TaskPool'})
        <class 'celery.concurrency.processes.TaskPool'>

        # Does not try to look up non-string names.
        >>> from celery.concurrency.processes import TaskPool
        >>> symbol_by_name(TaskPool) is TaskPool
        True

    """
    def _reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    if imp is None:
        imp = importlib.import_module

    if not isinstance(name, basestring):
        return name  # already a class

    name = aliases.get(name) or name
    sep = ':' if ':' in name else sep
    module_name, _, cls_name = name.rpartition(sep)
    if not module_name:
        cls_name, module_name = None, package if package else cls_name
    try:
        try:
            module = imp(module_name, package=package, **kwargs)
        except ValueError as exc:
            _reraise(ValueError,
                     ValueError("Couldn't import {0!r}: {1}".format(name, exc)),
                     sys.exc_info()[2])
        return getattr(module, cls_name) if cls_name else module
    except (ImportError, AttributeError):
        if default is None:
            raise
    return default
