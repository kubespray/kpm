#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

import socket
import datetime
import traceback as tb
import json


def _default_json_default(obj):
    """
    Coerce everything to strings.
    All objects representing time get output as ISO8601.
    """
    if (isinstance(obj, datetime.datetime) or
       isinstance(obj, datetime.date) or
       isinstance(obj, datetime.time)):
        return obj.isoformat()
    else:
        return str(obj)


class JsonFormatter(logging.Formatter):
    """
    A custom formatter to prepare logs to be in json format
    """

    def __init__(self,
                 fmt=None,
                 datefmt=None,
                 json_cls=None,
                 json_default=_default_json_default):
        """
        :param source_host: override source host name
        :param extra: provide extra fields always present in logs
        :param json_cls: JSON encoder to forward to json.dumps
        :param json_default: Default JSON representation for unknown types,
                             by default coerce everything to a string
        """

        if fmt is not None:
            self._fmt = json.loads(fmt)
        else:
            self._fmt = {}
        self.json_default = json_default
        self.json_cls = json_cls
        if 'extra' not in self._fmt:
            self.defaults = {}
        else:
            self.defaults = self._fmt['extra']
        if 'source_host' in self._fmt:
            self.source_host = self._fmt['source_host']
        else:
            try:
                self.source_host = socket.gethostname()
            except:
                self.source_host = ""

    def format(self, record):
        """
        Format a log record to JSON, if the message is a dict
        assume an empty message and use the dict as additional
        fields.
        """

        fields = record.__dict__.copy()
        if isinstance(record.msg, dict):
            fields.pop('msg')
            msg = ""
        else:
            msg = record.getMessage()

        if 'msg' in fields:
            fields.pop('msg')

        if 'exc_info' in fields:
            if fields['exc_info']:
                formatted = tb.format_exception(*fields['exc_info'])
                fields['exception'] = formatted
            fields.pop('exc_info')
        fields.pop('exc_text')
        fields.pop('args')
        fields.pop('created')
        fields.pop('filename')
        fields.pop('levelno')
        fields.pop('module')
        fields.pop('msecs')
        fields.pop('pathname')
        fields.pop('process')
        fields.pop('processName')
        fields.pop('relativeCreated')
        fields.pop('thread')
        fields.pop('threadName')
        if 'logstash' in fields:
            fields.pop('logstash')
        base_log = {'message': msg,
                    '@timestamp': datetime.datetime.utcnow(),
                    'source_host': self.source_host}
        base_log.update(fields)

        logr = self.defaults.copy()
        logr.update(base_log)

        return json.dumps(logr, default=self.json_default, cls=self.json_cls)


def init_logging(logger, loglevel="DEBUG",
                 fmt='[%(asctime)s: %(levelname)s][%(name)s:%(lineno)d] %(message)s'):

    logger.setLevel(logging.getLevelName(loglevel))
    json_fmt = JsonFormatter()
    f_formatter = json_fmt

    jsonh = logging.StreamHandler()
    jsonh.setLevel(logging.getLevelName(loglevel))
    jsonh.setFormatter(f_formatter)
    logger.addHandler(jsonh)
