import tempfile
import logging
import yaml
import subprocess


__all__ = ['DockerCompose']


logger = logging.getLogger(__name__)


class DockerCompose(object):
    def __init__(self, compose_obj):
        self.obj = compose_obj
        self.compose = yaml.safe_dump(self.obj)
        self.result = None

    def _create_compose_file(self):
        f = tempfile.NamedTemporaryFile()
        f.write(self.compose)
        f.flush()
        return f

    def create(self, force=False):
        cmd = ['up', "-d"]
        if force:
            cmd.append("--force-recreate")
        return self._call(cmd)

    def get(self):
        return self._call(['ps'])

    def delete(self):
        return self._call(["down"])

    def exists(self):
        return (self.get() is None)

    def _call(self, cmd, dry=False):
        f = self._create_compose_file()
        command = ['docker-compose', "--file", f.name] + cmd
        try:
            r = subprocess.check_output(command, stderr=subprocess.STDOUT)
        finally:
            f.close()
        return r
