import tempfile
import time
import logging
import yaml
import json
import subprocess
import requests
from urlparse import urlparse

__all__ = ['DockerCompose']


logger = logging.getLogger(__name__)


class DockerCompose(object):
    def __init__(self, compose_obj):
        self.obj = compose_obj
        self.compose = yaml.dump(self.obj)
        self.result = None

    def _create_compose_file(self):
        f = tempfile.NamedTemporaryFile()
        f.write(self.compose)
        f.flush()
        return f

    def create(self, force=False):
        f = self._create_compose_file()
        cmd = ['--file', f.name,  'up', "-d"]
        if force:
            cmd.append("--force-recreate")
        r = self._call(cmd)
        f.close()
        return r

    def get(self):
        f = self._create_compose_file()
        cmd = ['--file', f.name, 'ps']
        r = self._call(cmd)
        f.close()
        return r

    def delete(self):
        f = self._create_compose_file()
        cmd = ['--file', f.name, "down"]
        r = self._call(cmd)
        f.close()
        return r

    def exists(self):
        r = self.get()
        if r is None:
            return False
        else:
            return True

    def _call(self, cmd, dry=False):
        command = ['docker-compose'] + cmd
        return subprocess.check_output(command, stderr=subprocess.STDOUT)
