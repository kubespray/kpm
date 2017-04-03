import subprocess

__all__ = ['Helm']


class Helm(object):

    def __init__(self, chart):
        self.chart = chart
        self.result = None

    def install(self):
        release = self.chart.build()
        cmd = ['install', release.name]
        return self._call(cmd)

    def get(self):
        return self._call(['ps'])

    def delete(self):
        return self._call(["down"])

    def exists(self):
        return (self.get() is None)

    def _call(self, cmd, dry=False):
        command = ['helm'] + cmd
        return subprocess.check_output(command, stderr=subprocess.STDOUT)
