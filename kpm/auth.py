import yaml
import os.path
from kpm.utils import mkdir_p


class KpmAuth(object):
    """ Store Auth object """

    def __init__(self, conf_directory=".kpm"):
        self.conf_directory = conf_directory
        home = os.path.expanduser("~")
        old_path = "%s/%s/auth_token" % (home, conf_directory)
        path = "%s/%s/auths.yaml" % (home, conf_directory)
        mkdir_p(os.path.join(home, conf_directory))
        self.tokenfile = os.path.join(home, path)
        self._tokens = None
        self._retro_compat(old_path)

    def _retro_compat(self, old):
        oldtoken = self._old_token(old)
        if oldtoken:
            if self.tokens is None or '*' not in self.tokens['auths']:
                self.add_token('*', oldtoken)
            os.remove(old)

    def _old_token(self, path):
        if os.path.exists(path):
            with open(path, 'r') as tokenfile:
                return tokenfile.read()
        else:
            return None

    @property
    def tokens(self):
        if self._tokens is None:
            if os.path.exists(self.tokenfile):
                with open(self.tokenfile, 'r') as tokenfile:
                    self._tokens = yaml.load(tokenfile.read())
            else:
                return None
        return self._tokens

    def token(self, host=None):
        if not self.tokens:
            return None
        if host is None or host not in self.tokens['auths']:
            host = '*'
        return self.tokens['auths'].get(host, None)

    def add_token(self, host, value):
        auths = self.tokens
        if auths is None:
            auths = {'auths': {}}
        auths['auths'][host] = value
        self._write_tokens(auths)

    def _write_tokens(self, tokens):
        with open(self.tokenfile, 'w') as tokenfile:
            tokenfile.write(yaml.safe_dump(tokens, indent=2, default_style='"', default_flow_style=False))

    def delete_token(self, host):
        auths = self.tokens
        if not auths or host not in auths['auths']:
            return None
        prev = auths['auths'].pop(host)
        self._write_tokens(auths)
        return prev
