import json
import logging
import subprocess


logger = logging.getLogger(__name__)


class Kompose(object):
    def __init__(self, kubcompose):
        self.kubcompose = kubcompose

    def convert(self):
        return json.loads(self._call([]))

    def _call(self, cmd, dry=False):
        f = self.kubcompose.create_temp_compose_file()
        command = ['kompose', "--file", f.name, "convert", "--stdout"] + cmd
        try:
            r = subprocess.check_output(command)
        finally:
            f.close()
        return r
