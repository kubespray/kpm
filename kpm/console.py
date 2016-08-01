import json
import subprocess
import random
import logging


logger = logging.getLogger(__name__)


class KubernetesExec(object):
    def __init__(self, rcname, cmd='sh', namespace="default", container=None, kind="rc"):
        self.rcname = rcname
        self.namespace = namespace
        self.command = cmd
        self.kind = kind
        self.container = container

    def call(self, tty=True):
        rc = self._getrc()
        selector = self._getselector(rc)
        logger.info("selector: %s", selector)
        pods = self._getpods(selector)
        podname = random.choice(pods)['metadata']['name']
        cmd = ['exec', '--namespace', self.namespace, podname]
        if tty:
            cmd.append("-ti")
        if self.container is not None:
            cmd += ['-c', self.container]
        command = ['kubectl'] + cmd + ["--"] + self.command.split(" ")
        return subprocess.call(command)

    def _getpods(self, selector):
        cmd = ['get', "pods", "-l", selector, '-o', 'json']
        podslist = json.loads(self._call(cmd))
        pods = podslist['items']
        return pods

    def _getselector(self, rc):
        s = None
        items = rc['spec']['selector']
        if 'matchLabels' in items:
            items = items['matchLabels']
        for k, v in items.iteritems():
            if s is None:
                s = "%s=%s" % (k, v)
            else:
                s += ",%s=%s" % (k, v)
        return s

    def _getrc(self):
        cmd = ['get', self.kind, self.rcname, '-o', 'json']
        return (json.loads(self._call(cmd)))

    def _call(self, cmd, dry=False):
        command = ['kubectl'] + cmd + ["--namespace", self.namespace]
        return subprocess.check_output(command, stderr=subprocess.STDOUT)
