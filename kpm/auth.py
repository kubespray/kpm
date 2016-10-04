import os.path
from kpm.utils import mkdir_p


class KpmAuth(object):
    """ Store Auth object """

    def __init__(self, conf_directory=".kpm"):
        self.conf_directory = conf_directory
        path = "%s/auth_token" % conf_directory
        home = os.path.expanduser("~")
        mkdir_p(os.path.join(home, conf_directory))
        self.tokenfile = os.path.join(home, path)
        self._token = None

    @property
    def token(self):
        if self._token is None:
            if os.path.exists(self.tokenfile):
                with open(self.tokenfile, 'r') as tokenfile:
                    self._token = tokenfile.read()
            else:
                return None
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
        with open(self.tokenfile, 'w') as tokenfile:
            tokenfile.write(value)

    def delete_token(self):
        prev_token = self.token
        if os.path.exists(self.tokenfile):
            os.remove(self.tokenfile)
        self._token = None
        return prev_token
