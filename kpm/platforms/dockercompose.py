import logging
import subprocess


__all__ = ['DockerCompose']


logger = logging.getLogger(__name__)


class DockerCompose(object):
    def __init__(self, kubcompose):
        self.kubcompose = kubcompose
        self.result = None

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
        f = self.kubcompose.create_temp_compose_file()
        command = ['docker-compose', "--file", f.name] + cmd
        try:
            r = subprocess.check_output(command, stderr=subprocess.STDOUT)
        finally:
            f.close()
        return r
