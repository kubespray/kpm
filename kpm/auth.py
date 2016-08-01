import os.path
from kpm.utils import mkdir_p


class KpmAuth(object):
    def __init__(self):
        path = ".kpm/auth_token"
        home = os.path.expanduser("~")
        mkdir_p(os.path.join(home, ".kpm"))
        self.tokenfile = os.path.join(home, path)
        self._token = None

    @property
    def token(self):
        if self._token is None:
            if os.path.exists(self.tokenfile):
                f = open(self.tokenfile, 'r')
                self._token = f.read()
                f.close()
            else:
                return None
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
        f = open(self.tokenfile, 'w')
        f.write(value)
        f.close()

    def delete_token(self):
        prev_token = self.token
        if os.path.exists(self.tokenfile):
            os.remove(self.tokenfile)
        self._token = None
        return prev_token
